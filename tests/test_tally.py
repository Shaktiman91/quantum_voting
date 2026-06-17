"""
tests/test_tally.py -- Tally and audit unit tests.
"""

import pytest
from tally import run_tally, find_winner, generate_audit_report
from models import CommissionContext


def test_run_tally_normal():
    ballots = [
        {"decoded": "A"}, {"decoded": "B"}, {"decoded": "A"},
    ]
    result = run_tally(ballots)
    assert result == {"A": 2, "B": 1, "C": 0}


def test_run_tally_all_same():
    ballots = [{"decoded": "C"}, {"decoded": "C"}, {"decoded": "C"}]
    result = run_tally(ballots)
    assert result["C"] == 3
    assert result["A"] == 0


def test_find_winner_clear():
    assert find_winner({"A": 3, "B": 1, "C": 0}) == "A"


def test_find_winner_tie():
    assert find_winner({"A": 2, "B": 2, "C": 0}) == "TIE"


def test_find_winner_all_zero():
    assert find_winner({"A": 0, "B": 0, "C": 0}) == "TIE"


def test_generate_audit_clean():
    ctx = CommissionContext(expected_voters=["Voter1", "Voter2", "Voter3"])
    ctx.tokens = {"Voter1": "t1", "Voter2": "t2", "Voter3": "t3"}
    ctx.ballots = {
        "Voter1": {"token": "t1", "decoded": "A", "status": "accepted"},
        "Voter2": {"token": "t2", "decoded": "B", "status": "accepted"},
        "Voter3": {"token": "t3", "decoded": "A", "status": "accepted"},
    }
    report = generate_audit_report(ctx)
    assert report.consistency_passed is True
    assert report.winner == "A"
    assert report.accepted_ballot_count == 3
    assert report.rejected_ballot_count == 0
    assert report.errors == []


def test_generate_audit_with_invalid():
    ctx = CommissionContext(expected_voters=["Voter1", "Voter2"])
    ctx.tokens = {"Voter1": "t1", "Voter2": "t2"}
    ctx.ballots = {
        "Voter1": {"token": "t1", "decoded": "A",       "status": "accepted"},
        "Voter2": {"token": "t2", "decoded": "INVALID",  "status": "invalid"},
    }
    report = generate_audit_report(ctx)
    assert report.accepted_ballot_count == 1
    assert report.invalid_ballot_count == 1
    assert report.rejected_ballot_count == 1


def test_generate_audit_duplicate():
    ctx = CommissionContext(expected_voters=["Voter1", "Voter2"])
    ctx.tokens = {"Voter1": "t1", "Voter2": "t2"}
    ctx.ballots = {
        "Voter1":     {"token": "t1", "decoded": "A", "status": "accepted"},
        "Voter1_dup": {"token": "t1", "decoded": "B", "status": "duplicate"},
    }
    report = generate_audit_report(ctx)
    assert report.duplicate_token_count == 1
