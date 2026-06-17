"""
ballot.py -- Ballot creation and submission.

DISCLAIMER: This is a prototype demonstration of a quantum-inspired workflow.
It does NOT guarantee real-world secrecy or replace audited cryptographic
protocols.
"""

from models import Election, Ballot
from quantum_core import encode_vote


def create_ballot(election: Election, token_id: str, candidate_label: str) -> Ballot:
    """
    Build a Ballot for the given token and candidate label.
    Encoding is done via the quantum layer.
    """
    # Verify token is known (but we do NOT look up voter identity here)
    if token_id not in election.issued_tokens:
        raise ValueError("Unknown token. Ballot rejected.")

    # Find candidate by label
    candidate = _find_candidate_by_label(election, candidate_label)
    if candidate is None:
        return Ballot(
            token_id=token_id,
            encoded_vote="",
            status="rejected",
            error_message=f"Unknown candidate label: '{candidate_label}'"
        )

    # Quantum encode
    encoded = encode_vote(candidate.encoding)
    ballot = Ballot(
        token_id=token_id,
        encoded_vote=encoded,
        measurement_result=encoded
    )
    return ballot


def submit_ballot(election: Election, ballot: Ballot) -> None:
    """Submit a ballot to the election. Checks election status."""
    if election.status != "open":
        ballot.status = "rejected"
        ballot.error_message = "Election is not open for submissions."
        print(f"[Ballot] Rejected (election not open): token={ballot.token_id[:8]}...")
        election.submitted_ballots.append(ballot)
        return
    election.submitted_ballots.append(ballot)
    if ballot.status != "rejected":
        print(f"[Ballot] Submitted anonymously (token={ballot.token_id[:8]}...).")
    else:
        print(f"[Ballot] Rejected on submission: {ballot.error_message}")


def _find_candidate_by_label(election: Election, label: str):
    for c in election.candidates.values():
        if c.label == label:
            return c
    return None
