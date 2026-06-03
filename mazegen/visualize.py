"""Maze visualization — to be implemented."""
import curses
from .shared import Cell, Edge, DIRECTION_DELTAS, Grid


"""Color ID's for every type of cell"""
WALL = 1
OPEN = 2
PATH = 3
ENTRY = 4
EXIT = 5
LOGO = 6
LOGO_BORDER = 7
CURSOR = 8

PALETTE = {
    WALL: (168, 50, 78),
    OPEN: (18, 18, 22),
    PATH: (255, 150, 230),
    ENTRY: (0, 220, 120),
    EXIT: (235, 40, 40),
    LOGO: (150, 40, 220),
    LOGO_BORDER: (80, 20, 120),
    CURSOR: (46, 199, 38)
}

FOOTER_SPACE = 2


def _convert_col(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    r, g, b = rgb
    return ((r*1000//255), (g*1000//255), (b*1000//255))


def setup_colors() -> None:
    curses.start_color()
    curses.use_default_colors()
    for k, v in PALETTE.items():
        conv = _convert_col(v)
        curses.init_color(k, *conv)
        curses.init_pair(k, -1, k)


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

) -> None:
    """Paint one cell and its open walls onto the canvas."""

    cx = 2 * x + 1
    cy = 2 * y + 1

    if (x, y) == entry:
        canvas[cy][cx] = ENTRY
    elif (x, y) == exits:
        canvas[cy][cx] = EXIT
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
        canvas[wy][wx] = PATH if (
            (x, y), neighbor) in path_edges else OPEN


def _fill_pillars(
    canvas: list[list[int]], rows: int, cols: int,
    wall: int
) -> None:
    """Fill wall-junction pillars based on their neighboring slots."""

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
            else:
                canvas[py][px] = OPEN


def _draw_logo_border(
    canvas: list[list[int]], logo_cells: set[Cell],
    wall: int
) -> None:
    """Recolor the wall slots around logo cells to the border shade."""

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


def build_canvas(grid: Grid,  path_cells: set[Cell],
                 path_edges: set[Edge],
                 entry: Cell,
                 exits: Cell,
                 logo_cells: set[Cell],
                 cursor: Cell) -> None:
    rows = len(grid)
    cols = len(grid[0])
    canvas_height = 2*rows+1
    canvas_width = 2*cols+1
