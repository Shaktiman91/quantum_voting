"""
Quantum Voting -- Voter (client)   [scaffolding]

Mirror of the homework client.py. Each voter runs as a classical client that
connects to the Commission, receives a GHZ share, takes part in verification,
encodes its vote, and broadcasts a single measurement bit. The vote value never
leaves this process. The handler body is a stub.

Usage: python voter.py <VoterName> <vote 0|1>
"""

import sys
from asyncio import StreamReader, StreamWriter
from pathlib import Path

from netqasm.runtime.settings import set_simulator
set_simulator("simulaqron")

from netqasm.sdk.external import NetQASMConnection  # noqa: E402
from netqasm.sdk import Qubit, EPRSocket            # noqa: E402

from simulaqron.general.host_config import SocketsConfig
from simulaqron.sdk.protocol import SimulaQronClassicalClient
from simulaqron.settings import network_config, simulaqron_settings
from simulaqron.settings.network_config import NodeConfigType

from utils import MAX_QUBITS


async def run_voter(reader: StreamReader, writer: StreamWriter,
                    name: str, vote: int) -> None:
    print(f"Voter {name}: connected to Commission (vote stays local).", flush=True)

    epr_socket = EPRSocket("Commission")
    conn = NetQASMConnection(name, epr_sockets=[epr_socket], max_qubits=MAX_QUBITS)
    try:
        # Phase 1: initialize the local qubit.
        # Phase 2: receive the teleported GHZ share.
        # Phase 3: take part in a verification round.
        # Phase 4: encode the vote, measure, broadcast the bit.
        raise NotImplementedError
    finally:
        conn.close()


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "Voter1"
    vote = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    _here = Path(__file__).parent
    simulaqron_settings.read_from_file(_here / "simulaqron_settings.json")
    network_config.read_from_file(_here / "simulaqron_network.json")
    sockets_config = SocketsConfig(network_config, "default", NodeConfigType.APP)

    # TODO: confirm against the course helper how a client declares its own node
    #       name (Voter1/2/3) so each voter process binds to the right app socket.
    client = SimulaQronClassicalClient(sockets_config)
    print(f"Voter {name}: connecting to Commission (vote={vote})...", flush=True)
    client.run_client("Commission", run_voter, name, vote)
