"""Shared constants for the quantum voting demo."""

VOTER_NAMES = ["Voter1", "Voter2", "Voter3"]
NUM_VOTERS = len(VOTER_NAMES)
CANDIDATES = ["A", "B", "C"]
MAX_QUBITS = 16
BALLOT_QUBITS = 2

CANDIDATE_ENCODINGS = {
    "A": "00",
    "B": "01",
    "C": "10",
}
INVALID_ENCODING = "11"
