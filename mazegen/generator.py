"""Maze generation."""

import random
from collections.abc import Callable

from .errors import Err, MazeError, Ok
from .patterns import Pattern, select_pattern
from .shared import (
    DIRECTION_DELTAS,
    Cell,
    Direction,
    Grid,
    is_inbounds,
)


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
        self.cursor: Cell | None = None

    def init_grid(self, value: int) -> Grid:
        """Build a grid with all walls intact and return it."""

        self.grid = [[value for _ in range(self.width)]
                     for _ in range(self.height)]
        return self.grid

    def _no_wall(self, x: int, y: int, direction: Direction) -> bool:
        """Return True if (x, y) has no wall on the given side."""

        if self.grid[y][x] & (1 << direction.value) == 0:
            return True
        return False

    def _is_open_square(self, top_leftx: int, top_lefty: int) -> bool:
        """Return True if the 3x3 block at the corner has no inner walls."""

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
        """Return True if removing this wall opens a 3x3 block."""

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
        """Carve extra passages to add loops, skipping logo cells."""

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

    def bin_tree(self,
                 on_step: Callable[[], None] | None = None) -> Ok[None] | Err:
        """Carve the maze with the binary tree algorithm.

        Each cell removes either its north or east wall, biasing the
        maze toward a top-right corridor texture.
        """

        check = self._validate()
        if isinstance(check, Err):
            return check

        self.init_grid(15)
        pattern = select_pattern(self.width, self.height)
        logo_cells = pattern.placed_cells(self.width, self.height)

        if not pattern.fits(self.width, self.height):
            print("Maze too small for logo")
        elif self.entry in logo_cells or self.exits in logo_cells:
            print("Entry/Exit would be in Logo")
        else:
            self.logo_cells = self.add_42(pattern)
        logo = set(self.logo_cells)

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in logo:
                    continue
                options: list[Direction] = []
                for direction in (Direction.NORTH, Direction.EAST):
                    dx, dy = DIRECTION_DELTAS[direction]
                    nx, ny = x + dx, y + dy
                    if (is_inbounds(nx, ny, self.width, self.height)
                            and (nx, ny) not in logo):
                        options.append(direction)
                if options:
                    self.remove_wall(x, y, random.choice(options))
                    self.cursor = (x, y)
                    if on_step:
                        on_step()

        if not self.perfect:
            self.add_loops()

        return Ok(None)

    def generate(self,
                 on_step: Callable[[], None] | None = None) -> Ok[None] | Err:
        """Carve the maze in place via iterative randomized DFS."""

        check = self._validate()
        if isinstance(check, Err):
            return check

        visited = [[False for _ in range(self.width)]
                   for _ in range(self.height)]
        self.init_grid(15)
        pattern = select_pattern(self.width, self.height)
        logo_cells = pattern.placed_cells(self.width, self.height)

        if not pattern.fits(self.width, self.height):
            print("Maze too small for logo")
        elif self.entry in logo_cells or self.exits in logo_cells:
            print("Entry/Exit would be in Logo")
        else:
            self.logo_cells = self.add_42(pattern)
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
                self.cursor = (nx, ny)
                if on_step:
                    on_step()
            else:
                stack.pop()
        if not self.perfect:
            self.add_loops()

        return Ok(None)

    def prims_algorithm(
            self,
            on_step: Callable[[], None] | None = None) -> Ok[None] | Err:
        check = self._validate()
        if isinstance(check, Err):
            return check

        visited = [[False for _ in range(self.width)]
                   for _ in range(self.height)]
        self.init_grid(15)
        pattern = select_pattern(self.width, self.height)
        logo_cells = pattern.placed_cells(self.width, self.height)

        if not pattern.fits(self.width, self.height):
            print("Maze too small for logo")
        elif self.entry in logo_cells or self.exits in logo_cells:
            print("Entry/Exit would be in Logo")
        else:
            self.logo_cells = self.add_42(pattern)
        visited[self.entry[1]][self.entry[0]] = True
        frontier: list[tuple[int, int]] = []
        x, y = self.entry
        for direction in Direction:
            dx, dy = DIRECTION_DELTAS[direction]
            nx = x + dx
            ny = y + dy
            if (is_inbounds(nx, ny, self.width, self.height)
                    and not visited[ny][nx]
                    and (nx, ny)not in self.logo_cells):
                frontier.append((nx, ny))
        while frontier:
            visited_neighbors = []
            new_frontier = []
            i = random.randrange(len(frontier))
            frontier[i], frontier[-1] = frontier[-1], frontier[i]
            fx, fy = frontier.pop()
            if visited[fy][fx]:
                continue
            visited[fy][fx] = True
            for direction in Direction:
                dx, dy = DIRECTION_DELTAS[direction]
                nx = fx + dx
                ny = fy + dy
                if not (is_inbounds(nx, ny, self.width, self.height)
                        and (nx, ny) not in self.logo_cells):
                    continue
                if visited[ny][nx]:
                    visited_neighbors.append((direction, nx, ny))
                else:
                    new_frontier.append((nx, ny))
            if visited_neighbors:
                direction, nx, ny = random.choice(visited_neighbors)
                self.remove_wall(fx, fy, direction)
                frontier.extend(new_frontier)
                self.cursor = (fx, fy)
                if on_step:
                    on_step()
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

    def add_42(self, pattern: Pattern) -> list[Cell]:
        """Stamp the logo into the grid and return its cells."""

        cells = pattern.placed_cells(self.width, self.height)
        for (x, y) in cells:
            self.grid[y][x] = 15
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
