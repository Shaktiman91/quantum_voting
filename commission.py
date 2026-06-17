"""
commission.py -- Election Commission logic.

DISCLAIMER: This is a prototype demonstration of a quantum-inspired workflow.
It does NOT guarantee real-world secrecy or replace audited cryptographic
protocols.
"""

import uuid
from models import Election, Voter, Candidate


def create_election(title: str, election_id: str = None) -> Election:
    """Create a new election and return it in 'created' status."""
    eid = election_id or str(uuid.uuid4())[:8]
    election = Election(election_id=eid, title=title)
    print(f"[Commission] Election created: '{title}' (id={eid})")
    return election


def add_candidate(election: Election, candidate_id: str, label: str, encoding: str) -> None:
    """Register a candidate with a fixed bitstring encoding."""
    if election.status != "created":
        raise ValueError("Candidates can only be added before the election opens.")
    if candidate_id in election.candidates:
        raise ValueError(f"Candidate '{candidate_id}' already registered.")
    election.candidates[candidate_id] = Candidate(
        candidate_id=candidate_id, label=label, encoding=encoding
    )
    print(f"[Commission] Candidate registered: {label} (encoding={encoding})")


def register_voter(election: Election, voter_id: str, name: str) -> None:
    """Register a voter. Must be done before the election opens."""
    if election.status not in ("created", "open"):
        raise ValueError("Voter registration is closed.")
    if voter_id in election.registered_voters:
        raise ValueError(f"Voter '{voter_id}' already registered.")
    voter = Voter(voter_id=voter_id, name=name, registered=True)
    election.registered_voters[voter_id] = voter
    print(f"[Commission] Voter registered: {name} (id={voter_id})")


def issue_token(election: Election, voter_id: str) -> str:
    """Issue a one-time anonymous ballot token to a registered voter."""
    if voter_id not in election.registered_voters:
        raise ValueError(f"Voter '{voter_id}' is not registered.")
    voter = election.registered_voters[voter_id]
    if voter.token_issued:
        raise ValueError(f"Voter '{voter_id}' has already received a token.")
    token_id = str(uuid.uuid4())
    voter.token_issued = True
    voter.token_id = token_id
    election.issued_tokens[token_id] = voter_id  # identity layer
    print(f"[Commission] Token issued to voter '{voter_id}'.")
    return token_id


def open_election(election: Election) -> None:
    """Open the election to accept ballots."""
    if election.status != "created":
        raise ValueError("Election must be in 'created' status to open.")
    if not election.candidates:
        raise ValueError("No candidates registered.")
    election.status = "open"
    print(f"[Commission] Election '{election.title}' is now OPEN.")


def close_election(election: Election) -> None:
    """Close the election; no more ballot submissions allowed."""
    if election.status != "open":
        raise ValueError("Only an open election can be closed.")
    election.status = "closed"
    print(f"[Commission] Election '{election.title}' is now CLOSED.")
