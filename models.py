"""
models.py -- Data classes for the Quantum Voting Prototype.

DISCLAIMER: This is a prototype demonstration of a quantum-inspired workflow.
It does NOT guarantee real-world secrecy, prevent coercion or endpoint
compromise, or replace audited cryptographic protocols. The quantum part is
educational and architectural, not a proof of election security.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Candidate:
    candidate_id: str
    label: str
    encoding: str  # bitstring e.g. '00', '01', '10'


@dataclass
class Voter:
    voter_id: str
    name: str
    registered: bool = False
    token_issued: bool = False
    token_id: Optional[str] = None


@dataclass
class Ballot:
    token_id: str
    encoded_vote: str          # bitstring produced by quantum_core
    decoded_vote: Optional[str] = None   # candidate label after decoding
    status: str = "submitted"  # submitted | accepted | rejected | duplicate | tampered
    measurement_result: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class AuditReport:
    registered_voter_count: int = 0
    issued_token_count: int = 0
    submitted_ballot_count: int = 0
    accepted_ballot_count: int = 0
    rejected_ballot_count: int = 0
    duplicate_token_count: int = 0
    invalid_ballot_count: int = 0
    candidate_tallies: dict = field(default_factory=dict)
    consistency_checks: dict = field(default_factory=dict)


@dataclass
class Election:
    election_id: str
    title: str
    status: str = "created"   # created | open | closed | tallied
    candidates: dict = field(default_factory=dict)       # candidate_id -> Candidate
    registered_voters: dict = field(default_factory=dict)  # voter_id -> Voter
    issued_tokens: dict = field(default_factory=dict)    # token_id -> voter_id
    submitted_ballots: list = field(default_factory=list)  # list[Ballot]
    results: dict = field(default_factory=dict)          # candidate_label -> count
    audit_report: Optional[AuditReport] = None
