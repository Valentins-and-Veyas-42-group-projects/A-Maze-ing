"""Command-line maze generator, solver, and ANSI-colorizer."""

import random
import sys
import time

from .errors import Err
from .generator import MazeGenerator
from .output import format_output
from .shared import Cell, Edge
from .solver import path_to_edges, solve, validate_path
from .visualize import visualize


def random_cell(width: int, height: int) -> Cell:
    """Return a random cell coordinate within the given dimensions."""

    return (random.randint(0, width - 1), random.randint(0, height - 1))


def _get_maze_input() -> MazeGenerator:
    width = int(input("Maze width: "))
    height = int(input("Maze height: "))
    perfect: bool = input("Is perfect: ").strip().lower() in (
        "true", "1", "yes", "y", "t"
    )
    entry = random_cell(width, height)
    exit_node = random_cell(width, height)

    while entry == exit_node:
        exit_node = random_cell(width, height)
    seed = input("Seed: ")
    random.seed(seed)
    return MazeGenerator(width, height, entry, exit_node, perfect)


def _random_wall_color() -> tuple[int, int, int]:
    """Return a random RGB wall color."""

    return (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )


def _save_output(mazegen: MazeGenerator) -> None:
    """Write the maze, endpoints, and path to output.txt."""

    result = format_output(mazegen.grid, mazegen.entry, mazegen.exits)
    if isinstance(result, Err):
        print(f"Error compiling layout: {result.error.name}")
        return
    with open("output.txt", "w") as f:
        _ = f.write(result)
    print("Maze layout saved to output.txt")


def _build_maze(animation: bool,
                alge: int) -> tuple[MazeGenerator, set[Cell], set[Edge]]:
    """Read input, generate, solve, and validate a fresh maze."""

    mazegen = _get_maze_input()

    def animate_step() -> None:
        print("\033[?2026h", end="", flush=True)
        print("\033[2J\033[H", end="")
        visualize(mazegen.grid, entry=mazegen.entry, exits=mazegen.exits,
                  animating=True)
        print("\033[?2026l", end="", flush=True)
        time.sleep(0.01)
    if alge == 1:
        if animation:
            gen_result = mazegen.generate(on_step=animate_step)
        else:
            gen_result = mazegen.generate()
    else:
        if animation:
            gen_result = mazegen.bin_tree(on_step=animate_step)
        else:
            gen_result = mazegen.bin_tree()
    if isinstance(gen_result, Err):
        print(f"generate failed: {gen_result.error.name}")
        sys.exit(1)

    solve_result = solve(mazegen.grid, mazegen.entry, mazegen.exits)
    if isinstance(solve_result, Err):
        print(f"solver failed: {solve_result.error.name}")
        sys.exit(1)
    path = solve_result.value

    validation = validate_path(
        mazegen.grid, path, mazegen.entry, mazegen.exits
    )
    if isinstance(validation, Err):
        print(f"solver produced invalid path: {validation.error.name}")
        sys.exit(1)

    path_cells, path_edges = path_to_edges(path, mazegen.entry)
    return mazegen, path_cells, path_edges


def _print_menu(show_path: bool) -> None:
    """Print the interactive viewer menu."""

    state = "on" if show_path else "off"
    print()
    print(f"[1] Toggle solution path (currently {state})")
    print("[2] Randomize wall color")
    print("[r] Regenerate maze")
    print("[s] Save to output.txt")
    print("[q] Quit")


def main() -> None:
    """Generate a maze, then drive the interactive ANSI viewer."""
    ani: bool = input("Is Animation: ").strip().lower() in (
        "true", "1", "yes", "y", "t"
    )
    try:
        print("\033[?1049h", end="", flush=True)
        alge = int(input("Choose alge. 1 for DFS 2 for bintree"))

        mazegen, path_cells, path_edges = _build_maze(ani, alge)
        show_path = False
        wall_color: tuple[int, int, int] | None = None
        while True:
            print("\033[2J\033[H", end="")

            visualize(
                mazegen.grid,
                path_cells if show_path else None,
                path_edges if show_path else None,
                mazegen.entry,
                mazegen.exits,
                set(mazegen.logo_cells),
                wall_color,
            )
            _print_menu(show_path)
            match input("> ").strip().lower():
                case "1":
                    show_path = not show_path
                case "2":
                    wall_color = _random_wall_color()
                case "r":
                    mazegen, path_cells, path_edges = _build_maze(ani, alge)
                case "s":
                    _save_output(mazegen)
                case "q":
                    print("\033[?1049l", end="", flush=True)
                    break
                case _:
                    print("Invalid choice.")
    finally:
        print("\033[?1049l", end="", flush=True)


if __name__ == "__main__":
    main()
