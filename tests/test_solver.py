"""Solver correctness tests."""

import random
from typing import cast

from mazegen import Err, MazeGenerator, Ok, solve, validate_path


def test_solver_path_is_valid_for_generated_maze() -> None:
    random.seed(1)
    maze = MazeGenerator(20, 20, (16, 6), (18, 12), False)

    assert not isinstance(maze.generate(), Err)

    result = solve(maze.grid, maze.entry, maze.exits)
    assert isinstance(result, Ok)
    path = cast(str, result.value)

    assert not isinstance(validate_path(maze.grid, path, maze.entry, maze.exits), Err)
