# Quantum Voting Prototype — Implementation Instructions

## Purpose

This document specifies how an implementation agent should build a Python prototype for a **quantum-inspired voting system demo**. The design is directly inspired by the multi-party communication architecture in [Shaktiman91/Quantum_week8](https://github.com/Shaktiman91/Quantum_week8), where `alice.py`, `bob.py`, and `referee.py` each run as independent network processes and exchange structured messages over classical TCP sockets, while sharing quantum state through EPR pairs via SimulaQron/NetQASM.

The voting prototype follows the same architectural pattern. Each participant — voter or election commission — runs as a separate Python process. Processes communicate using an asynchronous message protocol. The quantum layer handles ballot encoding through EPR-based operations and is simulated using SimulaQron and NetQASM.

***

## Overview of the Communication Architecture

Directly following the pattern in `step4_quantum_fingerprinting`, this prototype replaces the Alice/Bob/Referee fingerprinting scenario with a voting scenario:

| Quantum_week8 role | Voting prototype role | Process file |
|---|---|---|
| Alice | Voter (one per registered voter) | `voter_N.py` |
| Bob | Second voter or abstain (optional) | `voter_N.py` (same template) |
| Referee | Election Commission | `commission.py` |

Each voter process connects to the commission server over a classical TCP socket. The commission acts as the server, coordinates rounds, distributes EPR pairs, collects encoded ballots, and tallies results.

There is one additional process:

| Role | Process file | Responsibility |
|---|---|---|
| Tally and Audit | `tally.py` | Called by commission after all ballots are in; verifies and counts. |

***

## Scope

### In scope
- Local multi-process Python execution.
- Async TCP sockets using `asyncio` StreamReader and StreamWriter.
- SimulaQron quantum network simulation.
- NetQASM SDK for EPR socket creation and qubit operations.
- Deterministic ballot encoding and decoding.
- Anonymous ballot protocol with separated identity and ballot storage.
- Duplicate and invalid vote detection.
- Audit report generation.

### Out of scope
- Production security guarantees.
- Networked deployment over real infrastructure.
- Cryptographic authentication systems.
- Formal anonymity proofs.
- GUI or web interface for version 1.

***

## Technology Stack

| Component | Library |
|---|---|
| Quantum simulation | SimulaQron + NetQASM SDK |
| Network communication | `asyncio` StreamReader/StreamWriter |
| Classical protocol | Custom message strings over TCP |
| Data models | Python `dataclasses` |
| Testing | `pytest` + `pytest-asyncio` |
| Configuration | JSON files (matching repo pattern) |

Install requirements:
```
pip install simulaqron netqasm pytest pytest-asyncio
```

***

## SimulaQron Network Configuration

Follow the exact pattern from `simulaqron_network.json` in your repository. Create a `simulaqron_network.json` file in the project root with nodes for each process.

For a demo with 3 voters and 1 commission:

```json
[
  {
    "name": "default",
    "nodes": [
      {
        "Commission": {
          "app_socket": ["localhost", 8851],
          "qnodeos_socket": ["localhost", 8852],
          "vnode_socket": ["localhost", 8853]
        }
      },
      {
        "Voter1": {
          "app_socket": ["localhost", 8821],
          "qnodeos_socket": ["localhost", 8822],
          "vnode_socket": ["localhost", 8823]
        }
      },
      {
        "Voter2": {
          "app_socket": ["localhost", 8831],
          "qnodeos_socket": ["localhost", 8832],
          "vnode_socket": ["localhost", 8833]
        }
      },
      {
        "Voter3": {
          "app_socket": ["localhost", 8841],
          "qnodeos_socket": ["localhost", 8842],
          "vnode_socket": ["localhost", 8843]
        }
      }
    ],
    "topology": null
  }
]
```

Also create `simulaqron_settings.json` matching the repo's pattern to configure timeouts and backend options.

***

## Project File Structure

```
quantum_voting/
├── commission.py               # Election commission server (Referee role)
├── voter.py                    # Voter client template (Alice/Bob role)
├── voter1.py                   # Voter 1 instance (wraps voter.py with identity V1)
├── voter2.py                   # Voter 2 instance
├── voter3.py                   # Voter 3 instance
├── tally.py                    # Tally and audit engine
├── models.py                   # Dataclasses: Ballot, Election, AuditReport
├── quantum_core.py             # Quantum encoding helpers (circuit builders)
├── simulaqron_network.json     # Network topology config
├── simulaqron_settings.json    # SimulaQron settings
├── main.py                     # Orchestration script to launch all processes
├── tests/
│   ├── test_models.py
│   ├── test_tally.py
│   ├── test_quantum_core.py
│   └── test_protocol.py
└── README.md
```

***

## Message Protocol

Define a structured classical message format matching the style from the repository. All messages are UTF-8 strings passed over TCP.

### Voter to Commission

| Message | Format | Meaning |
|---|---|---|
| HELLO | `HELLO:<voter_id>` | Voter identifies itself to commission |
| BALLOT | `BALLOT:<voter_id>:<round>:<enc0>:<enc1>:...<encN>` | Voter sends encoded ballot bits |

### Commission to Voter

| Message | Format | Meaning |
|---|---|---|
| REGISTERED | `REGISTERED:<voter_id>:<token>` | Commission acknowledges voter, issues token |
| START_ROUND | `START_ROUND:<round_index>` | Commission starts a voting round |
| RESULT | `RESULT:<winner>:<total_votes>` | Commission broadcasts final result |
| REJECTED | `REJECTED:<voter_id>:<reason>` | Commission rejects a ballot |

***

## State Machine

Each process runs an async state machine, identical in spirit to the `STATE_WAIT_INPUT`, `STATE_START`, `STATE_WAIT_FOR_MESSAGE`, `STATE_DONE` pattern in `alice.py`.

### Voter state machine

```
WAIT_INPUT
    -> get candidate choice from env var or stdin
    -> transition to START

START
    -> send HELLO:<voter_id> to commission
    -> transition to WAIT_FOR_MESSAGE

WAIT_FOR_MESSAGE
    -> on REGISTERED: store token, confirm identity
    -> on START_ROUND: encode ballot, prepare quantum circuit,
         send BALLOT message with corrections, stay in WAIT_FOR_MESSAGE
    -> on RESULT: print result, transition to DONE
    -> on REJECTED: log rejection, transition to DONE

DONE
    -> exit
```

### Commission state machine

The commission is an async server (like `referee.py`) that manages a shared context object. It accepts connections from multiple voters.

```
INIT
    -> load election config
    -> start server
    -> wait for all voters to connect

WAIT_CONNECTIONS
    -> on HELLO from each voter: register, issue token, acknowledge
    -> when all voters connected: start protocol

RUNNING_ROUNDS
    -> for each round:
         broadcast START_ROUND
         create EPR pairs for each voter via SimulaQron
         wait for BALLOT from all voters
         validate each ballot
         decode ballot via quantum measurement
         after all received: continue to next round or tally

TALLY
    -> collect accepted ballot list
    -> run tally engine
    -> broadcast RESULT to all voters
    -> generate audit report
    -> transition to DONE

DONE
    -> print audit, exit
```

***

## Commission Process: `commission.py`

Model this directly after `referee.py` from your repository.

### Key structural elements to replicate

1. Use an async context dataclass (like `RefereeContext`) to hold shared state:

```python
@dataclass
class CommissionContext:
    writers: dict[str, StreamWriter] = field(default_factory=dict)
    tokens: dict[str, str] = field(default_factory=dict)
    ballots: dict[str, object] = field(default_factory=dict)
    current_round: Optional[int] = None
    all_connected: asyncio.Event = field(default_factory=asyncio.Event)
    all_ballots_in: asyncio.Event = field(default_factory=asyncio.Event)
    done: asyncio.Event = field(default_factory=asyncio.Event)
    protocol_task: Optional[asyncio.Task] = None
    expected_voters: list[str] = field(default_factory=list)
```

2. Use `SimulaQronClassicalServer` and register a client handler, same as `referee.py`.

3. In `run_protocol`, loop over voting rounds:
   - For each round, open EPR sockets to every voter.
   - Create EPR pairs using `epr_socket.create_keep(number=BALLOT_QUBITS)`.
   - Broadcast `START_ROUND:<round_index>` to all voters.
   - Wait for `all_ballots_in` event.
   - Apply corrections to each voter's EPR qubits.
   - Run quantum measurement or swap test on decoded ballots.
   - Decode to candidate label.
   - Aggregate results.

4. In `handle_client`, parse incoming messages:
   - `HELLO` -> register voter, issue token, set writer, check if all voters connected.
   - `BALLOT` -> parse correction bits, store in `ctx.ballots`, set event when all received.

5. At boot:

```python
if __name__ == "__main__":
    _here = Path(__file__).parent
    simulaqron_settings.read_from_file(_here / "simulaqron_settings.json")
    network_config.read_from_file(_here / "simulaqron_network.json")

    run_commission.ctx = CommissionContext(expected_voters=["Voter1", "Voter2", "Voter3"])
    sockets_config = SocketsConfig(network_config, "default", NodeConfigType.APP)
    server = SimulaQronClassicalServer(sockets_config, "Commission")
    server.register_client_handler(run_commission)
    print("Commission: starting server...", flush=True)
    server.start_serving()
```

***

## Voter Process: `voter.py`

Model this directly after `alice.py` from your repository.

### Key structural elements to replicate

1. Use environment variables to pass vote choice, voter ID, and node name:

```python
VOTER_ID = os.environ.get("VOTER_ID", "Voter1")
VOTE_CHOICE = os.environ.get("VOTE_CHOICE", "A")
NODE_NAME = os.environ.get("NODE_NAME", "Voter1")
```

This mirrors the `ALICE_INPUT_BITS` env var pattern in `alice.py`.

2. Implement an `encode_ballot` function analogous to `prepare_hadamard_fingerprint`:

```python
def encode_ballot(conn: NetQASMConnection, candidate: str) -> list[Qubit]:
    """
    Encode the voter's choice into a quantum state.
    A -> |00>, B -> X on qubit 0 -> |10>, C -> X on qubit 1 -> |01>
    """
    qubits = [Qubit(conn) for _ in range(BALLOT_QUBITS)]
    if candidate == "B":
        qubits[0].X()
    elif candidate == "C":
        qubits[1].X()
    return qubits
```

3. Implement `teleport_ballot` analogous to `teleport_fingerprint`:

```python
def teleport_ballot(ballot: list[Qubit], epr_qubits: list[Qubit]) -> list:
    measurements = []
    for q, epr in zip(ballot, epr_qubits):
        q.cnot(epr)
        q.H()
        measurements.append(q.measure())
        measurements.append(epr.measure())
    return measurements
```

4. In `run_voter`, implement the state machine. On `START_ROUND`:
   - Open `EPRSocket("Commission")`.
   - Open `NetQASMConnection(NODE_NAME, epr_sockets=[epr_socket], max_qubits=MAX_QUBITS)`.
   - Receive EPR halves with `epr_socket.recv_keep(number=BALLOT_QUBITS)`.
   - Encode ballot and teleport.
   - Send `BALLOT` message with correction bits, matching the `CORRECTIONS` message format in `alice.py`.

5. At boot, use `SimulaQronClassicalClient` to connect to Commission:

```python
if __name__ == "__main__":
    _here = Path(__file__).parent
    simulaqron_settings.read_from_file(_here / "simulaqron_settings.json")
    network_config.read_from_file(_here / "simulaqron_network.json")

    sockets_config = SocketsConfig(network_config, "default", NodeConfigType.APP)
    client = SimulaQronClassicalClient(sockets_config)
    print(f"{NODE_NAME}: connecting to Commission...", flush=True)
    client.run_client("Commission", run_voter)
```

***

## Voter Instance Files

Create one thin wrapper file per voter, exactly as you would spin up separate alice/bob instances. These simply set environment variables and import the shared voter logic:

### `voter1.py`
```python
import os
os.environ["VOTER_ID"] = "Voter1"
os.environ["VOTE_CHOICE"] = "A"
os.environ["NODE_NAME"] = "Voter1"
from voter import *
```

### `voter2.py`
```python
import os
os.environ["VOTER_ID"] = "Voter2"
os.environ["VOTE_CHOICE"] = "B"
os.environ["NODE_NAME"] = "Voter2"
from voter import *
```

### `voter3.py`
```python
import os
os.environ["VOTER_ID"] = "Voter3"
os.environ["VOTE_CHOICE"] = "A"
os.environ["NODE_NAME"] = "Voter3"
from voter import *
```

Alternatively, let vote choices come from stdin, matching the interactive input flow in `alice.py` where `get_input_bits()` supports both terminal and env var modes.

***

## Quantum Core: `quantum_core.py`

This module contains reusable quantum helpers used by both commission and voter processes.

### Candidate encoding table

```python
CANDIDATE_ENCODINGS = {
    "A": "00",
    "B": "01",
    "C": "10",
}
INVALID_ENCODING = "11"
BALLOT_QUBITS = 2
```

### Functions to implement

```python
def encode_ballot(conn, candidate: str) -> list
    # Prepare qubits in the state corresponding to candidate

def teleport_ballot(ballot: list, epr_qubits: list) -> list
    # Teleport ballot qubits through EPR channel, return correction measurements

def apply_ballot_corrections(qubits: list, corrections: tuple) -> None
    # Apply X and Z corrections to received qubits, same as apply_teleportation_corrections in referee.py

def decode_ballot(conn, qubits: list) -> str
    # Measure qubits and return candidate label string or "INVALID"

def is_valid_encoding(bits: str) -> bool
    # Return True if bits map to a known candidate
```

***

## Tally Engine: `tally.py`

The tally engine is called by the commission after all ballots are collected and decoded. It runs classically.

### Functions to implement

```python
def run_tally(accepted_ballots: list[Ballot]) -> dict[str, int]
    # Count decoded votes per candidate; return {"A": 2, "B": 1, "C": 0}

def find_winner(tally: dict[str, int]) -> str
    # Return candidate label with highest count

def generate_audit_report(ctx: CommissionContext) -> AuditReport
    # Verify invariants, count anomalies, return structured report

def print_audit(report: AuditReport) -> None
    # Human-readable summary
```

### Invariants to verify in audit

- `issued_tokens == registered_voters`
- `submitted_ballots <= issued_tokens`
- `accepted_ballots <= submitted_ballots`
- `sum(tally.values()) == accepted_ballot_count`
- `duplicate_token_count + invalid_ballot_count == rejected_ballot_count`
- No voter ID appears in both the ballot register and the result summary.

***

## Data Models: `models.py`

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Ballot:
    token_id: str
    encoded_correction_bits: tuple
    decoded_candidate: Optional[str] = None
    status: str = "submitted"   # submitted | accepted | rejected | duplicate | invalid
    error_message: Optional[str] = None

@dataclass
class Election:
    title: str
    candidates: list[str]
    registered_voters: list[str]
    issued_tokens: dict[str, str]   # voter_id -> token
    submitted_ballots: list[Ballot]
    results: Optional[dict[str, int]] = None

@dataclass
class AuditReport:
    registered_voter_count: int
    issued_token_count: int
    submitted_ballot_count: int
    accepted_ballot_count: int
    rejected_ballot_count: int
    duplicate_token_count: int
    invalid_ballot_count: int
    candidate_tallies: dict[str, int]
    winner: str
    consistency_passed: bool
    errors: list[str]
```

***

## Orchestration: `main.py`

Implement a script that launches all processes using `subprocess` or `asyncio.create_subprocess_exec`, mirroring how the Alice/Bob/Referee triple is started in the repo's demo flows.

Suggested sequence:
1. Start SimulaQron network backend.
2. Start `commission.py`.
3. Start each voter process (`voter1.py`, `voter2.py`, `voter3.py`).
4. Wait for all processes to complete.
5. Print combined output.

Alternatively, provide a shell script `run_demo.sh`:

```bash
#!/bin/bash
simulaqron start --nrnodes 4 --nodes "Commission,Voter1,Voter2,Voter3" &
sleep 2
python commission.py &
sleep 1
python voter1.py &
python voter2.py &
python voter3.py &
wait
```

***

## Running the Demo

Step-by-step startup order (same as running alice/bob/referee separately in your repository):

1. Start the SimulaQron network for all 4 nodes.
2. Start `commission.py` — it begins listening for voter connections.
3. Start `voter1.py`, `voter2.py`, `voter3.py` — each connects to commission.
4. Commission issues tokens, starts voting round, creates EPR pairs.
5. Each voter encodes ballot, teleports, sends correction bits.
6. Commission applies corrections, decodes, tallies.
7. Commission broadcasts `RESULT` to all voters.
8. Commission generates and prints audit report.

***

## Implementation Invariants

- Each voter sends exactly one `HELLO` per session.
- Each voter sends exactly one `BALLOT` per round.
- Commission rejects any voter that sends a second `BALLOT` in the same round.
- Token is bound to one voter ID and never reissued.
- Identity records (`voter_id -> token`) are held only in CommissionContext.
- Ballot storage (`token -> decoded_candidate`) never contains voter names.
- All quantum operations complete before corrections are sent.
- All corrections are applied before tally decoding begins.

***

## Security and Honesty Requirements

The implementation must include a clear disclaimer in the README and at the top of `commission.py`:

```
# PROTOTYPE NOTICE
# This is a research demo of a quantum-inspired voting workflow.
# It does not provide real-world ballot secrecy, coercion resistance,
# or cryptographic authentication. It is an architectural demonstration
# using SimulaQron for quantum channel simulation.
```

***

## Testing Requirements

### Unit tests

- `test_quantum_core.py`: Test `encode_ballot`, `decode_ballot`, `apply_ballot_corrections` with all valid candidates and the invalid `11` state.
- `test_tally.py`: Test `run_tally` with known ballot lists. Test `generate_audit_report` with normal and anomalous inputs. Test winner determination with ties.
- `test_models.py`: Test dataclass construction and field defaults.

### Integration tests

- `test_protocol.py`: Simulate a full 3-voter election using mock TCP streams. Verify messages flow correctly through each state. Verify REJECTED message is sent on duplicate ballot. Verify audit report consistency flags.

### Adversarial cases to test

- Voter sends `BALLOT` twice with the same token.
- Voter sends an encoding not in `CANDIDATE_ENCODINGS`.
- Voter sends wrong number of correction bits.
- Commission receives ballot after election close.
- All voters vote for the same candidate.
- Votes split equally among all candidates.

***

## Implementation Sequence

### Phase 1: Classical skeleton
Build without quantum layer first.

1. Define `models.py`.
2. Implement `commission.py` server with message protocol and state machine.
3. Implement `voter.py` client with state machine.
4. Implement `tally.py`.
5. Run a test election where ballots are plain text candidate labels, no encoding.
6. Write unit tests.

Deliverable: A complete classical multi-process voting demo that runs end-to-end with separate commission and voter processes communicating over TCP.

### Phase 2: Quantum encoding layer
Add SimulaQron and NetQASM.

1. Implement `quantum_core.py` functions.
2. Replace plain-text ballot submission with EPR-based teleportation in `voter.py`.
3. Add EPR pair creation and correction application in `commission.py`.
4. Add ballot decoding via measurement in commission tally step.
5. Verify deterministic decoding of all three candidate states.

Deliverable: A working quantum-layer demo where ballot content is encoded, teleported, and decoded through simulated quantum channels.

### Phase 3: Audit and adversarial cases
1. Add duplicate ballot detection.
2. Add invalid encoding detection.
3. Add audit report generation.
4. Test all adversarial scenarios.

Deliverable: Full demo with trust and integrity layer.

### Phase 4: Optional GHZ extension
Isolated experimental module. See Phase 4 in the original spec. Keep entirely separate from the main deterministic protocol.

***

## Definition of Done

The prototype is complete when:

- `commission.py`, `voter1.py`, `voter2.py`, `voter3.py` each run as independent processes.
- They communicate using the defined classical TCP message protocol.
- Quantum ballot encoding and teleportation use SimulaQron EPR pairs.
- Ballot identity is separated from voter identity in all data structures.
- Duplicate and invalid ballots are rejected and logged.
- Final tally is deterministic and consistent with accepted ballots.
- Audit report passes all invariant checks.
- All unit tests pass.
- Demo runs to completion from a single `main.py` or `run_demo.sh` invocation.
- README explains the architecture, startup sequence, and prototype limitations.

***

## Reference

The `alice.py`, `bob.py`, and `referee.py` patterns from [Shaktiman91/Quantum_week8/materials/step4_quantum_fingerprinting](https://github.com/Shaktiman91/Quantum_week8/tree/main/materials/step4_quantum_fingerprinting) are the direct structural reference for this prototype. The voter processes follow the `alice.py`/`bob.py` client pattern. The commission process follows the `referee.py` server pattern. The network config follows `simulaqron_network.json`. The message format follows the `HELLO`, `START_ROUND`, `CORRECTIONS`, `RESULT` protocol defined in those files.
