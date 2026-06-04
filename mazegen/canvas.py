"""Maze canvas building — pure cell-to-color mapping, no curses."""

from .shared import Cell, Edge, Grid, DIRECTION_DELTAS

WALL = 1
OPEN = 2
PATH = 3
ENTRY = 4
EXIT = 5
LOGO = 6
LOGO_BORDER = 7
CURSOR = 8
VISITED = 9
FRONTIER = 10

PALETTE: dict[int, tuple[int, int, int]] = {
    WALL: (168, 50, 78),
    OPEN: (18, 18, 22),
    PATH: (255, 150, 230),
    ENTRY: (0, 220, 120),
    EXIT: (235, 40, 40),
    LOGO: (150, 40, 220),
    LOGO_BORDER: (80, 20, 120),
    CURSOR: (46, 199, 38),
    VISITED: (25, 55, 120),
    FRONTIER: (50, 200, 245),
}


def rgb_to_curses(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    """Convert 8-bit RGB to the 0–1000 range curses expects."""
    r, g, b = rgb
    return (r * 1000 // 255, g * 1000 // 255, b * 1000 // 255)


def _draw_cell(
    canvas: list[list[int]],
    cell: int,
    x: int,
    y: int,
    path_cells: set[Cell],
    path_edges: set[Edge],
    entry: Cell | None,
    exits: Cell | None,
    logo_cells: set[Cell],
    animation: bool = False,
    visited_cells: set[Cell] | None = None,
    frontier_cells: set[Cell] | None = None,
) -> None:
    """Paint one cell and its open walls onto the canvas.

    Assigns a color ID to the cell slot and any open wall slots based
    on the cell's role: entry/exit marker, path, logo, animation state
    (frontier/visited), or plain open space. Cells with all walls intact
    (value 15) are skipped during generation animation.
    """
    _visited = visited_cells if visited_cells is not None else set()
    _frontier = frontier_cells if frontier_cells is not None else set()

    cx = 2 * x + 1
    cy = 2 * y + 1
    if animation and cell == 15 and (x, y) not in (entry, exits):
        return
    if (x, y) == entry:
        canvas[cy][cx] = ENTRY
    elif (x, y) == exits:
        canvas[cy][cx] = EXIT
    elif _frontier and (x, y) in _frontier:
        canvas[cy][cx] = FRONTIER
    elif _visited and (x, y) in _visited:
        canvas[cy][cx] = VISITED
    elif (x, y) in logo_cells:
        canvas[cy][cx] = LOGO
    elif (x, y) in path_cells:
        canvas[cy][cx] = PATH
    else:
        canvas[cy][cx] = OPEN

    for direction, (dx, dy) in DIRECTION_DELTAS.items():
        if cell & (1 << direction.value):
            continue

        wx = cx + dx
        wy = cy + dy
        neighbor = (x + dx, y + dy)

        if ((x, y), neighbor) in path_edges:
            canvas[wy][wx] = PATH
        elif (x, y) in _frontier or neighbor in _frontier:
            canvas[wy][wx] = FRONTIER
        elif (x, y) in _visited and neighbor in _visited:
            canvas[wy][wx] = VISITED
        else:
            canvas[wy][wx] = OPEN


def _fill_pillars(
    canvas: list[list[int]], rows: int, cols: int, wall: int
) -> None:
    """Fill wall-junction pillars based on their four neighboring slots.

    A pillar at position (2x+2, 2y+2) sits at the corner between four
    cells. If none of its neighbors are walls it inherits the color of
    surrounding open slots, preferring PATH > VISITED > OPEN.
    """
    for y in range(rows - 1):
        for x in range(cols - 1):
            px = 2 * x + 2
            py = 2 * y + 2
            slots = (
                canvas[py - 1][px],
                canvas[py + 1][px],
                canvas[py][px - 1],
                canvas[py][px + 1],
            )
            if any(s == wall for s in slots):
                continue
            if all(s == PATH for s in slots):
                canvas[py][px] = PATH
            elif all(s in (VISITED, PATH) for s in slots):
                canvas[py][px] = VISITED
            else:
                canvas[py][px] = OPEN


def _draw_logo_border(
    canvas: list[list[int]], logo_cells: set[Cell], wall: int
) -> None:
    """Recolor wall slots adjacent to logo cells with the border shade."""
    height = len(canvas)
    width = len(canvas[0]) if canvas else 0
    for (x, y) in logo_cells:
        cx = 2 * x + 1
        cy = 2 * y + 1
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                if ox == 0 and oy == 0:
                    continue
                wx = cx + ox
                wy = cy + oy
                if 0 <= wy < height and 0 <= wx < width:
                    if canvas[wy][wx] == wall:
                        canvas[wy][wx] = LOGO_BORDER


def build_canvas(
    grid: Grid,
    entry: Cell,
    exits: Cell,
    logo_cells: set[Cell] | None = None,
    cursor: Cell | None = None,
    path_cells: set[Cell] | None = None,
    path_edges: set[Edge] | None = None,
    animating: bool = False,
    visited_cells: set[Cell] | None = None,
    frontier_cells: set[Cell] | None = None,
) -> list[list[int]]:
    """Build a 2D color-ID canvas from the maze grid state.

    Each grid cell maps to a 2×2 block on the canvas with interleaved
    wall slots, producing a canvas of size (2*rows+1) × (2*cols+1).
    Every element holds a color ID constant (WALL, OPEN, PATH, etc.)
    ready to be passed to blit().
    """
    rows = len(grid)
    cols = len(grid[0])
    canvas_height = 2 * rows + 1
    canvas_width = 2 * cols + 1
    _path_cells = path_cells or set()
    _path_edges = path_edges or set()
    _logo_cells = logo_cells or set()

    canvas: list[list[int]] = [
        [WALL for _ in range(canvas_width)] for _ in range(canvas_height)
    ]
    for y in range(rows):
        for x in range(cols):
            _draw_cell(
                canvas, grid[y][x], x, y,
                _path_cells, _path_edges, entry, exits,
                _logo_cells, animating, visited_cells, frontier_cells,
            )
    _fill_pillars(canvas, rows, cols, WALL)
    _draw_logo_border(canvas, _logo_cells, WALL)
    if cursor is not None:
        cx, cy = cursor
        if 0 <= cy < rows and 0 <= cx < cols:
            canvas[2 * cy + 1][2 * cx + 1] = CURSOR
    return canvas
