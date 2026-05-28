"""Command-line maze generator, solver, and ANSI-colorizer."""

import random
import sys

from .errors import Err, Ok
from .generator import MazeGenerator
from .output import format_output
from .shared import Cell
from .solver import path_to_edges, solve, validate_path
from .visualize import visualize


def random_cell(width: int, height: int) -> Cell:
    """Return a random cell coordinate within the given dimensions."""

    return (random.randint(0, width - 1), random.randint(0, height - 1))


def main() -> None:
    """CLI execution entrypoint."""

    width = int(input("Enter width: "))
    height = int(input("Enter height: "))
    perfect: bool = input("Is perfect: ").strip().lower() in (
        "true", "1", "yes", "y", "t"
    )

    entry = random_cell(width, height)
    exit_node = random_cell(width, height)
    while entry == exit_node:
        exit_node = random_cell(width, height)

    mazegen = MazeGenerator(width, height, entry, exit_node, perfect)
    gen_result = mazegen.generate()
    if isinstance(gen_result, Err):
        print(f"generate failed: {gen_result.error.name}")
        sys.exit(1)

    solve_result = solve(mazegen.grid, mazegen.entry, mazegen.exits)
    if isinstance(solve_result, Ok):
        path = solve_result.value
    else:
        print(f"solver failed: {solve_result.error.name}")
        sys.exit(1)

    validation = validate_path(
        mazegen.grid, path, mazegen.entry, mazegen.exits
    )
    if isinstance(validation, Err):
        print(f"solver produced invalid path: {validation.error.name}")
        sys.exit(1)

    path_cells, path_edges = path_to_edges(path, mazegen.entry)
    visualize(
        mazegen.grid, path_cells, path_edges, mazegen.entry, mazegen.exits,
        set(mazegen.logo_cells)
    )

    result = format_output(mazegen.grid, mazegen.entry, mazegen.exits)
    output_file = "output.txt"
    if isinstance(result, str):
        with open(output_file, "w") as f:
            _ = f.write(result)
        print(f"\nMaze layout configurations saved cleanly to {output_file}")
    else:
        print(f"Error compiling layout: {result.error}")


if __name__ == "__main__":
    main()
