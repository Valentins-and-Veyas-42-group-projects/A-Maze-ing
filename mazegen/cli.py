"""Command-line maze generator and solver."""

import curses
import random
import sys

from .config import Config, parse_config
from .errors import Err
from .generator import MazeGenerator
from .visualize import runviewer


def _load_config() -> Config | None:
    """Load an optional config file passed as the first CLI argument."""

    if len(sys.argv) <= 1:
        return None

    result = parse_config(sys.argv[1])
    if isinstance(result, Err):
        result.print_diagnostic()
        sys.exit(1)
    return result.value


def _build_maze(config: Config, isregen: bool) -> MazeGenerator:
    """Seed the RNG and create the MazeGenerator."""

    if config.seed is not None and not isregen:
        random.seed(config.seed)
    else:
        random.seed()

    return MazeGenerator(
        config.width,
        config.height,
        config.entry,
        config.exits,
        config.perfect,
    )


def _print_goodbye() -> None:
    """Print a goodbye message upon exit."""
    print("\n[mazegen] Interrupted by user.")


def main() -> None:
    """Generate a maze, then drive the interactive viewer."""

    config = _load_config()
    if config is None:
        print("Usage: python3 a_maze_ing.py config.txt")
        return

    try:
        curses.wrapper(
            lambda stdscr: runviewer(
                stdscr,
                lambda: _build_maze(config, True),
                config.algorithm,
                config.show_path,
                config.output_file,
                config.animation,
            )
        )
    except KeyboardInterrupt:
        _print_goodbye()


if __name__ == "__main__":
    main()
