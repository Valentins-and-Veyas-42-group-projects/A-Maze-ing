"""Maze generator tests."""

import random

from mazegen import Err, MazeGenerator, Ok
from mazegen.errors import MazeError
from mazegen.shared import Direction


def test_maze_generator_validation() -> None:
    # Invalid width
    maze = MazeGenerator(0, 10, (0, 0), (9, 9), True)
    res = maze.generate()
    assert isinstance(res, Err)
    assert res.error == MazeError.INVALID_WIDTH

    # Invalid height
    maze = MazeGenerator(10, 0, (0, 0), (9, 9), True)
    res = maze.generate()
    assert isinstance(res, Err)
    assert res.error == MazeError.INVALID_HEIGHT

    # Invalid entry
    maze = MazeGenerator(10, 10, (-1, 0), (9, 9), True)
    res = maze.generate()
    assert isinstance(res, Err)
    assert res.error == MazeError.INVALID_ENTRY

    # Invalid exit
    maze = MazeGenerator(10, 10, (0, 0), (10, 10), True)
    res = maze.generate()
    assert isinstance(res, Err)
    assert res.error == MazeError.INVALID_EXIT

    # Entry and exit same
    maze = MazeGenerator(10, 10, (5, 5), (5, 5), True)
    res = maze.generate()
    assert isinstance(res, Err)
    assert res.error == MazeError.ENTRY_EXIT_SAME


def test_maze_generator_init_grid() -> None:
    maze = MazeGenerator(5, 5, (0, 0), (4, 4), True)
    grid = maze.init_grid(15)
    assert len(grid) == 5
    assert len(grid[0]) == 5
    for row in grid:
        for cell in row:
            assert cell == 15


def test_maze_generator_remove_wall() -> None:
    maze = MazeGenerator(2, 2, (0, 0), (1, 1), True)
    maze.init_grid(15)

    # Remove wall between (0,0) and (1,0) - EAST
    maze.remove_wall(0, 0, Direction.EAST)
    assert maze.grid[0][0] & (1 << Direction.EAST.value) == 0
    assert maze.grid[0][1] & (1 << Direction.WEST.value) == 0


def test_maze_generator_add_wall() -> None:
    maze = MazeGenerator(2, 2, (0, 0), (1, 1), True)
    maze.init_grid(0)

    # Add wall between (0,0) and (0,1) - SOUTH
    maze.add_wall(0, 0, Direction.SOUTH)
    assert maze.grid[0][0] & (1 << Direction.SOUTH.value) != 0
    assert maze.grid[1][0] & (1 << Direction.NORTH.value) != 0


def test_dfs_generation_creates_reachable_maze() -> None:
    random.seed(42)
    maze = MazeGenerator(10, 10, (0, 0), (9, 9), True)
    assert isinstance(maze.generate(), Ok)

    # Use solver to verify reachability
    from mazegen.solver import solve

    assert isinstance(solve(maze.grid, maze.entry, maze.exits), Ok)


def test_bin_tree_generation_creates_reachable_maze() -> None:
    random.seed(42)
    maze = MazeGenerator(10, 10, (0, 0), (9, 9), True)
    assert isinstance(maze.bin_tree(), Ok)

    from mazegen.solver import solve

    assert isinstance(solve(maze.grid, maze.entry, maze.exits), Ok)


def test_prims_algorithm_creates_reachable_maze() -> None:
    random.seed(42)
    maze = MazeGenerator(10, 10, (0, 0), (9, 9), True)
    assert isinstance(maze.prims_algorithm(), Ok)

    from mazegen.solver import solve

    assert isinstance(solve(maze.grid, maze.entry, maze.exits), Ok)


def test_non_perfect_maze_adds_loops() -> None:
    random.seed(42)
    maze = MazeGenerator(5, 5, (0, 0), (4, 4), False)
    maze.generate()

    # Count open walls
    open_walls = 0
    for y in range(maze.height):
        for x in range(maze.width):
            for d in range(4):
                if not (maze.grid[y][x] & (1 << d)):
                    open_walls += 1

    perfect_maze = MazeGenerator(5, 5, (0, 0), (4, 4), True)
    random.seed(42)
    perfect_maze.generate()
    perfect_open_walls = 0
    for y in range(perfect_maze.height):
        for x in range(perfect_maze.width):
            for d in range(4):
                if not (perfect_maze.grid[y][x] & (1 << d)):
                    perfect_open_walls += 1

    assert open_walls > perfect_open_walls


def test_would_make_open_sqr() -> None:
    maze = MazeGenerator(5, 5, (0, 0), (4, 4), True)
    maze.init_grid(0)  # All walls open

    maze.init_grid(15)
    assert maze.would_make_open_sqr(0, 0, Direction.EAST) is False
