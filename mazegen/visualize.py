"""ANSI maze visualization."""

from .shared import DIRECTION_DELTAS, Cell, Edge, Grid

ANSI_RESET = "\033[0m"

ANSI_WALL = "\033[48;2;184;2;44m  "
ANSI_OPEN = "\033[48;2;10;10;10m  "
ANSI_PATH = "\033[48;2;255;200;255m  "
ANSI_ENTRY = "\033[48;2;0;220;120m  "
ANSI_EXIT = "\033[48;2;230;30;30m  "
ANSI_LOGO = "\033[48;2;141;16;205m  "
ANSI_LOGO_BORDER = "\033[48;2;77;11;110m  "


def visualize(
    grid: Grid,
    path_cells: set[Cell] | None = None,
    path_edges: set[Edge] | None = None,
    entry: Cell | None = None,
    exits: Cell | None = None,
    logo_cells: set[Cell] | None = None,
    wall_color: tuple[int, int, int] | None = None,
    animating: bool = False,
) -> None:
    """Render maze with ANSI colors."""
    if wall_color:
        r, g, b = wall_color
        wall: str = f"\033[48;2;{r};{g};{b}m  "
    else:
        wall = ANSI_WALL
    path_cells = path_cells or set()
    path_edges = path_edges or set()
    logo_cells = logo_cells or set()
    rows = len(grid)
    cols = len(grid[0]) if grid else 0

    canvas_height = 2 * rows + 1
    canvas_width = 2 * cols + 1
    canvas = [
        [wall for _ in range(canvas_width)] for _ in range(canvas_height)
    ]

    for y in range(rows):
        for x in range(cols):
            _draw_cell(
                canvas, grid[y][x], x, y, path_cells, path_edges,
                entry, exits, logo_cells, animating
            )

    _fill_pillars(canvas, rows, cols, wall)
    _draw_logo_border(canvas, logo_cells, wall)

    for row in canvas:
        print("".join(row) + ANSI_RESET)


def _draw_logo_border(
    canvas: list[list[str]], logo_cells: set[Cell],
    wall: str
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
                        canvas[wy][wx] = ANSI_LOGO_BORDER


def _fill_pillars(
    canvas: list[list[str]], rows: int, cols: int,
    wall: str
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
            if all(s == ANSI_PATH for s in slots):
                canvas[py][px] = ANSI_PATH
            else:
                canvas[py][px] = ANSI_OPEN


def _draw_cell(
    canvas: list[list[str]],
    cell: int,
    x: int,
    y: int,
    path_cells: set[Cell],
    path_edges: set[Edge],
    entry: Cell | None,
    exits: Cell | None,
    logo_cells: set[Cell],
    animating: bool,
) -> None:
    """Paint one cell and its open walls onto the canvas."""

    cx = 2 * x + 1
    cy = 2 * y + 1

    if animating and cell == 15 and (x, y) not in (entry, exits):
        return

    if (x, y) == entry:
        canvas[cy][cx] = ANSI_ENTRY
    elif (x, y) == exits:
        canvas[cy][cx] = ANSI_EXIT
    elif (x, y) in logo_cells:
        canvas[cy][cx] = ANSI_LOGO
    elif (x, y) in path_cells:
        canvas[cy][cx] = ANSI_PATH
    else:
        canvas[cy][cx] = ANSI_OPEN

    for direction, (dx, dy) in DIRECTION_DELTAS.items():
        if cell & (1 << direction.value):
            continue

        wx = cx + dx
        wy = cy + dy
        neighbor = (x + dx, y + dy)
        canvas[wy][wx] = ANSI_PATH if ((x, y), neighbor) in path_edges else ANSI_OPEN
