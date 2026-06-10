"""
Quantum Voting -- Election Commission (server)   [scaffolding]

Mirror of the homework bank.py. The commission runs the classical server, acts
as the GHZ source, and orchestrates the four phases across the voters. The
handler body is a stub.
"""

from asyncio import StreamReader, StreamWriter
from pathlib import Path

import numpy as np

from netqasm.runtime.settings import set_simulator
set_simulator("simulaqron")

from netqasm.sdk.external import NetQASMConnection  # noqa: E402
from netqasm.sdk import Qubit, EPRSocket            # noqa: E402

from simulaqron.general.host_config import SocketsConfig
from simulaqron.sdk.protocol import SimulaQronClassicalServer
from simulaqron.settings import network_config, simulaqron_settings
from simulaqron.settings.network_config import NodeConfigType

from utils import VOTER_NAMES, MAX_QUBITS


def make_run_commission(rng: np.random.Generator):
    # Shared state across voter connections goes here (the GHZ qubits, the
    # running tally, how many voters have connected, ...).
    # TODO: decide how the commission coordinates the multiple voter clients
    #       (one handler per voter vs one orchestrator holding all connections).

    async def run_commission(reader: StreamReader, writer: StreamWriter) -> None:
        print("Commission: a voter connected.", flush=True)

        # The remote name is learned per connection (e.g. a HELLO line).
        # TODO: read which voter this is, then EPRSocket(voter_name).
        epr_socket = EPRSocket("Voter1")
        conn = NetQASMConnection(
            "Commission", epr_sockets=[epr_socket], max_qubits=MAX_QUBITS
        )
        try:
            # Phase 2: build the GHZ state and teleport this voter's share.
            # Phase 3: run a verification round with this voter.
            # Phase 4: receive the voter's broadcast bit, add it to the tally.
            raise NotImplementedError
        finally:
            conn.close()

    return run_commission


if __name__ == "__main__":
    import sys
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
    rng = np.random.default_rng(seed)

    _here = Path(__file__).parent
    simulaqron_settings.read_from_file(_here / "simulaqron_settings.json")
    network_config.read_from_file(_here / "simulaqron_network.json")
    sockets_config = SocketsConfig(network_config, "default", NodeConfigType.APP)

    server = SimulaQronClassicalServer(sockets_config, "Commission")
    server.register_client_handler(make_run_commission(rng))
    print("Commission: starting server...", flush=True)
    server.start_serving()
