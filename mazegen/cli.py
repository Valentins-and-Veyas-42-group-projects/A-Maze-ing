from enum import Enum
import random
from collections import deque


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
delta_to_direction = {v: k for k, v in Direction_Deltas.items()}

direction_to_letter = {
    Direction.NORTH: "N",
    Direction.EAST: "E",
    Direction.SOUTH: "S",
    Direction.WEST: "W",
}


class MazeGenerator:
    """Generate a perfect maze on a grid using randomized DFS.

    Each cell is a 4-bit value where set bits mark intact walls in
    the order NORTH, EAST, SOUTH, WEST.
    """

    def __init__(self, width: int, height: int, entry: tuple[int, int],
                 exit: tuple[int, int]) -> None:
        """Initialize the generator with dimensions and endpoints."""
        self.width = width
        self.height = height
        self.grid: list[list[int]] = []
        self.entry = entry
        self.exits = exit

    @staticmethod
    def _is_inbounds(x: int, y: int, width: int, height: int) -> bool:
        """Return True if (x, y) lies within the grid bounds."""
        if 0 <= x < width and 0 <= y < height:
            return True
        else:
            return False

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
        self._validate_entry_exit()
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

    def _validate_entry_exit(self) -> None:
        """Validate that entry and exit are distinct in-bounds cells."""
        if not self._is_inbounds(*self.entry, self.width, self.height):
            raise ValueError(f"entry {self.entry} out of bounds")
        if not self._is_inbounds(*self.exits, self.width, self.height):
            raise ValueError(f"exit {self.exits} out of bounds")
        if self.entry == self.exits:
            raise ValueError("entry and exit must differ")

    def wall_helper(self, x: int, y: int,
                    direction: Direction) -> None:
        """Remove the wall between cell (x, y) and its neighbor."""
        self.grid[y][x] &= ~(1 << direction.value)
        (dx, dy) = Direction_Deltas[direction]
        x += dx
        y += dy
        self.grid[y][x] &= ~(1 << (direction.value + 2) % 4)

    def solver(self) -> str:
        (x, y) = self.entry
        array_visited = [[False for _ in range(
            self.width)]for _ in range(self.height)]
        came_from: dict[tuple[int, int], tuple[int, int]] = {}
        array_visited[y][x] = True
        queue: deque[tuple[int, int]] = deque()
        queue.append(self.entry)
        directions = []
        while queue:
            (x, y) = queue.popleft()
            if (x, y) == self.exits:
                path = []
                current = self.exits
                while current != self.entry:
                    path.append(current)
                    current = came_from[current]
                path.append(self.entry)
                path.reverse()
                for (px, py), (cx, cy) in zip(path, path[1:]):
                    delta = (cx - px, cy - py)
                    directions.append(delta_to_direction[delta])
                return "".join(direction_to_letter[d] for d in directions)
            for direction in Direction:
                (dx, dy) = Direction_Deltas[direction]
                nx = x+dx
                ny = y+dy
                if (self._is_inbounds(nx, ny, self.width, self.height)
                    and not (self.grid[y][x] & (1 << direction.value))
                        and not array_visited[ny][nx]):
                    array_visited[ny][nx] = True
                    came_from[(nx, ny)] = (x, y)
                    queue.append((nx, ny))
        return "".join(direction_to_letter[d] for d in directions)


def path_to_cells(path: str, entry: tuple[int, int]) -> set[tuple[int, int]]:
    letter_to_direction = {v: k for k, v in direction_to_letter.items()}
    cells = set()
    x, y = entry
    cells.add((x, y))
    for letter in path:
        direction = letter_to_direction[letter]
        dx, dy = Direction_Deltas[direction]
        x += dx
        y += dy
        cells.add((x, y))
    return cells


def visualize(grid: list[list[int]],
              path: set[tuple[int, int]] | None = None,
              entry: tuple[int, int] | None = None,
              exits: tuple[int, int] | None = None) -> None:
    """CLAUDE FUNCTION TO BE REPLACED"""
    path = path or set()
    rows = len(grid)
    cols = len(grid[0])
    wall = "\033[48;2;245;245;245m  \033[0m"
    opening = "\033[48;2;10;10;10m  \033[0m"
    on_path = "\033[48;2;255;200;0m  \033[0m"
    entry_c = "\033[48;2;0;220;120m  \033[0m"
    exit_c = "\033[48;2;230;30;30m  \033[0m"
    h = 2 * rows + 1
    w = 2 * cols + 1
    canvas = [[wall for _ in range(w)] for _ in range(h)]
    for y in range(rows):
        for x in range(cols):
            cell = grid[y][x]
            cx = 2 * x + 1
            cy = 2 * y + 1
            if (x, y) == entry:
                canvas[cy][cx] = entry_c
            elif (x, y) == exits:
                canvas[cy][cx] = exit_c
            elif (x, y) in path:
                canvas[cy][cx] = on_path
            else:
                canvas[cy][cx] = opening
            here = (x, y) in path
            neighbors = [
                (1, cy - 1, cx, (x, y - 1)),
                (2, cy, cx + 1, (x + 1, y)),
                (4, cy + 1, cx, (x, y + 1)),
                (8, cy, cx - 1, (x - 1, y)),
            ]
            for bit, wy, wx, other in neighbors:
                if cell & bit:
                    continue
                linked = here and other in path
                canvas[wy][wx] = on_path if linked else opening
    for row in canvas:
        print("".join(row))


if __name__ == "__main__":
    width = int(input("Enter width: "))
    height = int(input("Enter height: "))
    entry = (random.randint(0, width-1), random.randint(0, height-1,))
    exit = (random.randint(0, width-1), random.randint(0, height-1,))
    mazegen = MazeGenerator(
        width, height, entry, exit)
    print(mazegen.entry, mazegen.exits)
    mazegen.generate()
    path = mazegen.solver()
    visualize(mazegen.grid, path_to_cells(path, mazegen.entry),
              mazegen.entry, mazegen.exits)
    print(path)


def main() -> None:
    """Entry point placeholder."""
    pass
