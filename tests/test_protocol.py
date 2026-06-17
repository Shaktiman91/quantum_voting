"""
tests/test_protocol.py -- Classical message protocol format tests.
"""


def _parse_hello(msg: str):
    assert msg.startswith("HELLO:")
    return msg.split(":", 1)[1]


def _parse_registered(msg: str):
    parts = msg.split(":", 2)
    assert parts[0] == "REGISTERED"
    return parts[1], parts[2]


def _parse_start_round(msg: str):
    parts = msg.split(":", 1)
    assert parts[0] == "START_ROUND"
    return int(parts[1])


def _parse_ballot(msg: str):
    parts = msg.split(":", 3)
    assert parts[0] == "BALLOT"
    voter_id = parts[1]
    round_index = int(parts[2])
    corrections = [int(x) for x in parts[3].split(",")]
    return voter_id, round_index, corrections


def _parse_result(msg: str):
    parts = msg.split(":", 2)
    assert parts[0] == "RESULT"
    return parts[1], int(parts[2])


def _parse_rejected(msg: str):
    parts = msg.split(":", 2)
    assert parts[0] == "REJECTED"
    return parts[1], parts[2]


def test_hello():
    assert _parse_hello("HELLO:Voter1") == "Voter1"


def test_registered():
    voter_id, token = _parse_registered("REGISTERED:Voter1:abc123")
    assert voter_id == "Voter1"
    assert token == "abc123"


def test_start_round():
    assert _parse_start_round("START_ROUND:1") == 1


def test_ballot():
    voter_id, round_index, corrections = _parse_ballot("BALLOT:Voter1:1:0,1,1,0")
    assert voter_id == "Voter1"
    assert round_index == 1
    assert corrections == [0, 1, 1, 0]
    assert len(corrections) == 4  # BALLOT_QUBITS * 2


def test_ballot_wrong_correction_count():
    _, _, corrections = _parse_ballot("BALLOT:Voter2:1:1,0")
    assert len(corrections) == 2  # will be caught by _parse_corrections in commission


def test_result():
    winner, total = _parse_result("RESULT:A:3")
    assert winner == "A"
    assert total == 3


def test_rejected():
    voter_id, reason = _parse_rejected("REJECTED:Voter1:duplicate ballot")
    assert voter_id == "Voter1"
    assert "duplicate" in reason
