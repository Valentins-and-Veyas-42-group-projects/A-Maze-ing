"""Maze output serialization."""

from .errors import Err, Ok
from .shared import Cell, Grid
from .solver import solve


def format_output(grid: Grid, entry: Cell, exits: Cell) -> str | Err:
    """Format the grid, endpoints, and solved path as text."""

    grid_str = "\n".join("".join(format(cell, "X") for cell in row) for row in grid)
    entry_str = f"{entry[0]},{entry[1]}"
    exit_str = f"{exits[0]},{exits[1]}"
    result = solve(grid, entry, exits)

    if isinstance(result, Ok):
        path_str = result.value
    else:
        return Err(result.error)

    return f"{grid_str}\n\n{entry_str}\n{exit_str}\n{path_str}\n"
