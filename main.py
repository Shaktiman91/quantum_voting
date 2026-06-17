"""
main.py -- Full demo run of the Quantum Voting Prototype.

Runs a complete scripted election:
  1. Create election
  2. Register candidates A, B, C
  3. Register 5 voters
  4. Issue tokens
  5. Voters cast ballots
  6. Attempt duplicate submission
  7. Attempt invalid candidate submission
  8. Close election
  9. Tally votes
  10. Generate and print audit report

DISCLAIMER: This is a prototype demonstration of a quantum-inspired workflow.
It does NOT guarantee real-world secrecy, prevent coercion, or replace
audited cryptographic protocols. The quantum layer is educational.
"""

from commission import (
    create_election, add_candidate, register_voter,
    issue_token, open_election, close_election
)
from ballot import create_ballot, submit_ballot
from tally import run_tally
from audit import generate_audit_report, print_audit_report, save_audit_json


def main():
    print("\n" + "=" * 55)
    print("       QUANTUM VOTING PROTOTYPE -- DEMO RUN")
    print("=" * 55)

    # ------------------------------------------------------------------ #
    # Phase 1 -- Election Setup
    # ------------------------------------------------------------------ #
    election = create_election("Demo Election 2026", election_id="DEMO-01")

    add_candidate(election, "C_A", "Alice", "00")
    add_candidate(election, "C_B", "Bob",   "01")
    add_candidate(election, "C_C", "Carol", "10")

    voters = [
        ("V1", "Voter One"),
        ("V2", "Voter Two"),
        ("V3", "Voter Three"),
        ("V4", "Voter Four"),
        ("V5", "Voter Five"),
    ]
    for vid, vname in voters:
        register_voter(election, vid, vname)

    open_election(election)

    # Issue tokens
    tokens = {}
    for vid, _ in voters:
        tokens[vid] = issue_token(election, vid)

    # ------------------------------------------------------------------ #
    # Phase 2 -- Voters cast ballots
    # ------------------------------------------------------------------ #
    print("\n[Demo] Voters casting ballots...")
    vote_choices = {
        "V1": "Alice",
        "V2": "Bob",
        "V3": "Carol",
        "V4": "Alice",
        "V5": "Bob",
    }
    for vid, choice in vote_choices.items():
        ballot = create_ballot(election, tokens[vid], choice)
        submit_ballot(election, ballot)

    # ------------------------------------------------------------------ #
    # Phase 3 -- Adversarial cases
    # ------------------------------------------------------------------ #
    print("\n[Demo] Attempting duplicate submission (V1's token again)...")
    dup_ballot = create_ballot(election, tokens["V1"], "Carol")
    submit_ballot(election, dup_ballot)

    print("\n[Demo] Attempting invalid candidate...")
    invalid_ballot = create_ballot(election, tokens["V2"], "NonExistentCandidate")
    submit_ballot(election, invalid_ballot)

    # ------------------------------------------------------------------ #
    # Phase 4 -- Close, Tally, Audit
    # ------------------------------------------------------------------ #
    close_election(election)

    print("\n[Demo] Running tally...")
    run_tally(election)

    print("\n[Demo] Generating audit report...")
    report = generate_audit_report(election)
    print_audit_report(report)
    save_audit_json(report)


if __name__ == "__main__":
    main()
