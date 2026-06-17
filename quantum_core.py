"""
quantum_core.py -- Quantum simulation layer for ballot encoding/decoding.

Uses Qiskit with a statevector simulator for deterministic, reproducible
behavior. Each candidate maps to a compact 2-qubit gate sequence; measurement
outputs are decoded back to exactly one candidate label.

DISCLAIMER: This is a prototype demonstration of a quantum-inspired workflow.
It does NOT guarantee real-world secrecy or cryptographic election security.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.compiler import transpile

# ---------------------------------------------------------------------------
# Candidate encoding table (bitstring -> gate recipe)
# Extend this dict to support more candidates; use ceil(log2(N)) qubits.
# '11' is reserved as the INVALID state.
# ---------------------------------------------------------------------------
ENCODING_GATES = {
    "00": [],            # Candidate A: |00> -- no gates (identity)
    "01": [("x", 0)],   # Candidate B: apply X to qubit-0  -> |01>
    "10": [("x", 1)],   # Candidate C: apply X to qubit-1  -> |10>
    # '11' is deliberately absent -- it maps to INVALID
}

INVALID_ENCODING = "11"
NUM_QUBITS = 2
_SIMULATOR = AerSimulator(method="statevector")


def _build_circuit(encoding: str) -> QuantumCircuit:
    """Build a small quantum circuit for the given candidate encoding."""
    qc = QuantumCircuit(NUM_QUBITS, NUM_QUBITS)
    gates = ENCODING_GATES.get(encoding, [])
    for gate_name, qubit in gates:
        if gate_name == "x":
            qc.x(qubit)
    qc.measure(range(NUM_QUBITS), range(NUM_QUBITS))
    return qc


def encode_vote(candidate_encoding: str) -> str:
    """
    Run the quantum circuit for the given candidate encoding and
    return the deterministic measurement bitstring.
    """
    if candidate_encoding not in ENCODING_GATES:
        return INVALID_ENCODING
    qc = _build_circuit(candidate_encoding)
    compiled = transpile(qc, _SIMULATOR)
    job = _SIMULATOR.run(compiled, shots=1, seed_simulator=42)
    counts = job.result().get_counts()
    # Return the highest-count result (deterministic for valid encodings)
    result_bits = max(counts, key=counts.get)
    # Qiskit returns bits in reverse order; normalise to MSB-first 2-char string
    return result_bits.replace(" ", "").zfill(NUM_QUBITS)


def decode_ballot(encoded_vote: str, candidates: dict) -> str:
    """
    Decode a measurement bitstring back to a candidate label.
    Returns the candidate label, or 'INVALID' if no match.
    """
    for candidate in candidates.values():
        if candidate.encoding == encoded_vote:
            return candidate.label
    return "INVALID"


def visualise_circuit(candidate_encoding: str) -> str:
    """Return a text drawing of the ballot circuit (optional utility)."""
    qc = _build_circuit(candidate_encoding)
    return qc.draw(output="text").single_string()
