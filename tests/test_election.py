"""
tests/test_election.py -- Unit tests for the Quantum Voting Prototype.

Covers normal operation, failure handling, integrity checks,
and quantum layer behavior.
"""

import pytest
from commission import (
    create_election, add_candidate, register_voter,
    issue_token, open_election, close_election
)
from ballot import create_ballot, submit_ballot
from tally import run_tally
from audit import generate_audit_report
from quantum_core import encode_vote, decode_ballot, ENCODING_GATES, INVALID_ENCODING


# ======================================================================== #
# Fixtures
# ======================================================================== #

@pytest.fixture
def basic_election():
    """Election with 3 candidates, 3 voters, open and ready."""
    e = create_election("Test Election", election_id="TEST-01")
    add_candidate(e, "C_A", "Alice", "00")
    add_candidate(e, "C_B", "Bob",   "01")
    add_candidate(e, "C_C", "Carol", "10")
    register_voter(e, "V1", "Voter One")
    register_voter(e, "V2", "Voter Two")
    register_voter(e, "V3", "Voter Three")
    open_election(e)
    return e


@pytest.fixture
def election_with_tokens(basic_election):
    e = basic_election
    tokens = {v: issue_token(e, v) for v in ["V1", "V2", "V3"]}
    return e, tokens


# ======================================================================== #
# Normal operation
# ======================================================================== #

class TestNormalOperation:
    def test_election_setup(self, basic_election):
        assert basic_election.status == "open"
        assert len(basic_election.candidates) == 3

    def test_voter_registration(self, basic_election):
        assert len(basic_election.registered_voters) == 3
        assert basic_election.registered_voters["V1"].registered

    def test_candidate_registration(self, basic_election):
        labels = [c.label for c in basic_election.candidates.values()]
        assert "Alice" in labels and "Bob" in labels and "Carol" in labels

    def test_tokens_are_unique(self, election_with_tokens):
        _, tokens = election_with_tokens
        assert len(set(tokens.values())) == 3

    def test_ballot_accepted(self, election_with_tokens):
        e, tokens = election_with_tokens
        b = create_ballot(e, tokens["V1"], "Alice")
        submit_ballot(e, b)
        assert b.status == "submitted"

    def test_tally_matches_votes(self, election_with_tokens):
        e, tokens = election_with_tokens
        for vid, choice in [("V1", "Alice"), ("V2", "Bob"), ("V3", "Alice")]:
            submit_ballot(e, create_ballot(e, tokens[vid], choice))
        close_election(e)
        results = run_tally(e)
        assert results["Alice"] == 2
        assert results["Bob"] == 1
        assert results["Carol"] == 0


# ======================================================================== #
# Failure handling
# ======================================================================== #

class TestFailureHandling:
    def test_duplicate_token_rejected(self, election_with_tokens):
        e, tokens = election_with_tokens
        submit_ballot(e, create_ballot(e, tokens["V1"], "Alice"))
        dup = create_ballot(e, tokens["V1"], "Bob")
        submit_ballot(e, dup)
        close_election(e)
        run_tally(e)
        dup_ballots = [b for b in e.submitted_ballots if b.status == "duplicate"]
        assert len(dup_ballots) == 1

    def test_invalid_candidate_rejected(self, election_with_tokens):
        e, tokens = election_with_tokens
        b = create_ballot(e, tokens["V1"], "UnknownCandidate")
        submit_ballot(e, b)
        assert b.status == "rejected"

    def test_submission_after_close_rejected(self, election_with_tokens):
        e, tokens = election_with_tokens
        close_election(e)
        b = create_ballot(e, tokens["V1"], "Alice")
        submit_ballot(e, b)
        assert b.status == "rejected"

    def test_unregistered_voter_no_token(self, basic_election):
        with pytest.raises(ValueError):
            issue_token(basic_election, "V_UNKNOWN")

    def test_duplicate_token_issue_blocked(self, election_with_tokens):
        e, _ = election_with_tokens
        with pytest.raises(ValueError):
            issue_token(e, "V1")  # already issued


# ======================================================================== #
# Integrity checks
# ======================================================================== #

class TestIntegrity:
    def test_accepted_count_equals_tally(self, election_with_tokens):
        e, tokens = election_with_tokens
        for vid, choice in [("V1", "Alice"), ("V2", "Bob"), ("V3", "Carol")]:
            submit_ballot(e, create_ballot(e, tokens[vid], choice))
        close_election(e)
        run_tally(e)
        report = generate_audit_report(e)
        assert report.consistency_checks["accepted_equals_tally"]

    def test_duplicate_does_not_change_result(self, election_with_tokens):
        e, tokens = election_with_tokens
        submit_ballot(e, create_ballot(e, tokens["V1"], "Alice"))
        submit_ballot(e, create_ballot(e, tokens["V1"], "Bob"))  # duplicate
        submit_ballot(e, create_ballot(e, tokens["V2"], "Carol"))
        submit_ballot(e, create_ballot(e, tokens["V3"], "Alice"))
        close_election(e)
        results = run_tally(e)
        assert results["Alice"] == 2
        assert results["Bob"] == 0   # duplicate was rejected

    def test_identity_ballot_separation(self, election_with_tokens):
        """Ballots must not contain voter names."""
        e, tokens = election_with_tokens
        submit_ballot(e, create_ballot(e, tokens["V1"], "Alice"))
        for ballot in e.submitted_ballots:
            for voter in e.registered_voters.values():
                assert voter.name not in str(ballot)
                assert voter.voter_id not in str(ballot)


# ======================================================================== #
# Quantum layer
# ======================================================================== #

class TestQuantumLayer:
    def test_encoding_produces_correct_bitstring(self):
        assert encode_vote("00") == "00"
        assert encode_vote("01") == "01"
        assert encode_vote("10") == "10"

    def test_decode_matches_candidate(self):
        from models import Candidate
        candidates = {
            "C_A": Candidate("C_A", "Alice", "00"),
            "C_B": Candidate("C_B", "Bob",   "01"),
            "C_C": Candidate("C_C", "Carol", "10"),
        }
        assert decode_ballot("00", candidates) == "Alice"
        assert decode_ballot("01", candidates) == "Bob"
        assert decode_ballot("10", candidates) == "Carol"

    def test_invalid_encoding_handled(self):
        from models import Candidate
        candidates = {
            "C_A": Candidate("C_A", "Alice", "00"),
        }
        assert decode_ballot(INVALID_ENCODING, candidates) == "INVALID"

    def test_unknown_encoding_returns_invalid(self):
        result = encode_vote("11")  # reserved state
        assert result == INVALID_ENCODING
