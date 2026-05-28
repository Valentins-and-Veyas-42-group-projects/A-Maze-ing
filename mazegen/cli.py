from enum import Enum
import random


class Direction(Enum):
    """Cardinal directions encoded as bit positions for cell walls."""

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


Direction_Deltas = {
    Direction.NORTH: (0, -1),
    Direction.EAST: (1, 0),
    Direction.SOUTH: (0, 1),
    Direction.WEST: (-1, 0),
}


class MazeGenerator:
    """Generate a perfect maze on a grid using randomized DFS.

    Each cell is a 4-bit value where set bits mark intact walls in
    the order NORTH, EAST, SOUTH, WEST.
    """

    @staticmethod
    def _is_inbounds(x: int, y: int, width: int, height: int) -> bool:
        """Return True if (x, y) lies within the grid bounds."""
        if 0 <= x < width and 0 <= y < height:
            return True
        else:
            return False

    def __init__(self, width: int, height: int, entry: tuple[int, int],
                 exit: tuple[int, int]) -> None:
        """Initialize the generator with dimensions and endpoints."""
        self.width = width
        self.height = height
        self.grid: list[list[int]] = []
        self.entry = entry
        self.exits = exit

    def init_grid(self) -> list[list[int]]:
        """Build a grid with all walls intact and return it."""
        columns = self.width
        rows = self.height
        self.grid = [[15 for _ in range(columns)]for _ in range(rows)]
        return self.grid

    def generate(self) -> None:
        """Carve the maze in place via iterative randomized DFS."""
        array_visited = [[False for _ in range(
            self.width)]for _ in range(self.height)]
        self.init_grid()
        self._setup_entry_exit()
        stack = []
        array_visited[0][0] = True
        stack.append((0, 0))
        while stack:
            (x, y) = stack[-1]
            candidates = []
            for direction in Direction:
                (dx, dy) = Direction_Deltas[direction]
                nx = x+dx
                ny = y+dy
                if (self._is_inbounds(nx, ny, self.width, self.height) and not
                        array_visited[ny][nx]):
                    candidates.append((direction, nx, ny))
            if candidates:
                (direction, nx, ny) = random.choice(candidates)
                self.wall_helper(x, y, direction)
                array_visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()

    def _setup_entry_exit(self) -> None:
        """Open the boundary walls at the entry and exit cells."""
        (enx, eny) = self.entry
        (exx, exy) = self.exits
        if (self._is_inbounds(*self.entry, self.width, self.height) and
            self._is_inbounds(*self.exits, self.width, self.height) and
                self.entry != self.exits):
            match (enx == 0, enx == self.width - 1, eny == 0,
                    eny == self.height - 1):
                case (_, _, True, _):
                    self.grid[eny][enx] &= ~(1 << 0)
                case (_, _, _, True):
                    self.grid[eny][enx] &= ~(1 << 2)
                case (True, _, _, _):
                    self.grid[eny][enx] &= ~(1 << 3)
                case (_, True, _, _):
                    self.grid[eny][enx] &= ~(1 << 1)
                case(False, False, False, False):
                    pass  # ERROR HANDLING!!!
            match (exx == 0, exx == self.width - 1, exy == 0,
                    exy == self.height - 1):
                case (_, _, True, _):
                    self.grid[exy][exx] &= ~(1 << 0)
                case (_, _, _, True):
                    self.grid[exy][exx] &= ~(1 << 2)
                case (True, _, _, _):
                    self.grid[exy][exx] &= ~(1 << 3)
                case (_, True, _, _):
                    self.grid[exy][exx] &= ~(1 << 1)
                case(False, False, False, False):
                    pass  # ERROR HANDLING!!!

    def wall_helper(self, x: int, y: int,
                    direction: Direction) -> None:
        """Remove the wall between cell (x, y) and its neighbor."""
        self.grid[y][x] &= ~(1 << direction.value)
        (dx, dy) = Direction_Deltas[direction]
        x += dx
        y += dy
        self.grid[y][x] &= ~(1 << (direction.value + 2) % 4)


def visualize(grid: list[list[int]]) -> None:
    """Print an ASCII rendering of the maze grid to stdout."""
    rows = len(grid)
    cols = len(grid[0])
    for y in range(rows):
        top = ""
        middle = ""
        for x in range(cols):
            cell = grid[y][x]
            north = cell & 1
            west = cell & 8
            top += "+" + ("---" if north else "   ")
            middle += ("|" if west else " ") + "   "
        print(top + "+")
        print(middle + "|")
    bottom = ""
    for x in range(cols):
        cell = grid[rows - 1][x]
        south = cell & 4
        bottom += "+" + ("---" if south else "   ")
    print(bottom + "+")


if __name__ == "__main__":
    width = int(input("Enter width: "))
    height = int(input("Enter height: "))
    mazegen = MazeGenerator(width, height, (0, 0), (5, height-1))
    mazegen.generate()
    visualize(mazegen.grid)


def main() -> None:
    """Entry point placeholder."""
    pass
