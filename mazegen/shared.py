"""Shared maze constants and helpers."""

from enum import Enum

Cell = tuple[int, int]
Grid = list[list[int]]
Edge = tuple[Cell, Cell]


class Direction(Enum):
    """Cardinal directions encoded as bit positions for cell walls."""

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


DIRECTION_DELTAS: dict[Direction, Cell] = {
    Direction.NORTH: (0, -1),
    Direction.EAST: (1, 0),
    Direction.SOUTH: (0, 1),
    Direction.WEST: (-1, 0),
}

DELTA_TO_DIRECTION: dict[Cell, Direction] = {
    delta: direction for direction, delta in DIRECTION_DELTAS.items()
}

DIRECTION_TO_LETTER: dict[Direction, str] = {
    Direction.NORTH: "N",
    Direction.EAST: "E",
    Direction.SOUTH: "S",
    Direction.WEST: "W",
}

LETTER_TO_DIRECTION: dict[str, Direction] = {
    letter: direction for direction, letter in DIRECTION_TO_LETTER.items()
}


def is_inbounds(x: int, y: int, width: int, height: int) -> bool:
    """Return True if (x, y) lies within the grid bounds."""

    return 0 <= x < width and 0 <= y < height
