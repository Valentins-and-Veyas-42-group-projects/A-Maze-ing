"""Maze visualization — to be implemented."""
import curses
from .errors import Err
from .generator import MazeGenerator
from .output import save_output
from .shared import Cell, Edge, DIRECTION_DELTAS, Grid
from .solver import path_to_edges, solve, validate_path


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
    animation: bool = False,

) -> None:
    """Paint one cell and its open walls onto the canvas."""

    cx = 2 * x + 1
    cy = 2 * y + 1
    if animation and cell == 15 and (x, y) not in (entry, exits):
        return
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


def build_canvas(grid: Grid,
                 entry: Cell,
                 exits: Cell,
                 logo_cells: set[Cell] | None = None,
                 cursor: Cell | None = None,
                 path_cells: set[Cell] | None = None,
                 path_edges: set[Edge] | None = None,
                 animating: bool = False,
                 ) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    canvas_height = 2*rows+1
    canvas_width = 2*cols+1
    path_cells = path_cells or set()
    path_edges = path_edges or set()
    logo_cells = logo_cells or set()
    canvas = [
        [WALL for _ in range(canvas_width)]for _ in range(canvas_height)]
    for y in range(rows):
        for x in range(cols):
            _draw_cell(
                canvas, grid[y][x], x, y, path_cells, path_edges, entry, exits,
                logo_cells, animating
            )
    _fill_pillars(canvas, rows, cols, WALL)
    _draw_logo_border(canvas, logo_cells, WALL)
    if cursor is not None:
        cx, cy = cursor
        if 0 <= cy < rows and 0 <= cx < cols:
            canvas[2 * cy + 1][2 * cx + 1] = CURSOR
    return canvas


def render(stdscr: curses.window, canvas: list[list[int]]) -> None:
    term_height, term_width = stdscr.getmaxyx()
    canvas_height, canvas_width = len(canvas), len(canvas[0])
    offset_y, offset_x = (
        term_height-canvas_height)//2, (term_width-canvas_width * 2)//2
    for y, row in enumerate(canvas):
        for x, color_id in enumerate(row):
            try:
                stdscr.addstr(offset_y+y, offset_x + x*2, "  ",
                              curses.color_pair(color_id))
            except curses.error:
                pass


def runviewer(stdscr: curses.window, mazegen: MazeGenerator,
              alge: int,
              show_path: bool = False,
              output_file: str = "output.txt",
              animation: bool = False) -> None:
    setup_colors()
    curses.curs_set(0)

    def on_step() -> None:
        stdscr.clear()
        animation_canvas = build_canvas(mazegen.grid, mazegen.entry,
                                        mazegen.exits, None, mazegen.cursor,
                                        None, None, True)
        render(stdscr, animation_canvas)

        stdscr.refresh()

    if alge == 1:
        gen_result = mazegen.generate(on_step if animation else None)
    elif alge == 3:
        gen_result = mazegen.prims_algorithm(on_step if animation else None)
    else:
        gen_result = mazegen.bin_tree(on_step if animation else None)

    if isinstance(gen_result, Err):
        return

    solve_result = solve(mazegen.grid, mazegen.entry, mazegen.exits)
    if isinstance(solve_result, Err):
        return

    path = solve_result.value
    validation = validate_path(
        mazegen.grid, path, mazegen.entry, mazegen.exits)
    if isinstance(validation, Err):
        return

    path_cells, path_edges = path_to_edges(path, mazegen.entry)

    while True:
        stdscr.clear()
        if not show_path:
            canvas = build_canvas(mazegen.grid, mazegen.entry, mazegen.exits,
                                  set(mazegen.logo_cells), None,
                                  None, None)
        else:
            canvas = build_canvas(mazegen.grid, mazegen.entry, mazegen.exits,
                                  set(mazegen.logo_cells), None,
                                  path_cells, path_edges)
        render(stdscr, canvas)
        height, width = stdscr.getmaxyx()
        stdscr.addstr(
            height -
            1, round(width/2)-30, "[p] show path     [s] save to output.txt"
            "      [q] quit", curses.A_BOLD)
        stdscr.refresh()
        match stdscr.getch():
            case q if q == ord('q'):
                break
            case p if p == ord('p'):
                show_path = not show_path
            case s if s == ord('s'):
                save_output(mazegen, output_file)
