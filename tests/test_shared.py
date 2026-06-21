"""Shared utility tests."""

from mazegen.shared import is_inbounds


def test_is_inbounds() -> None:
    assert is_inbounds(0, 0, 10, 10) is True
    assert is_inbounds(9, 9, 10, 10) is True
    assert is_inbounds(-1, 0, 10, 10) is False
    assert is_inbounds(0, -1, 10, 10) is False
    assert is_inbounds(10, 0, 10, 10) is False
    assert is_inbounds(0, 10, 10, 10) is False
