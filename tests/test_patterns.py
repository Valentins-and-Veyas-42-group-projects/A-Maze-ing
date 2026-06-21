"""Pattern selection and fitting tests."""

from mazegen.patterns import (
    PATTERN_LARGE,
    PATTERN_MEDIUM,
    PATTERN_SMALL,
    Pattern,
    select_pattern,
)


def test_pattern_offset() -> None:
    p = Pattern(cells=[], width=5, height=3)
    assert p.offset(10, 10) == (2, 3)


def test_pattern_placed_cells() -> None:
    p = Pattern(cells=[(0, 0), (1, 1)], width=2, height=2)
    assert p.placed_cells(4, 4) == [(1, 1), (2, 2)]


def test_pattern_fits() -> None:
    p = Pattern(cells=[], width=5, height=3)
    assert p.fits(6, 4) is True
    assert p.fits(5, 3) is False
    assert p.fits(4, 2) is False


def test_select_pattern() -> None:
    assert select_pattern(10, 10) == PATTERN_SMALL
    assert select_pattern(24, 22) == PATTERN_SMALL

    assert select_pattern(25, 23) == PATTERN_MEDIUM
    assert select_pattern(39, 37) == PATTERN_MEDIUM

    assert select_pattern(40, 38) == PATTERN_LARGE
    assert select_pattern(5, 5) == PATTERN_LARGE
