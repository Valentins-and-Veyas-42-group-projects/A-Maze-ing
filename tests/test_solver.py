"""Solver correctness tests."""

import random
from typing import cast

from mazegen import Err, MazeGenerator, Ok, solve, validate_path
from mazegen.solver import path_to_edges, solve_dfs


def test_solver_path_is_valid_for_generated_maze() -> None:
    random.seed(1)
    maze = MazeGenerator(20, 20, (16, 6), (18, 12), False)

    assert not isinstance(maze.generate(), Err)

    result = solve(maze.grid, maze.entry, maze.exits)
    assert isinstance(result, Ok)
    path = cast(str, result.value)

    assert not isinstance(
        validate_path(maze.grid, path, maze.entry, maze.exits), Err
    )


def test_solver_dfs_path_is_valid_for_generated_maze() -> None:
    random.seed(1)
    maze = MazeGenerator(20, 20, (16, 6), (18, 12), False)

    assert not isinstance(maze.generate(), Err)

    result = solve_dfs(maze.grid, maze.entry, maze.exits)
    assert isinstance(result, Ok)
    path = cast(str, result.value)

    assert not isinstance(
        validate_path(maze.grid, path, maze.entry, maze.exits), Err
    )


def test_solver_returns_error_when_no_path_exists() -> None:
    grid = [[15, 15], [15, 15]]
    entry = (0, 0)
    exits = (1, 1)

    result = solve(grid, entry, exits)
    assert isinstance(result, Err)
    from mazegen.errors import MazeError

    assert result.error == MazeError.NO_PATH_FOUND


def test_validate_path_fails_for_invalid_moves() -> None:
    grid = [[15, 15], [15, 15]]
    entry = (0, 0)
    exits = (1, 1)

    assert isinstance(validate_path(grid, "E", entry, (1, 0)), Err)
    assert isinstance(validate_path(grid, "N", entry, (0, -1)), Err)
    assert isinstance(validate_path(grid, "", entry, exits), Err)


def test_path_to_edges_converts_correctly() -> None:
    entry = (0, 0)
    path = "ES"

    cells, edges = path_to_edges(path, entry)

    assert cells == {(0, 0), (1, 0), (1, 1)}
    assert edges == {
        ((0, 0), (1, 0)),
        ((1, 0), (0, 0)),
        ((1, 0), (1, 1)),
        ((1, 1), (1, 0)),
    }


def test_solve_with_on_step_callback() -> None:
    from mazegen.shared import Cell

    grid = [[15, 15], [15, 15]]
    grid[0][0] &= ~2
    grid[0][1] &= ~8
    entry = (0, 0)
    exits = (1, 0)

    steps = []

    def on_step(visited: set[Cell], queue: set[Cell]) -> None:
        steps.append((set(visited), set(queue)))

    solve(grid, entry, exits, on_step=on_step)

    assert len(steps) > 0
    # First step should have entry in visited
    assert (0, 0) in steps[0][0]
