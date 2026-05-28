"""Maze generation."""

import random

from .errors import Err, MazeError, Ok
from .shared import (
    DIRECTION_DELTAS,
    Cell,
    Direction,
    Grid,
    is_inbounds,
)

PATTERN_SMALL = [
    # 4
    (0, 0),         (2, 0),
    (0, 1),         (2, 1),
    (0, 2), (1, 2), (2, 2),
    (2, 3),
    (2, 4),
    # 2
    (4, 0), (5, 0), (6, 0),
    (6, 1),
    (4, 2), (5, 2), (6, 2),
    (4, 3),
    (4, 4), (5, 4), (6, 4),
]


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
        perfect: bool,
    ) -> None:
        """Initialize the generator with dimensions and endpoints."""

        self.width = width
        self.height = height
        self.grid: Grid = []
        self.entry = entry
        self.exits = exit
        self.perfect = perfect
        self.logo_cells: list[Cell] = []

    def init_grid(self) -> Grid:
        """Build a grid with all walls intact and return it."""

        self.grid = [[15 for _ in range(self.width)]
                     for _ in range(self.height)]
        return self.grid

    def _no_wall(self, x: int, y: int, direction: Direction) -> bool:
        if self.grid[y][x] & (1 << direction.value) == 0:
            return True
        return False

    def _is_open_square(self, top_leftx: int, top_lefty: int) -> bool:
        tlx, tly = top_leftx, top_lefty
        if not is_inbounds(tlx, tly, self.width, self.height):
            return False
        if not is_inbounds(tlx + 2, tly + 2, self.width, self.height):
            return False
        for dy in range(3):
            for dx in range(2):
                if not self._no_wall(tlx + dx, tly + dy, Direction.EAST):
                    return False
        for dy in range(2):
            for dx in range(3):
                if not self._no_wall(tlx + dx, tly + dy, Direction.SOUTH):
                    return False
        return True

    def would_make_open_sqr(self, x: int, y: int,
                            direction: Direction) -> bool:
        result = False
        self.remove_wall(x, y, direction)
        if direction == Direction.EAST:
            for tlx in (x - 1, x):
                for tly in (y - 2, y - 1, y):
                    if self._is_open_square(tlx, tly):
                        result = True
        elif direction == Direction.SOUTH:
            for tlx in (x - 2, x - 1, x):
                for tly in (y - 1, y):
                    if self._is_open_square(tlx, tly):
                        result = True
        self.add_wall(x, y, direction)
        return result

    def add_loops(self) -> None:
        logo = set(self.logo_cells)
        candidates = []
        for y in range(self.height):
            for x in range(self.width):
                if x+1 < self.width and not (
                    (x, y) in logo or (x + 1, y) in logo
                ):
                    candidates.append((x, y, Direction.EAST))
                if y+1 < self.height and not (
                    (x, y) in logo or (x, y + 1) in logo
                ):
                    candidates.append((x, y, Direction.SOUTH))
        count: int = round(len(candidates)*0.25)
        samples = random.sample(candidates, count)
        for (xx, yy, direction) in samples:
            if not self.would_make_open_sqr(xx, yy, direction):
                self.remove_wall(xx, yy, direction)

    def generate(self) -> Ok[None] | Err:
        """Carve the maze in place via iterative randomized DFS."""

        check = self._validate()
        if isinstance(check, Err):
            return check

        visited = [[False for _ in range(self.width)]
                   for _ in range(self.height)]
        self.init_grid()
        ox = (self.width - 7) // 2
        oy = (self.height - 5) // 2
        potential_cells = [(ox + dx, oy + dy) for (dx, dy) in PATTERN_SMALL]

        if (self.width > 8 and self.height > 6
            and self.entry not in potential_cells
                and self.exits not in potential_cells):
            self.logo_cells = self.add_42()
        elif self.width <= 8 and self.height <= 6:
            print("Maze too small for logo")
        elif (self.entry in potential_cells
                or self.exits in potential_cells):
            print("Entry/Exit would be in Logo")
        stack: list[tuple[int, int]] = [self.entry]
        visited[self.entry[1]][self.entry[0]] = True
        while stack:
            x, y = stack[-1]
            candidates: list[tuple[Direction, int, int]] = []

            for direction in Direction:
                dx, dy = DIRECTION_DELTAS[direction]
                nx = x + dx
                ny = y + dy
                if (is_inbounds(nx, ny, self.width, self.height)
                        and not visited[ny][nx]
                        and (nx, ny)not in self.logo_cells):
                    candidates.append((direction, nx, ny))

            if candidates:
                direction, nx, ny = random.choice(candidates)
                self.remove_wall(x, y, direction)
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()
        if not self.perfect:
            self.add_loops()

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

    def add_42(self) -> list[tuple[int, int]]:
        ox = (self.width - 7) // 2
        oy = (self.height - 5) // 2
        cells = []
        for (dx, dy) in PATTERN_SMALL:
            self.grid[oy + dy][ox + dx] = 15
            cells.append((ox + dx, oy + dy))
        return cells

    def remove_wall(self, x: int, y: int, direction: Direction) -> None:
        """Remove the wall between cell (x, y) and its neighbor."""

        self.grid[y][x] &= ~(1 << direction.value)

        dx, dy = DIRECTION_DELTAS[direction]
        nx = x + dx
        ny = y + dy
        opposite = (direction.value + 2) % 4

        self.grid[ny][nx] &= ~(1 << opposite)

    def add_wall(self, x: int, y: int, direction: Direction) -> None:
        """Add the wall between cell (x, y) and its neighbor."""
        self.grid[y][x] |= (1 << direction.value)
        dx, dy = DIRECTION_DELTAS[direction]
        nx = x + dx
        ny = y + dy
        opposite = (direction.value + 2) % 4
        self.grid[ny][nx] |= (1 << opposite)

    def solver(self) -> Ok[str] | Err:
        """Solve this maze and return directions from entry to exit."""

        from .solver import solve

        return solve(self.grid, self.entry, self.exits)

    def output(self) -> str | Err:
        """Format this maze as the project output file format."""

        from .output import format_output

        return format_output(self.grid, self.entry, self.exits)
