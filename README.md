# Quantum Voting Prototype

> **DISCLAIMER**: This is a prototype demonstration of a quantum-inspired
> voting workflow. It does **not** guarantee real-world secrecy, prevent
> coercion or endpoint compromise, or replace audited cryptographic protocols.
> The quantum part is educational and architectural, not a proof of election
> security.

## Overview

A runnable Python demo of a quantum-inspired voting system that:
- Registers voters and candidates.
- Issues one-time ballot tokens (identity separated from ballot content).
- Encodes each ballot through a Qiskit quantum circuit simulation.
- Produces deterministic, reproducible final tallies.
- Detects duplicate, invalid, and tampered ballots.
- Generates a human-readable and machine-readable audit report.

## Architecture

```
models.py        -- Data classes (Election, Voter, Candidate, Ballot, AuditReport)
commission.py    -- Election Commission: setup, registration, token issuance
ballot.py        -- Ballot creation and anonymous submission
quantum_core.py  -- Qiskit quantum circuit encoding & decoding
tally.py         -- Duplicate detection, validation, vote counting
audit.py         -- Invariant checks and audit report generation
main.py          -- Full scripted demo run
tests/           -- pytest unit tests
```

## Candidate Encoding (2 qubits)

| Candidate | Encoding | Gate Applied    |
|-----------|----------|-----------------|
| Alice     | `00`     | Identity (none) |
| Bob       | `01`     | X on qubit 0    |
| Carol     | `10`     | X on qubit 1    |
| INVALID   | `11`     | Reserved        |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the full demo
python main.py

# 3. Run tests
pytest tests/ -v
```

## Demo Flow

1. Create election `Demo Election 2026`
2. Register candidates: Alice, Bob, Carol
3. Register 5 voters (V1–V5)
4. Issue one token per voter
5. Each voter casts one ballot (quantum encoded)
6. Attempt duplicate submission → rejected
7. Attempt invalid candidate → rejected
8. Close election → tally → audit report
9. Audit JSON saved to `audit_output.json`

## Privacy Model

- Voter identity is stored only in the registration ledger.
- Tokens link to voter identity, but ballots store only token + encoded content.
- The tally engine never sees voter names.
- Results contain only aggregate counts.

## Limitations

- No real cryptographic anonymity guarantees.
- No network transport security.
- No formal anonymity proofs.
- Not suitable for real elections.
