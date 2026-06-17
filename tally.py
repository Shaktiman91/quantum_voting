"""
tally.py -- Tally and audit engine (runs classically after all ballots decoded).
"""

from models import AuditReport, CommissionContext


def run_tally(accepted_ballots: list) -> dict:
    """Count decoded votes per candidate. Returns {candidate: count}."""
    tally = {"A": 0, "B": 0, "C": 0}
    for ballot in accepted_ballots:
        decoded = ballot.get("decoded")
        if decoded in tally:
            tally[decoded] += 1
    return tally


def find_winner(tally: dict) -> str:
    """Return candidate with highest count, or 'TIE' on equal top scores."""
    if not tally:
        return "TIE"
    max_votes = max(tally.values())
    winners = [c for c, v in tally.items() if v == max_votes]
    return winners[0] if len(winners) == 1 else "TIE"


def generate_audit_report(ctx: CommissionContext) -> AuditReport:
    """Validate all invariants and produce a structured audit report."""
    submitted = len(ctx.ballots)
    accepted_list = [b for b in ctx.ballots.values() if b.get("status") == "accepted"]
    accepted = len(accepted_list)
    rejected = sum(1 for b in ctx.ballots.values() if b.get("status") != "accepted")
    duplicates = sum(1 for b in ctx.ballots.values() if b.get("status") == "duplicate")
    invalid = sum(1 for b in ctx.ballots.values() if b.get("status") == "invalid")

    tally = run_tally(accepted_list)
    winner = find_winner(tally)

    errors = []
    if len(ctx.tokens) != len(ctx.expected_voters):
        errors.append("issued_tokens != registered_voters")
    if submitted > len(ctx.tokens):
        errors.append("submitted_ballots > issued_tokens")
    if accepted > submitted:
        errors.append("accepted_ballots > submitted_ballots")
    if sum(tally.values()) != accepted:
        errors.append("sum(tally.values()) != accepted_ballot_count")
    if duplicates + invalid != rejected:
        errors.append("duplicate + invalid != rejected_ballot_count")

    return AuditReport(
        registered_voter_count=len(ctx.expected_voters),
        issued_token_count=len(ctx.tokens),
        submitted_ballot_count=submitted,
        accepted_ballot_count=accepted,
        rejected_ballot_count=rejected,
        duplicate_token_count=duplicates,
        invalid_ballot_count=invalid,
        candidate_tallies=tally,
        winner=winner,
        consistency_passed=(len(errors) == 0),
        errors=errors,
    )


def print_audit(report: AuditReport) -> None:
    """Print a human-readable audit summary."""
    print("\n" + "=" * 55)
    print("           QUANTUM VOTING AUDIT REPORT")
    print("=" * 55)
    print(f"  Registered voters    : {report.registered_voter_count}")
    print(f"  Issued tokens        : {report.issued_token_count}")
    print(f"  Submitted ballots    : {report.submitted_ballot_count}")
    print(f"  Accepted ballots     : {report.accepted_ballot_count}")
    print(f"  Rejected ballots     : {report.rejected_ballot_count}")
    print(f"  Duplicate attempts   : {report.duplicate_token_count}")
    print(f"  Invalid ballots      : {report.invalid_ballot_count}")
    print(f"  Winner               : {report.winner}")
    print()
    print("  --- Final Tally ---")
    for candidate, count in report.candidate_tallies.items():
        print(f"    {candidate}: {count} vote(s)")
    print()
    status = "PASS" if report.consistency_passed else "FAIL"
    print(f"  [{status}] consistency checks")
    for error in report.errors:
        print(f"  [ERROR] {error}")
    print("=" * 55)
