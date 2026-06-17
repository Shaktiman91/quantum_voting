"""
tests/test_models.py -- Data model construction and defaults.
"""

from models import Ballot, Election, AuditReport, CommissionContext


def test_ballot_defaults():
    b = Ballot(token_id="t1", encoded_correction_bits=(0, 1, 1, 0))
    assert b.status == "submitted"
    assert b.decoded_candidate is None
    assert b.error_message is None


def test_election_defaults():
    e = Election(title="Demo", candidates=["A", "B", "C"], registered_voters=["V1"])
    assert e.issued_tokens == {}
    assert e.submitted_ballots == []
    assert e.results is None


def test_audit_report_fields():
    r = AuditReport(
        registered_voter_count=3, issued_token_count=3,
        submitted_ballot_count=3, accepted_ballot_count=3,
        rejected_ballot_count=0, duplicate_token_count=0,
        invalid_ballot_count=0, candidate_tallies={"A": 2, "B": 1, "C": 0},
        winner="A", consistency_passed=True,
    )
    assert r.winner == "A"
    assert r.consistency_passed is True
    assert r.errors == []


def test_context_event_defaults():
    ctx = CommissionContext(expected_voters=["Voter1", "Voter2"])
    assert not ctx.all_connected.is_set()
    assert not ctx.all_ballots_in.is_set()
    assert not ctx.result_ready.is_set()
    assert ctx.ballots == {}
    assert ctx.tokens == {}
