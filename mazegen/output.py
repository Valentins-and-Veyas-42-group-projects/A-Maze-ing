"""Maze output serialization."""

from .errors import Err, MazeError, Ok
from .generator import MazeGenerator
from .shared import Cell, Grid
from .solver import solve


def format_output(
    grid: Grid, entry: Cell, exits: Cell
) -> str | Err[MazeError]:
    """Format the grid, endpoints, and solved path as text."""

    grid_str = "\n".join(
        "".join(format(cell, "X") for cell in row) for row in grid
    )
    entry_str = f"{entry[0]},{entry[1]}"
    exit_str = f"{exits[0]},{exits[1]}"
    result = solve(grid, entry, exits)

    if isinstance(result, Ok):
        path_str = result.value
    else:
        return Err(result.error)

    return f"{grid_str}\n\n{entry_str}\n{exit_str}\n{path_str}\n"


def save_output(mazegen: MazeGenerator, output_file: str) -> None:
    """Write the maze, endpoints, and path to an output file."""

    result = format_output(mazegen.grid, mazegen.entry, mazegen.exits)
    if isinstance(result, Err):
        print(f"Error compiling layout: {result.error.name}")
        return
    with open(output_file, "w") as f:
        _ = f.write(result)
    print(f"Maze layout saved to {output_file}")
