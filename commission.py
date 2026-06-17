"""
commission.py -- Election Commission server (Referee role).

PROTOTYPE NOTICE
This is a research demo of a quantum-inspired voting workflow.
It does not provide real-world ballot secrecy, coercion resistance,
or cryptographic authentication. It is an architectural demonstration
using SimulaQron for quantum channel simulation.

Directly mirrors the referee.py pattern from Quantum_week8/step4_quantum_fingerprinting.

FIX: NetQASMConnection is now used as a context manager (`with` block) so that
the connection is properly opened and all buffered instructions (including EPR
create_keep) are flushed automatically on exit. Without this the EPR handshake
never completes and the process hangs after START_ROUND.
"""

import asyncio
import uuid
from asyncio import StreamReader, StreamWriter
from pathlib import Path

from netqasm.runtime.settings import set_simulator
set_simulator("simulaqron")

from netqasm.sdk.external import NetQASMConnection  # noqa: E402
from netqasm.sdk import EPRSocket                   # noqa: E402

from simulaqron.general.host_config import SocketsConfig
from simulaqron.sdk.protocol import SimulaQronClassicalServer
from simulaqron.settings import network_config, simulaqron_settings
from simulaqron.settings.network_config import NodeConfigType

from models import CommissionContext
from quantum_core import apply_ballot_corrections, decode_ballot
from tally import run_tally, find_winner, generate_audit_report, print_audit
from utils import VOTER_NAMES, MAX_QUBITS, BALLOT_QUBITS


def _parse_corrections(raw: str) -> list:
    """Parse 'm1,m2,m1,m2,...' correction string into list of (int,int) pairs."""
    bits = [int(x) for x in raw.split(",") if x != ""]
    if len(bits) != BALLOT_QUBITS * 2:
        raise ValueError(f"Expected {BALLOT_QUBITS * 2} correction bits, got {len(bits)}")
    return [(bits[i], bits[i + 1]) for i in range(0, len(bits), 2)]


def make_handler(ctx: CommissionContext):
    """Return the per-connection async handler, closing over shared CommissionContext."""

    async def run_commission(reader: StreamReader, writer: StreamWriter) -> None:
        voter_id = None
        try:
            # ---- HELLO ----
            line = await reader.readline()
            if not line:
                return
            msg = line.decode().strip()
            if not msg.startswith("HELLO:"):
                writer.write(b"REJECTED:unknown:bad hello\n")
                await writer.drain()
                return

            voter_id = msg.split(":", 1)[1]
            if voter_id not in ctx.expected_voters:
                writer.write(f"REJECTED:{voter_id}:unknown voter\n".encode())
                await writer.drain()
                return
            if voter_id in ctx.writers:
                writer.write(f"REJECTED:{voter_id}:duplicate hello\n".encode())
                await writer.drain()
                return

            # ---- REGISTERED ----
            token = str(uuid.uuid4())
            ctx.tokens[voter_id] = token
            ctx.writers[voter_id] = writer
            writer.write(f"REGISTERED:{voter_id}:{token}\n".encode())
            await writer.drain()
            print(f"Commission: {voter_id} registered (token={token[:8]}...)", flush=True)

            if len(ctx.writers) == len(ctx.expected_voters):
                ctx.all_connected.set()
                if ctx.protocol_task is None:
                    ctx.protocol_task = asyncio.create_task(_run_protocol(ctx))

            # ---- Message loop: BALLOT ----
            while True:
                line = await reader.readline()
                if not line:
                    break
                msg = line.decode().strip()

                if msg.startswith("BALLOT:"):
                    parts = msg.split(":", 3)
                    if len(parts) != 4:
                        writer.write(f"REJECTED:{voter_id}:malformed ballot\n".encode())
                        await writer.drain()
                        continue
                    _, incoming_voter, round_str, correction_str = parts
                    if incoming_voter != voter_id:
                        writer.write(f"REJECTED:{voter_id}:identity mismatch\n".encode())
                        await writer.drain()
                        continue
                    if voter_id in ctx.ballots:
                        ctx.ballots[voter_id]["status"] = "duplicate"
                        writer.write(f"REJECTED:{voter_id}:duplicate ballot\n".encode())
                        await writer.drain()
                        print(f"Commission: duplicate ballot rejected from {voter_id}", flush=True)
                        continue
                    try:
                        corrections = _parse_corrections(correction_str)
                        ctx.ballots[voter_id] = {
                            "token": ctx.tokens[voter_id],
                            "corrections": corrections,
                            "status": "pending",
                        }
                        print(f"Commission: ballot received from {voter_id}", flush=True)
                    except Exception as exc:
                        ctx.ballots[voter_id] = {
                            "token": ctx.tokens.get(voter_id, ""),
                            "status": "invalid",
                            "decoded": "INVALID",
                            "error": str(exc),
                        }
                        writer.write(f"REJECTED:{voter_id}:invalid encoding\n".encode())
                        await writer.drain()

                    if len(ctx.ballots) == len(ctx.expected_voters):
                        ctx.all_ballots_in.set()
                else:
                    writer.write(f"REJECTED:{voter_id}:unexpected message\n".encode())
                    await writer.drain()

                if ctx.result_ready.is_set():
                    break

            # ---- RESULT ----
            await ctx.result_ready.wait()
            winner = ctx.result_data.get("winner", "none")
            total = ctx.result_data.get("total_votes", 0)
            writer.write(f"RESULT:{winner}:{total}\n".encode())
            await writer.drain()
            print(f"Commission: sent RESULT to {voter_id}", flush=True)

        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    return run_commission


async def _run_protocol(ctx: CommissionContext) -> None:
    """
    Background task: broadcast START_ROUND, create EPR pairs per voter,
    wait for all ballots, then decode, tally and broadcast result.

    Each voter gets its own NetQASMConnection context so the connection is
    properly opened and flushed (fixing the post-START_ROUND hang).
    Measurement results are collected *inside* the `with` block so they are
    resolved before the connection is closed.
    """
    await ctx.all_connected.wait()
    ctx.current_round = 1
    print("Commission: all voters connected — broadcasting START_ROUND:1", flush=True)

    for writer in ctx.writers.values():
        writer.write(b"START_ROUND:1\n")
        await writer.drain()

    # Allow voters time to open their recv_keep EPR sockets before we create.
    await asyncio.sleep(1.0)

    # --- EPR: create_keep (one connection per voter, context-managed) ---
    # Correction bits are stored in ctx.epr_corrections[voter_id] as plain int lists.
    ctx.epr_corrections = {}  # voter_id -> list[(m1, m2)] resolved ints

    for voter_id in ctx.expected_voters:
        try:
            epr_socket = EPRSocket(voter_id)
            # `with` block opens the connection, submits create_keep, and flushes
            # on exit so measurement futures are resolved before we leave.
            with NetQASMConnection(
                "Commission", epr_sockets=[epr_socket], max_qubits=MAX_QUBITS
            ) as conn:
                remote_qubits = epr_socket.create_keep(number=BALLOT_QUBITS)
                # Store qubits for correction step; conn stays open until `with` exits
                ctx.epr_corrections[voter_id] = remote_qubits  # still Qubit objects here
            print(f"Commission: EPR pairs created for {voter_id}", flush=True)
        except Exception as exc:
            print(f"Commission: EPR error for {voter_id}: {exc}", flush=True)
            ctx.epr_corrections[voter_id] = None

    # --- Wait for all BALLOT messages to arrive ---
    await ctx.all_ballots_in.wait()
    print("Commission: all ballots received — decoding...", flush=True)

    # --- Decode: apply corrections + measure (each in its own connection context) ---
    for voter_id in ctx.expected_voters:
        ballot = ctx.ballots.get(voter_id)
        qubits = ctx.epr_corrections.get(voter_id)
        if ballot is None or qubits is None or ballot.get("status") in ("invalid", "duplicate"):
            continue
        try:
            epr_socket = EPRSocket(voter_id)
            with NetQASMConnection(
                "Commission", epr_sockets=[epr_socket], max_qubits=MAX_QUBITS
            ) as conn:
                apply_ballot_corrections(qubits, ballot["corrections"])
                decoded = decode_ballot(conn, qubits)
            ballot["decoded"] = decoded
            ballot["status"] = "accepted" if decoded != "INVALID" else "invalid"
            print(f"Commission: {voter_id} decoded -> {decoded}", flush=True)
        except Exception as exc:
            ballot["decoded"] = "INVALID"
            ballot["status"] = "invalid"
            ballot["error"] = str(exc)
            print(f"Commission: decode error for {voter_id}: {exc}", flush=True)

    accepted = [b for b in ctx.ballots.values() if b.get("status") == "accepted"]
    tally = run_tally(accepted)
    winner = find_winner(tally)
    report = generate_audit_report(ctx)
    print_audit(report)

    ctx.result_data = {"winner": winner, "total_votes": sum(tally.values()), "tally": tally}
    ctx.result_ready.set()
    ctx.done.set()
    print("Commission: protocol complete.", flush=True)


if __name__ == "__main__":
    here = Path(__file__).parent
    simulaqron_settings.read_from_file(here / "simulaqron_settings.json")
    network_config.read_from_file(here / "simulaqron_network.json")
    sockets_config = SocketsConfig(network_config, "default", NodeConfigType.APP)

    ctx = CommissionContext(expected_voters=list(VOTER_NAMES))
    server = SimulaQronClassicalServer(sockets_config, "Commission")
    server.register_client_handler(make_handler(ctx))
    print("Commission: starting server...", flush=True)
    server.start_serving()
