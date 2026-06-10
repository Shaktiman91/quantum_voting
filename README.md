# Quantum Voting

GHZ-based quantum voting on the SimulaQron / NetQASM backend. an Election Commission shares one GHZ state with the voters.
Each voter encodes a vote onto its own share, so the commission only ever
recovers an aggregate result, never an individual ballot. Privacy comes from the
entanglement, not from a computational hardness assumption.

## Files
- commission.py   election commission: classical server, GHZ source, tally
- voter.py        a single voter: classical client, encodes one vote
- utils.py        shared constants and quantum primitives, grouped by phase
- simulaqron_network.json / simulaqron_settings.json   backend config

## Phases
1. Initialization
2. GHZ creation and sharing
3. Verification
4. Voting and tally

## Run (inside WSL)
Activate the venv, start the SimulaQron backend, then run the commission and one
voter per process. Exact commands are in the project chat / report.
