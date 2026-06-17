# Quantum Voting Prototype

> **PROTOTYPE NOTICE**
> This is a research demo of a quantum-inspired voting workflow.
> It does **not** provide real-world ballot secrecy, coercion resistance,
> or cryptographic authentication. It is an architectural demonstration
> using SimulaQron for quantum channel simulation.

## Architecture

This prototype follows the multi-process pattern from
[Quantum_week8/step4_quantum_fingerprinting](https://github.com/Shaktiman91/Quantum_week8/tree/main/materials/step4_quantum_fingerprinting):

| Quantum_week8 role | Voting role | Process |
|--------------------|-------------|----------|
| Alice / Bob | Voter | `voter1.py`, `voter2.py`, `voter3.py` |
| Referee | Election Commission | `commission.py` |
| — | Tally + Audit | `tally.py` (called by commission) |

Each voter runs as an independent process. They connect to the commission
over a classical TCP socket. The commission coordinates voting rounds, creates
EPR pairs via SimulaQron, receives correction bits, decodes ballots, tallies,
and broadcasts the result.

## Project structure

```
commission.py               Commission server (Referee pattern)
voter.py                    Shared voter client logic (Alice pattern)
voter1.py / voter2.py / voter3.py   Per-node wrappers
tally.py                    Classical tally and audit engine
quantum_core.py             EPR-based encoding, teleportation, decoding helpers
models.py                   Data classes (Ballot, Election, AuditReport, CommissionContext)
utils.py                    Shared constants
main.py                     Subprocess orchestration script
run_demo.sh                 Shell script to start everything
simulaqron_network.json     SimulaQron node topology
simulaqron_settings.json    SimulaQron settings
tests/                      pytest unit tests
```

## Message protocol

| Message | Direction | Example |
|---------|-----------|--------|
| `HELLO:<voter_id>` | Voter → Commission | `HELLO:Voter1` |
| `REGISTERED:<voter_id>:<token>` | Commission → Voter | `REGISTERED:Voter1:abc...` |
| `START_ROUND:<index>` | Commission → Voter | `START_ROUND:1` |
| `BALLOT:<voter_id>:<round>:<bits>` | Voter → Commission | `BALLOT:Voter1:1:0,1,1,0` |
| `RESULT:<winner>:<total>` | Commission → Voter | `RESULT:A:2` |
| `REJECTED:<voter_id>:<reason>` | Commission → Voter | `REJECTED:Voter1:duplicate ballot` |

## Candidate encoding (2 qubits)

| Candidate | State | Gate |
|-----------|-------|------|
| A | `\|00⟩` | identity |
| B | `\|01⟩` | X on qubit 0 |
| C | `\|10⟩` | X on qubit 1 |
| INVALID | `\|11⟩` | reserved |

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start SimulaQron network (4 nodes)
simulaqron start --nrnodes 4 --nodes "Commission,Voter1,Voter2,Voter3"

# 3a. Run demo via orchestrator
python main.py

# 3b. Or use the shell script
bash run_demo.sh

# 3c. Or start manually
python commission.py &
sleep 1
python voter1.py &
python voter2.py &
python voter3.py &

# 4. Run tests (no SimulaQron required)
pytest tests/ -v
```

## Limitations

- No real cryptographic anonymity guarantees.
- No network transport security.
- No formal anonymity proofs.
- SimulaQron backend must be running before any process starts.
- Not suitable for real elections.
