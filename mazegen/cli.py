"""Command-line maze generator and solver."""

import random
import sys

from .config import Config, parse_config
from .errors import Err
from .generator import MazeGenerator
from .shared import Cell
from .visualize import runviewer
import curses


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


def _build_maze(
    config: Config | None,
    isregen: bool,
) -> MazeGenerator:
    """Seed the RNG and create the MazeGenerator."""

    if config is not None and config.seed is not None and not isregen:
        random.seed(config.seed)
    elif isregen:
        random.seed()
    else:
        random.seed()

    return _get_maze_input(config)


def _print_menu(show_path: bool) -> None:
    """Print the interactive viewer menu."""

    state = "on" if show_path else "off"
    print()
    print(f"[1] Toggle solution path (currently {state})")
    print("[r] Regenerate maze")
    print("[s] Save to output.txt")
    print("[q] Quit")


def main() -> None:
    """Generate a maze, then drive the interactive viewer."""
    config = _load_config()
    output_file = config.output_file if config is not None else "output.txt"
    if config is None:
        animation: bool = input("Animation: ").strip().lower() in (
            "true", "1", "yes", "y", "t"
        )
        alge = int(input(
            "Choose alge. 1 for DFS 2 for bintree 3 for Prim's: "))
    else:
        alge = config.algorithm
        animation = config.animation

    mazegen = _build_maze(config, False)
    show_path = config.show_path if config is not None else False

    curses.wrapper(lambda stdscr: runviewer(
        stdscr, mazegen, alge, show_path, output_file, animation))


if __name__ == "__main__":
    main()
