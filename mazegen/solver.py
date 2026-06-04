"""Maze solving and path conversion."""

from collections import deque
from collections.abc import Callable

from .errors import Err, MazeError, Ok
from .shared import (
    DELTA_TO_DIRECTION,
    DIRECTION_DELTAS,
    DIRECTION_TO_LETTER,
    LETTER_TO_DIRECTION,
    Cell,
    Direction,
    Edge,
    Grid,
    is_inbounds,
)


def solve(
    grid: Grid,
    entry: Cell,
    exits: Cell,
    on_step: Callable[[set[Cell], set[Cell]], None] | None = None,
) -> Ok[str] | Err[MazeError]:
    """Solve the maze with BFS and return directions as a string."""

    width = len(grid[0]) if grid else 0
    height = len(grid)
    x, y = entry

    if not is_inbounds(x, y, width, height):
        return Err(MazeError.INVALID_ENTRY)
    exit_x, exit_y = exits
    if not is_inbounds(exit_x, exit_y, width, height):
        return Err(MazeError.INVALID_EXIT)

    visited = [[False for _ in range(width)] for _ in range(height)]
    visited_set: set[Cell] = {entry}
    came_from: dict[Cell, Cell] = {}
    queue: deque[Cell] = deque([entry])
    visited[y][x] = True

    while queue:
        x, y = queue.popleft()
        if (x, y) == exits:
            return Ok(_path_to_directions(came_from, entry, exits))

        for direction in Direction:
            dx, dy = DIRECTION_DELTAS[direction]
            nx = x + dx
            ny = y + dy

            if not is_inbounds(nx, ny, width, height):
                continue
            if grid[y][x] & (1 << direction.value):
                continue
            if visited[ny][nx]:
                continue

            visited[ny][nx] = True
            visited_set.add((nx, ny))
            came_from[(nx, ny)] = (x, y)
            queue.append((nx, ny))

        if on_step is not None:
            on_step(visited_set, set(queue))

    return Err(MazeError.NO_PATH_FOUND)


def path_to_edges(path: str, entry: Cell) -> tuple[set[Cell], set[Edge]]:
    """Convert direction string into traversed cells and edges."""

    cells: set[Cell] = set()
    edges: set[Edge] = set()
    x, y = entry
    cells.add((x, y))

    for letter in path:
        direction = LETTER_TO_DIRECTION[letter]
        dx, dy = DIRECTION_DELTAS[direction]
        nx = x + dx
        ny = y + dy

        cells.add((nx, ny))
        edges.add(((x, y), (nx, ny)))
        edges.add(((nx, ny), (x, y)))
        x, y = nx, ny

    return cells, edges


def validate_path(grid: Grid, path: str,
                  entry: Cell, exits: Cell) -> Ok[None] | Err[MazeError]:
    """Validate that a direction string
      reaches exits without crossing walls."""

    width = len(grid[0]) if grid else 0
    height = len(grid)
    x, y = entry

    if not is_inbounds(x, y, width, height):
        return Err(MazeError.INVALID_ENTRY)

    exit_x, exit_y = exits
    if not is_inbounds(exit_x, exit_y, width, height):
        return Err(MazeError.INVALID_EXIT)

    for letter in path:
        direction = LETTER_TO_DIRECTION.get(letter)
        if direction is None:
            return Err(MazeError.INVALID_PATH)

        if grid[y][x] & (1 << direction.value):
            return Err(MazeError.INVALID_PATH)

        dx, dy = DIRECTION_DELTAS[direction]
        x += dx
        y += dy

        if not is_inbounds(x, y, width, height):
            return Err(MazeError.INVALID_PATH)

    if (x, y) != exits:
        return Err(MazeError.INVALID_PATH)

    return Ok(None)


def _path_to_directions(
    came_from: dict[Cell, Cell],
    entry: Cell,
    exits: Cell,
) -> str:
    """Reconstruct the BFS came_from chain into a direction string."""

    path: list[Cell] = []
    current = exits

    while current != entry:
        path.append(current)
        current = came_from[current]

    path.append(entry)
    path.reverse()

    directions: list[Direction] = []
    for (px, py), (cx, cy) in zip(path, path[1:], strict=False):
        delta = (cx - px, cy - py)
        directions.append(DELTA_TO_DIRECTION[delta])

    return "".join(DIRECTION_TO_LETTER[direction] for direction in directions)
