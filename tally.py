"""
tally.py -- Ballot validation, duplicate detection, and vote counting.

DISCLAIMER: This is a prototype demonstration of a quantum-inspired workflow.
It does NOT guarantee real-world secrecy or replace audited cryptographic
protocols.
"""

from models import Election, Ballot
from quantum_core import decode_ballot


def run_tally(election: Election) -> dict:
    """
    Validate and decode all submitted ballots, then count accepted votes.
    Returns a dict {candidate_label: count}.
    """
    if election.status != "closed":
        raise ValueError("Election must be closed before tallying.")

    seen_tokens: set = set()
    tally: dict = {c.label: 0 for c in election.candidates.values()}

    for ballot in election.submitted_ballots:
        # Skip ballots already marked rejected during submission
        if ballot.status == "rejected":
            continue

        # Duplicate token detection
        if ballot.token_id in seen_tokens:
            ballot.status = "duplicate"
            ballot.error_message = "Duplicate token submission."
            print(f"[Tally] Duplicate ballot detected: token={ballot.token_id[:8]}...")
            continue
        seen_tokens.add(ballot.token_id)

        # Decode via quantum layer
        decoded = decode_ballot(ballot.encoded_vote, election.candidates)
        ballot.decoded_vote = decoded

        if decoded == "INVALID":
            ballot.status = "rejected"
            ballot.error_message = "Ballot decoded to INVALID state."
            print(f"[Tally] Invalid ballot (bad encoding): token={ballot.token_id[:8]}...")
        else:
            ballot.status = "accepted"
            tally[decoded] += 1
            print(f"[Tally] Ballot accepted. Decoded candidate: {decoded}")

    election.results = tally
    election.status = "tallied"
    print(f"[Tally] Final tally: {tally}")
    return tally
