"""
quantum_core.py -- Quantum helpers for ballot encoding and decoding.

Uses NetQASM Qubit primitives for EPR-based ballot teleportation.

NOTE on measurement conversion:
  teleport_ballot returns raw Future objects from q.measure() / epr.measure().
  These are only resolved after the enclosing NetQASMConnection context flushes.
  Callers must convert to int AFTER the `with` block exits -- never inside it.
  decode_ballot calls conn.flush() before reading measurement results.
"""

from netqasm.sdk import Qubit
from utils import CANDIDATE_ENCODINGS, INVALID_ENCODING, BALLOT_QUBITS


def _to_int(m) -> int:
    """Normalise a NetQASM measurement result to a plain int."""
    if isinstance(m, int):
        return m
    if hasattr(m, 'value'):
        return int(m.value)
    return int(m)


def encode_ballot(conn, candidate: str) -> list:
    """
    Prepare 2 qubits in the state encoding the chosen candidate.
      A -> |00>  (identity)
      B -> |01>  (X on qubit 0)
      C -> |10>  (X on qubit 1)
    """
    qubits = [Qubit(conn) for _ in range(BALLOT_QUBITS)]
    if candidate == "B":
        qubits[0].X()
    elif candidate == "C":
        qubits[1].X()
    return qubits


def teleport_ballot(ballot: list, epr_qubits: list) -> list:
    """
    Teleport ballot qubits through EPR channel.
    Returns a list of (Future, Future) pairs -- callers must convert to int
    AFTER the enclosing connection context has flushed.
    """
    corrections = []
    for q, epr in zip(ballot, epr_qubits):
        q.cnot(epr)
        q.H()
        m1 = q.measure()    # returns a Future; do NOT call int() here
        m2 = epr.measure()  # returns a Future; do NOT call int() here
        corrections.append((m1, m2))
    return corrections


def apply_ballot_corrections(qubits: list, corrections: list) -> None:
    """
    Apply X/Z corrections to EPR qubits held by the commission.
    corrections must be a list of (int, int) pairs (already resolved).
    Must be called inside an active NetQASMConnection context.
    Mirrors apply_teleportation_corrections from referee.py:
      X when m2 (epr_measure) == 1
      Z when m1 (q_measure)   == 1
    """
    for qubit, (m1, m2) in zip(qubits, corrections):
        if m2 == 1:
            qubit.X()
        if m1 == 1:
            qubit.Z()


def decode_ballot(conn, qubits: list) -> str:
    """
    Measure commission-side EPR qubits and decode to a candidate label.
    Must be called inside the same NetQASMConnection context in which
    the qubits were created. Returns 'INVALID' if bitstring is unknown.
    Caller should call conn.flush() after this to resolve the measurements.
    """
    measurements = [q.measure() for q in qubits]
    conn.flush()  # resolve measurement futures immediately
    bits = "".join(str(_to_int(m)) for m in measurements)
    for candidate, encoding in CANDIDATE_ENCODINGS.items():
        if encoding == bits:
            return candidate
    return "INVALID"


def is_valid_encoding(bits: str) -> bool:
    """Return True if bits map to a known candidate encoding."""
    return bits in CANDIDATE_ENCODINGS.values()
