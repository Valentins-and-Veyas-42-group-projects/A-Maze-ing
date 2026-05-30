"""Command-line maze generator, solver, and ANSI-colorizer."""

import random
import sys
import time

from .config import Config, parse_config
from .errors import Err
from .generator import MazeGenerator
from .output import format_output
from .shared import Cell, Edge
from .solver import path_to_edges, solve, validate_path
from .visualize import visualize


def random_cell(width: int, height: int) -> Cell:
    """Return a random cell coordinate within the given dimensions."""

    return (random.randint(0, width - 1), random.randint(0, height - 1))


def _load_config() -> Config | None:
    """Load an optional config file passed as the first CLI argument."""

    if len(sys.argv) <= 1:
        return None

    result = parse_config(sys.argv[1])
    if isinstance(result, Err):
        result.print_diagnostic()
        sys.exit(1)
    return result.value


def _get_maze_input(config: Config | None) -> MazeGenerator:
    if config is not None:
        return MazeGenerator(
            config.width,
            config.height,
            config.entry,
            config.exits,
            config.perfect,
        )

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


def _save_output(mazegen: MazeGenerator, output_file: str) -> None:
    """Write the maze, endpoints, and path to an output file."""

    result = format_output(mazegen.grid, mazegen.entry, mazegen.exits)
    if isinstance(result, Err):
        print(f"Error compiling layout: {result.error.name}")
        return
    with open(output_file, "w") as f:
        _ = f.write(result)
    print(f"Maze layout saved to {output_file}")


def _build_maze(

    animation: bool,
    alge: int,
    config: Config | None,
    isregen: bool,
) -> tuple[MazeGenerator, set[Cell], set[Edge]]:
    """Read input, generate, solve, and validate a fresh maze."""

    if config is not None and config.seed is not None and not isregen:
        random.seed(config.seed)
    elif isregen:
        alge = int(input(
            "Choose alge. 1 for DFS 2 for bintree 3 for Prim's: "))
        random.seed()

        # animation = input("Is Animation: ").strip().lower() in (
        #   "true", "1", "yes", "y", "t"
        # )
    else:
        random.seed()

    mazegen = _get_maze_input(config)
    wait_time = 0.001
    if config is not None:
        wait_time = config.force_wait_time / config.speed

    def animate_step() -> None:
        print("\033[?2026h", end="", flush=True)
        print("\033[2J\033[H", end="")
        visualize(mazegen.grid, entry=mazegen.entry, exits=mazegen.exits,
                  animating=True, cursor=mazegen.cursor)
        print("\033[?2026l", end="", flush=True)
        time.sleep(wait_time)
    if alge == 1:
        if animation:
            gen_result = mazegen.generate(on_step=animate_step)
        else:
            gen_result = mazegen.generate()
    elif alge == 3:
        if animation:
            gen_result = mazegen.prims_algorithm(on_step=animate_step)
        else:
            gen_result = mazegen.prims_algorithm()
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
    config = _load_config()
    output_file = config.output_file if config is not None else "output.txt"
    if config is None:
        ani: bool = input("Is Animation: ").strip().lower() in (
            "true", "1", "yes", "y", "t"
        )
        alge = int(input(
            "Choose alge. 1 for DFS 2 for bintree 3 for Prim's: "))
    else:
        ani = config.animation
        alge = config.algorithm
    try:
        print("\033[?1049h", end="", flush=True)

        mazegen, path_cells, path_edges = _build_maze(ani, alge, config, False)
        show_path = config.show_path if config is not None else False
        wall_color = config.wall_color if config is not None else None
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
                    mazegen, path_cells, path_edges = _build_maze(
                        ani, alge, config, True)
                case "s":
                    _save_output(mazegen, output_file)
                case "q":
                    print("\033[?1049l", end="", flush=True)
                    break
                case _:
                    print("Invalid choice.")
    finally:
        print("\033[?1049l", end="", flush=True)


if __name__ == "__main__":
    main()
