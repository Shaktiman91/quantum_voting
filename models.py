"""
models.py -- Data classes for the Quantum Voting Prototype.

PROTOTYPE NOTICE
This is a research demo of a quantum-inspired voting workflow.
It does not provide real-world ballot secrecy, coercion resistance,
or cryptographic authentication.
"""

from dataclasses import dataclass, field
from typing import Optional, Any
import asyncio


@dataclass
class Ballot:
    token_id: str
    encoded_correction_bits: tuple
    decoded_candidate: Optional[str] = None
    status: str = "submitted"  # submitted | accepted | rejected | duplicate | invalid
    error_message: Optional[str] = None


@dataclass
class Election:
    title: str
    candidates: list
    registered_voters: list
    issued_tokens: dict = field(default_factory=dict)     # voter_id -> token
    submitted_ballots: list = field(default_factory=list)
    results: Optional[dict] = None


@dataclass
class AuditReport:
    registered_voter_count: int
    issued_token_count: int
    submitted_ballot_count: int
    accepted_ballot_count: int
    rejected_ballot_count: int
    duplicate_token_count: int
    invalid_ballot_count: int
    candidate_tallies: dict
    winner: str
    consistency_passed: bool
    errors: list = field(default_factory=list)


@dataclass
class CommissionContext:
    expected_voters: list
    writers: dict = field(default_factory=dict)           # voter_id -> StreamWriter
    tokens: dict = field(default_factory=dict)            # voter_id -> token
    ballots: dict = field(default_factory=dict)           # voter_id -> ballot dict
    current_round: Optional[int] = None
    all_connected: asyncio.Event = field(default_factory=asyncio.Event)
    all_ballots_in: asyncio.Event = field(default_factory=asyncio.Event)
    done: asyncio.Event = field(default_factory=asyncio.Event)
    result_ready: asyncio.Event = field(default_factory=asyncio.Event)
    result_data: dict = field(default_factory=dict)
    protocol_task: Any = None
