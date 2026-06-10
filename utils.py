"""
Quantum Voting -- shared constants and quantum primitives.

Same role as the homework utils.py: constants plus the helper functions that
commission.py and voter.py call. Bodies are stubs, grouped by protocol phase.
"""

# --- Election parameters (kickoff: 3 voters, 2 to 3 candidates) ---
VOTER_NAMES = ["Voter1", "Voter2", "Voter3"]
NUM_VOTERS = len(VOTER_NAMES)
CANDIDATES = ["A", "B"]        # TODO: extend to 3 candidates if needed
MAX_QUBITS = 16                # mirrors MAX_NUM_CONN from the homework


# --- Phase 1: initialization ---
def initialize_qubit(conn):
    """Prepare a voter's local qubit. TODO."""
    raise NotImplementedError


# --- Phase 2: GHZ creation and sharing ---
def build_ghz(conn, n):
    """Commission: prepare an n-qubit GHZ state locally. TODO."""
    raise NotImplementedError


def teleport_out(conn, epr_socket, qubit):
    """Commission: teleport one GHZ share to a voter (homework MINT pattern). TODO."""
    raise NotImplementedError


def receive_share(conn, epr_socket, m1, m2):
    """Voter: recover a teleported GHZ share. TODO."""
    raise NotImplementedError


# --- Phase 3: verification ---
def verify_state(conn, share):
    """Test the shared state for tampering. TODO."""
    raise NotImplementedError


# --- Phase 4: voting and tally ---
def encode_vote(share, vote):
    """Voter: encode the vote onto the share. TODO."""
    raise NotImplementedError


def measure_share(conn, share):
    """Voter: measure the encoded share, return the broadcast bit. TODO."""
    raise NotImplementedError


def aggregate(broadcasts, candidates):
    """Commission: combine the broadcast bits into a result. TODO."""
    raise NotImplementedError
