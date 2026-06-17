"""
voter.py -- Voter client (Alice/Bob role).

PROTOTYPE NOTICE
This is a research demo of a quantum-inspired voting workflow.
It does not provide real-world ballot secrecy, coercion resistance,
or cryptographic authentication.

Directly mirrors the alice.py pattern from Quantum_week8/step4_quantum_fingerprinting.
Voter identity, vote choice, and SimulaQron node name are read from environment
variables, mirroring the ALICE_INPUT_BITS env-var pattern in alice.py.

FIX: NetQASMConnection is now used as a context manager (`with` block) so that
the connection is properly opened, all buffered instructions (recv_keep, encode,
teleport) are flushed, and measurement futures are resolved before the connection
closes. Without this the process would hang after START_ROUND.
"""

import os
from asyncio import StreamReader, StreamWriter
from pathlib import Path

from netqasm.runtime.settings import set_simulator
set_simulator("simulaqron")

from netqasm.sdk.external import NetQASMConnection  # noqa: E402
from netqasm.sdk import EPRSocket                   # noqa: E402

from simulaqron.general.host_config import SocketsConfig
from simulaqron.sdk.protocol import SimulaQronClassicalClient
from simulaqron.settings import network_config, simulaqron_settings
from simulaqron.settings.network_config import NodeConfigType

from quantum_core import encode_ballot, teleport_ballot
from utils import MAX_QUBITS, BALLOT_QUBITS

VOTER_ID    = os.environ.get("VOTER_ID",    "Voter1")
VOTE_CHOICE = os.environ.get("VOTE_CHOICE", "A")
NODE_NAME   = os.environ.get("NODE_NAME",   "Voter1")


async def run_voter(
    reader: StreamReader, writer: StreamWriter, name: str, vote: str
) -> None:
    print(f"{name}: connected to Commission.", flush=True)

    writer.write(f"HELLO:{name}\n".encode())
    await writer.drain()

    while True:
        line = await reader.readline()
        if not line:
            break
        msg = line.decode().strip()

        if msg.startswith("REGISTERED:"):
            parts = msg.split(":", 2)
            token = parts[2] if len(parts) > 2 else ""
            print(f"{name}: registered — token={token[:8]}...", flush=True)

        elif msg.startswith("START_ROUND:"):
            round_index = msg.split(":", 1)[1]
            print(f"{name}: starting round {round_index}, encoding vote={vote}", flush=True)

            try:
                epr_socket = EPRSocket("Commission")
                # FIX: use `with` block so the connection is opened and all
                # quantum instructions (recv_keep, X gates, CNOT, H, measure)
                # are flushed before we try to read correction bit values.
                with NetQASMConnection(
                    name, epr_sockets=[epr_socket], max_qubits=MAX_QUBITS
                ) as conn:
                    # Receive EPR half from Commission
                    epr_qubits = epr_socket.recv_keep(number=BALLOT_QUBITS)

                    # Encode ballot qubit state
                    ballot_qubits = encode_ballot(conn, vote)

                    # Teleport: CNOT + H + measure both qubits
                    # corrections are resolved int pairs AFTER the `with` block flushes
                    corrections = teleport_ballot(ballot_qubits, epr_qubits)

                # corrections are now resolved plain Python ints (flush happened on exit)
                flat = ",".join(str(bit) for pair in corrections for bit in pair)
                writer.write(f"BALLOT:{name}:{round_index}:{flat}\n".encode())
                await writer.drain()
                print(f"{name}: sent BALLOT with corrections={corrections}", flush=True)

            except Exception as exc:
                print(f"{name}: quantum error in round {round_index}: {exc}", flush=True)
                break

        elif msg.startswith("RESULT:"):
            print(f"{name}: received {msg}", flush=True)
            break

        elif msg.startswith("REJECTED:"):
            print(f"{name}: {msg}", flush=True)
            break


def main() -> None:
    here = Path(__file__).parent
    simulaqron_settings.read_from_file(here / "simulaqron_settings.json")
    network_config.read_from_file(here / "simulaqron_network.json")
    sockets_config = SocketsConfig(network_config, "default", NodeConfigType.APP)
    client = SimulaQronClassicalClient(sockets_config)
    print(f"{NODE_NAME}: connecting to Commission (vote={VOTE_CHOICE})...", flush=True)
    client.run_client("Commission", run_voter, NODE_NAME, VOTE_CHOICE)


if __name__ == "__main__":
    main()
