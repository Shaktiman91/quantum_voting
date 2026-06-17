"""
audit.py -- Audit and integrity verification module.

DISCLAIMER: This is a prototype demonstration of a quantum-inspired workflow.
It does NOT guarantee real-world secrecy or replace audited cryptographic
protocols.
"""

import json
from models import Election, AuditReport


def generate_audit_report(election: Election) -> AuditReport:
    """Validate invariants and produce a structured audit report."""
    if election.status != "tallied":
        raise ValueError("Election must be tallied before generating an audit report.")

    ballots = election.submitted_ballots
    submitted   = len(ballots)
    accepted    = sum(1 for b in ballots if b.status == "accepted")
    rejected    = sum(1 for b in ballots if b.status == "rejected")
    duplicates  = sum(1 for b in ballots if b.status == "duplicate")
    invalid     = sum(1 for b in ballots if b.status in ("rejected", "tampered"))

    total_tally = sum(election.results.values())

    checks = {
        "accepted_equals_tally": accepted == total_tally,
        "no_over_voting": submitted <= len(election.issued_tokens),
        "tokens_unique":  len(election.issued_tokens) == len(
            set(election.issued_tokens.keys())
        ),
        "issued_tokens_match_registered": len(election.issued_tokens) <= len(
            election.registered_voters
        ),
    }

    report = AuditReport(
        registered_voter_count=len(election.registered_voters),
        issued_token_count=len(election.issued_tokens),
        submitted_ballot_count=submitted,
        accepted_ballot_count=accepted,
        rejected_ballot_count=rejected,
        duplicate_token_count=duplicates,
        invalid_ballot_count=invalid,
        candidate_tallies=dict(election.results),
        consistency_checks=checks,
    )
    election.audit_report = report
    return report


def print_audit_report(report: AuditReport) -> None:
    """Print a human-readable audit summary."""
    print("\n" + "=" * 55)
    print("           QUANTUM VOTING AUDIT REPORT")
    print("=" * 55)
    print(f"  Registered voters    : {report.registered_voter_count}")
    print(f"  Issued tokens        : {report.issued_token_count}")
    print(f"  Ballots submitted    : {report.submitted_ballot_count}")
    print(f"  Ballots accepted     : {report.accepted_ballot_count}")
    print(f"  Ballots rejected     : {report.rejected_ballot_count}")
    print(f"  Duplicate attempts   : {report.duplicate_token_count}")
    print(f"  Invalid ballots      : {report.invalid_ballot_count}")
    print()
    print("  --- Final Tally ---")
    for candidate, count in report.candidate_tallies.items():
        print(f"    {candidate}: {count} vote(s)")
    print()
    print("  --- Consistency Checks ---")
    for check, passed in report.consistency_checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"    [{status}] {check}")
    print("=" * 55)


def save_audit_json(report: AuditReport, filepath: str = "audit_output.json") -> None:
    """Persist machine-readable audit artifact as JSON."""
    data = {
        "registered_voter_count":    report.registered_voter_count,
        "issued_token_count":         report.issued_token_count,
        "submitted_ballot_count":     report.submitted_ballot_count,
        "accepted_ballot_count":      report.accepted_ballot_count,
        "rejected_ballot_count":      report.rejected_ballot_count,
        "duplicate_token_count":      report.duplicate_token_count,
        "invalid_ballot_count":       report.invalid_ballot_count,
        "candidate_tallies":          report.candidate_tallies,
        "consistency_checks":         report.consistency_checks,
    }
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[Audit] Report saved to {filepath}")
