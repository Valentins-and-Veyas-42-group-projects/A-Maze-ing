"""Maze generation."""

import random

from .errors import Err, MazeError, Ok
from .shared import DIRECTION_DELTAS, Direction, Grid, is_inbounds


class MazeGenerator:
    """Generate a perfect maze on a grid using randomized DFS.

    Each cell is a 4-bit value where set bits mark intact walls in
    the order NORTH, EAST, SOUTH, WEST.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
    ) -> None:
        """Initialize the generator with dimensions and endpoints."""

        self.width = width
        self.height = height
        self.grid: Grid = []
        self.entry = entry
        self.exits = exit

    def init_grid(self) -> Grid:
        """Build a grid with all walls intact and return it."""

        self.grid = [[15 for _ in range(self.width)] for _ in range(self.height)]
        return self.grid

    def generate(self) -> Ok[None] | Err:
        """Carve the maze in place via iterative randomized DFS."""

        check = self._validate()
        if isinstance(check, Err):
            return check

        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.init_grid()

        stack: list[tuple[int, int]] = [(0, 0)]
        visited[0][0] = True

        while stack:
            x, y = stack[-1]
            candidates: list[tuple[Direction, int, int]] = []

            for direction in Direction:
                dx, dy = DIRECTION_DELTAS[direction]
                nx = x + dx
                ny = y + dy
                if is_inbounds(nx, ny, self.width, self.height) and not visited[ny][nx]:
                    candidates.append((direction, nx, ny))

            if candidates:
                direction, nx, ny = random.choice(candidates)
                self.remove_wall(x, y, direction)
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()

        return Ok(None)

    def _validate(self) -> Ok[None] | Err:
        """Validate dimensions and endpoints."""

        if self.width <= 0:
            return Err(MazeError.INVALID_WIDTH)
        if self.height <= 0:
            return Err(MazeError.INVALID_HEIGHT)
        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exits

        if not is_inbounds(entry_x, entry_y, self.width, self.height):
            return Err(MazeError.INVALID_ENTRY)
        if not is_inbounds(exit_x, exit_y, self.width, self.height):
            return Err(MazeError.INVALID_EXIT)
        if self.entry == self.exits:
            return Err(MazeError.ENTRY_EXIT_SAME)
        return Ok(None)

    def remove_wall(self, x: int, y: int, direction: Direction) -> None:
        """Remove the wall between cell (x, y) and its neighbor."""

        self.grid[y][x] &= ~(1 << direction.value)

        dx, dy = DIRECTION_DELTAS[direction]
        nx = x + dx
        ny = y + dy
        opposite = (direction.value + 2) % 4

        self.grid[ny][nx] &= ~(1 << opposite)

    def solver(self) -> Ok[str] | Err:
        """Solve this maze and return directions from entry to exit."""

        from .solver import solve

        return solve(self.grid, self.entry, self.exits)

    def output(self) -> str | Err:
        """Format this maze as the project output file format."""

        from .output import format_output

        return format_output(self.grid, self.entry, self.exits)
