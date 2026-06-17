# Quantum Voting Prototype Implementation Instructions

## Purpose

This document specifies how an implementation agent should build a Python prototype for a **quantum-inspired voting system demo** based on the sketched concept: a central election commission coordinates voting, voters submit privacy-preserving encoded ballots, and the system produces only aggregate results. The goal is not to create a production-ready election platform or claim real cryptographic election security. The goal is to create a technically clean, testable, explainable demonstration of a quantum-inspired voting workflow.

The prototype should favor clarity, determinism, modularity, and reproducibility over theoretical novelty. Where the original concept is ambiguous, the implementation should choose the simplest architecture that preserves the intended ideas of privacy, aggregation, encoding, and tally verification.

## Project Goal

Build a runnable Python demo that:
- Registers voters and candidates.
- Issues one voting credential per voter.
- Lets each voter cast one anonymous encoded ballot.
- Separates voter identity from ballot content.
- Uses a quantum simulation layer for ballot encoding and decoding.
- Produces deterministic final tallies.
- Detects duplicate, invalid, or tampered ballots.
- Generates an audit log and testable outputs.

## Scope Boundaries

### In scope
- Local Python execution.
- Quantum circuit simulation using Qiskit or Cirq.
- Command-line demo.
- Toy election sizes such as 3 to 20 voters.
- Classical audit and verification logic.
- Anonymous ballot storage.
- Unit-testable components.

### Out of scope
- Real-world cryptographic guarantees.
- Networked voting.
- Multi-device secure transport.
- Formal anonymity proofs.
- Real election deployment.
- Blockchain integration.
- Authentication beyond simple prototype credentials.

## Core Design Decision

Do **not** implement the prototype by assigning arbitrary numeric values like candidate A = -15, B = 0, C = 100 and deciding a winner directly from probability distribution weights. That makes tally semantics harder to verify and explain.

Instead, implement a **deterministic ballot model**:
- Each candidate maps to a compact bitstring or basis-state label.
- Each voter creates one encoded ballot.
- The ballot is processed through a quantum simulation layer.
- The decoded outcome maps back to exactly one candidate.
- Final election results are classical counts over decoded ballots.

This preserves the original idea of quantum encoding while keeping the tally process clear and testable.

## Recommended Protocol Model

Use a **quantum-inspired encoded ballot protocol** instead of a fully shared GHZ-state protocol for version 1.

### Why this model
- Easier to implement in Python.
- Easier to debug.
- Easier to explain to reviewers.
- Keeps privacy and tally separation explicit.
- Scales better than a single shared entangled state in a toy demo.

### Optional extension
After the first version works, a second experimental module may simulate GHZ-based parity voting for research comparison. That GHZ module should be optional and isolated from the main deterministic prototype.

## Functional Requirements

The prototype must support the following flow:

1. Election setup.
2. Voter registration.
3. Candidate registration.
4. Ballot token issuance.
5. Vote selection.
6. Ballot encoding.
7. Anonymous ballot submission.
8. Ballot validation.
9. Quantum decode or measurement simulation.
10. Deterministic tally.
11. Audit report generation.
12. Duplicate and invalid vote detection.

## System Roles

### 1. Election Commission
Responsibilities:
- Define election metadata.
- Register candidates.
- Register voters.
- Issue one-time ballot tokens.
- Close the election.
- Trigger tally and audit.

Constraints:
- Must not store final ballot content together with voter identity.
- May store a token issuance ledger.
- Must not allow the same token to be used twice.

### 2. Voter
Responsibilities:
- Receive a one-time token.
- Select exactly one candidate.
- Encode and submit a ballot.

Constraints:
- May cast only one ballot.
- Must not see other ballots.
- Must not modify the tally.

### 3. Tally Engine
Responsibilities:
- Accept anonymous ballots.
- Validate structure.
- Decode ballot state.
- Count results.
- Report invalid ballots.

Constraints:
- Must not know voter identity.
- Must operate only on tokenized ballots.

### 4. Audit Module
Responsibilities:
- Verify token uniqueness.
- Verify one ballot per used token.
- Verify that each accepted ballot maps to exactly one candidate.
- Verify counts are internally consistent.
- Produce a readable audit summary.

## Conceptual Architecture

Use this layered design:

- **Identity layer**: voter registration and token issuance.
- **Ballot layer**: anonymous ballots keyed only by token.
- **Quantum layer**: ballot encoding and simulated decoding.
- **Tally layer**: final candidate counts.
- **Audit layer**: integrity checks and reporting.

The identity layer and ballot layer must be separated in code and data structures.

## Candidate Encoding

For version 1, use fixed candidate encodings.

### Three-candidate example
- A -> `00`
- B -> `01`
- C -> `10`
- `11` reserved as invalid or unused

### Notes
- This supports deterministic decoding.
- It keeps the mapping human-readable.
- It simplifies testing.
- It allows explicit invalid-state handling.

If the implementation supports more candidates later, use the smallest number of qubits that can represent all candidates.

## Quantum Encoding Strategy

Use a simple and explainable quantum encoding layer.

### Recommended approach
For each ballot:
- Prepare a small quantum circuit with enough qubits to represent candidate states.
- Initialize qubits in a known state such as `|00>`.
- Apply gate operations based on the selected candidate.
- Simulate measurement.
- Decode the most probable or deterministic measurement output back into a candidate label.

### Example mapping
For a 2-qubit ballot:
- Candidate A: no gate or identity.
- Candidate B: apply `X` to qubit 0.
- Candidate C: apply `X` to qubit 1.
- Invalid state: any unrecognized or malformed output.

### Important rule
Avoid a design where the winner emerges from a noisy probability distribution unless the code also includes a deterministic decision rule. Elections in the prototype must yield reproducible final counts.

## Privacy Model

This prototype should simulate privacy through architecture, not claim true quantum anonymity.

### Privacy rules
- Voter identity is stored only in the registration ledger.
- Token issuance is stored separately.
- Submitted ballots contain token plus encoded content, but no voter name.
- Tally engine receives only tokenized anonymous ballots.
- Final published results include only aggregate counts and audit metadata.

### Required disclaimer in code or README
State clearly that this is a **prototype demonstration of a quantum-inspired workflow**, not a secure production voting system.

## Data Model

Implement the following core entities.

### Election
Suggested fields:
- `election_id`
- `title`
- `status` (`created`, `open`, `closed`, `tallied`)
- `candidates`
- `registered_voters`
- `issued_tokens`
- `submitted_ballots`
- `results`
- `audit_report`

### Voter
Suggested fields:
- `voter_id`
- `name` or alias
- `registered` boolean
- `token_issued` boolean
- `token_id` optional

### Candidate
Suggested fields:
- `candidate_id`
- `label`
- `encoding`

### Ballot
Suggested fields:
- `token_id`
- `encoded_vote`
- `decoded_vote`
- `status` (`submitted`, `accepted`, `rejected`, `tampered`, `duplicate`)
- `measurement_result`
- `error_message`

### AuditReport
Suggested fields:
- `registered_voter_count`
- `issued_token_count`
- `submitted_ballot_count`
- `accepted_ballot_count`
- `rejected_ballot_count`
- `duplicate_token_count`
- `invalid_ballot_count`
- `candidate_tallies`
- `consistency_checks`

## Required Modules

Implement the codebase with clear module separation.

### `main.py`
Responsibilities:
- Run a full demo election.
- Print or save outputs.
- Call setup, vote casting, tally, and audit functions.

### `models.py`
Responsibilities:
- Define data classes for Election, Voter, Candidate, Ballot, and AuditReport.

### `commission.py`
Responsibilities:
- Register voters.
- Register candidates.
- Issue tokens.
- Open and close election.

### `ballot.py`
Responsibilities:
- Build ballot objects.
- Validate vote choices.
- Convert candidate choices into encodings.

### `quantum_core.py`
Responsibilities:
- Create quantum circuits.
- Encode candidate choices.
- Run simulator backend.
- Decode measurement outputs.

### `tally.py`
Responsibilities:
- Accept ballots.
- Check token reuse.
- Mark duplicates.
- Count accepted votes.
- Produce final result dictionary.

### `audit.py`
Responsibilities:
- Validate invariants.
- Generate summary report.
- Expose machine-readable and human-readable outputs.

### `tests/`
Responsibilities:
- Verify normal and failure cases.
- Test deterministic behavior.
- Test duplicate detection.
- Test invalid candidate handling.
- Test consistency between accepted ballots and final counts.

## Implementation Sequence

The implementation agent should follow this order.

### Phase 1: Classical skeleton
Build a fully working classical prototype before adding any quantum simulation.

Tasks:
1. Define all models.
2. Implement election setup.
3. Implement voter and candidate registration.
4. Implement token issuance.
5. Implement anonymous ballot submission.
6. Implement deterministic tally and audit.
7. Add tests.

Deliverable:
- A complete classical version that already demonstrates one-voter-one-ballot and separated identity versus ballot storage.

### Phase 2: Quantum simulation layer
Add quantum simulation only after the classical skeleton is stable.

Tasks:
1. Add candidate-to-gate mapping.
2. Add circuit generation.
3. Simulate measurement.
4. Decode measurement to candidate label.
5. Plug decoded result into tally logic.
6. Preserve deterministic behavior for standard valid ballots.

Deliverable:
- A working hybrid demo where ballots are encoded or validated through a quantum circuit simulator.

### Phase 3: Audit and adversarial cases
Tasks:
1. Add duplicate-token attempts.
2. Add invalid candidate encoding.
3. Add malformed ballot payloads.
4. Add tampering simulation.
5. Confirm audit catches all failures.

Deliverable:
- A demonstrable trust and integrity layer.

### Phase 4: Optional GHZ research module
Tasks:
1. Create a separate experimental file or package.
2. Simulate a shared GHZ-state style vote aggregation.
3. Keep this isolated from the main deterministic prototype.
4. Document clearly that it is exploratory.

## Required Invariants

The implementation must enforce these invariants:

- Each registered voter receives at most one token.
- Each token may be used at most once.
- Each accepted ballot maps to exactly one valid candidate.
- Final tally equals the number of accepted ballots.
- Identity records and ballot records are stored separately.
- Closing the election prevents further submissions.
- Invalid ballots must not affect final counts.

## Suggested CLI Demo Flow

The command-line demo should support a scripted run like this:

1. Create election.
2. Add candidates A, B, C.
3. Register voters V1 to V5.
4. Issue tokens.
5. Simulate each voter casting one vote.
6. Attempt one duplicate submission.
7. Attempt one invalid ballot.
8. Close election.
9. Run tally.
10. Print results and audit report.

### Example narrative output
The output should show:
- Election created.
- Tokens issued.
- Ballots submitted anonymously.
- Duplicate ballot rejected.
- Invalid ballot rejected.
- Accepted ballots decoded.
- Final tally displayed.
- Audit checks passed or failed.

## Suggested Internal APIs

The following signatures are illustrative; equivalent designs are acceptable.

```python
create_election(title: str) -> Election
register_voter(election: Election, voter_id: str, name: str) -> None
add_candidate(election: Election, candidate_id: str, label: str, encoding: str) -> None
issue_token(election: Election, voter_id: str) -> str
create_ballot(token_id: str, candidate_label: str) -> Ballot
encode_vote(candidate_encoding: str) -> object
submit_ballot(election: Election, ballot: Ballot) -> None
close_election(election: Election) -> None
decode_ballot(ballot: Ballot) -> str
run_tally(election: Election) -> dict
generate_audit_report(election: Election) -> AuditReport
```

## Simulator Recommendation

Preferred stack:
- Python 3.11+
- Qiskit for quantum simulation
- `dataclasses` for models
- `pytest` for tests

Alternative:
- Cirq instead of Qiskit if the implementation agent prefers a lighter conceptual model

### If using Qiskit
Recommended usage:
- Small circuits only
- Statevector or qasm simulator
- Explicit measurement handling
- Clear mapping between measurement bitstrings and candidate labels

## Determinism Requirement

The demo must be reproducible.

### Acceptable methods
- Use deterministic candidate-to-gate mappings.
- Use simulator seeds where randomness exists.
- For valid ballots, decode results unambiguously.
- Keep probabilistic behavior only in optional experimental modules.

### Unacceptable behavior
- Same inputs produce different winners across runs without explanation.
- Vote counts depend on unstable measurement sampling for ordinary valid ballots.

## Testing Requirements

At minimum, implement these tests.

### Normal operation
- Election setup succeeds.
- Voter registration works.
- Candidate registration works.
- Tokens are unique.
- Ballots are accepted before election closes.
- Tally matches expected votes.

### Failure handling
- Duplicate token submission is rejected.
- Invalid candidate is rejected.
- Malformed ballot is rejected.
- Submission after close is rejected.
- Unregistered voter cannot receive token.

### Integrity checks
- Accepted ballot count equals total tally count.
- Duplicate ballots do not change result.
- Rejected ballots appear in audit report.
- Identity and ballot records remain separated.

### Quantum layer tests
- Candidate encoding creates expected circuit behavior.
- Measurement decode matches intended candidate.
- Reserved invalid state is handled properly.

## Logging and Audit Output

The implementation should generate two forms of output.

### Human-readable audit summary
Include:
- Election title.
- Number of registered voters.
- Number of issued tokens.
- Number of submitted ballots.
- Number of accepted ballots.
- Number of rejected ballots.
- Duplicate attempts.
- Invalid ballots.
- Final tally per candidate.
- Result of consistency checks.

### Machine-readable audit artifact
Save JSON or CSV with:
- token usage status
- ballot status list
- tally summary
- consistency check booleans
- error events

## Security and Honesty Requirements

The implementation agent must not overclaim.

The code comments and documentation must explicitly state:
- This is a prototype.
- This does not guarantee real-world secrecy.
- This does not prevent coercion or endpoint compromise.
- This does not replace audited cryptographic protocols.
- The quantum part is educational and architectural, not a proof of election security.

## Optional Enhancements

After the core prototype works, the implementation may add:
- A simple text menu CLI.
- Configurable number of candidates.
- Configurable voter count.
- Export of result and audit files.
- Visualization of the circuit for each ballot.
- Experimental GHZ parity mode.
- A small web UI as a separate layer.

## Non-Goals for Version 1

Do not spend time on:
- GUI-first development.
- Real cryptographic credential systems.
- Complex distributed state sharing.
- Continuous network services.
- Production-grade authentication.
- Fancy optimization.

Version 1 succeeds if it is understandable, modular, testable, and demonstrable.

## Definition of Done

The prototype is complete when all of the following are true:
- A full demo election runs from start to finish locally.
- Voters, candidates, tokens, ballots, tally, and audit are implemented.
- Ballot identities are separated from voter records.
- The quantum layer is integrated for encoding and decoding.
- Duplicate and invalid ballots are handled correctly.
- Unit tests pass.
- Output is readable and reproducible.
- Documentation clearly explains limitations.

## Final Guidance for the Implementation Agent

Prioritize clean architecture over ambitious theory. Build the classical election workflow first, then insert the quantum simulation layer as a deterministic encoding component. Treat privacy as a structural separation problem inside the prototype, not as a solved security theorem. Keep the code small, readable, and easy to demonstrate in a single local run.
