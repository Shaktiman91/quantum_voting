"""
tests/test_quantum_core.py -- Quantum core unit tests (no SimulaQron required).
"""

from quantum_core import is_valid_encoding
from utils import INVALID_ENCODING, CANDIDATE_ENCODINGS


def test_valid_candidate_encodings():
    for encoding in CANDIDATE_ENCODINGS.values():
        assert is_valid_encoding(encoding)


def test_invalid_state_not_valid():
    assert not is_valid_encoding(INVALID_ENCODING)


def test_unknown_bits_not_valid():
    assert not is_valid_encoding("111")
    assert not is_valid_encoding("")
    assert not is_valid_encoding("xx")


def test_candidate_encoding_table():
    assert CANDIDATE_ENCODINGS["A"] == "00"
    assert CANDIDATE_ENCODINGS["B"] == "01"
    assert CANDIDATE_ENCODINGS["C"] == "10"
    assert INVALID_ENCODING == "11"
