"""Maze visualization — to be implemented."""
import curses
from collections.abc import Callable
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
VISITED = 9
FRONTIER = 10

PALETTE = {
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
    visited_cells: set[Cell] = set(),
    frontier_cells: set[Cell] = set(),
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
    elif frontier_cells and (x, y) in frontier_cells:
        canvas[cy][cx] = FRONTIER
    elif visited_cells and (x, y) in visited_cells:
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
        elif (x, y) in frontier_cells or neighbor in frontier_cells:
            canvas[wy][wx] = FRONTIER
        elif (x, y) in visited_cells and neighbor in visited_cells:
            canvas[wy][wx] = VISITED
        else:
            canvas[wy][wx] = OPEN


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
            elif all(s in (VISITED, PATH) for s in slots):
                canvas[py][px] = VISITED
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
                 visited_cells: set[Cell] | None = None,
                 frontier_cells: set[Cell] | None = None,
                 ) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    canvas_height = 2*rows+1
    canvas_width = 2*cols+1
    path_cells = path_cells or set()
    path_edges = path_edges or set()
    logo_cells = logo_cells or set()
    _visited = visited_cells or set()
    _frontier = frontier_cells or set()
    canvas = [
        [WALL for _ in range(canvas_width)]for _ in range(canvas_height)]
    for y in range(rows):
        for x in range(cols):
            _draw_cell(
                canvas, grid[y][x], x, y, path_cells, path_edges, entry, exits,
                logo_cells, animating, _visited, _frontier
            )
    _fill_pillars(canvas, rows, cols, WALL)
    _draw_logo_border(canvas, logo_cells, WALL)
    if cursor is not None:
        cx, cy = cursor
        if 0 <= cy < rows and 0 <= cx < cols:
            canvas[2 * cy + 1][2 * cx + 1] = CURSOR
    return canvas


def render(stdscr: curses.window, canvas: list[list[int]]) -> None:
    blit(stdscr, canvas)


def runviewer(stdscr: curses.window, make_mazegen: Callable[[], MazeGenerator],
              alge: int,
              show_path: bool = False,
              output_file: str = "output.txt",
              animation: bool = False,
              solver_anim: bool = False) -> None:
    setup_colors()
    curses.curs_set(0)

    while True:
        mazegen = make_mazegen()
        step_count = 0

        def on_step() -> None:
            nonlocal step_count
            step_count += 1
            if step_count % 6 != 0:
                return
            stdscr.erase()
            animation_canvas = build_canvas(mazegen.grid, mazegen.entry,
                                            mazegen.exits, None,
                                            mazegen.cursor,
                                            None, None, True)
            render(stdscr, animation_canvas)
            stdscr.refresh()

        if alge == 1:
            gen_result = mazegen.generate(on_step if animation else None)
        elif alge == 3:
            gen_result = mazegen.prims_algorithm(
                on_step if animation else None)
        else:
            gen_result = mazegen.bin_tree(on_step if animation else None)

        if isinstance(gen_result, Err):
            return

        solve_step_count = 0

        def solve_on_step(
            visited: set[Cell], frontier: set[Cell]
        ) -> None:
            nonlocal solve_step_count
            solve_step_count += 1
            if solve_step_count % 4 != 0:
                return
            stdscr.erase()
            solve_canvas = build_canvas(
                mazegen.grid, mazegen.entry, mazegen.exits,
                set(mazegen.logo_cells), None, None, None,
                False, visited, frontier)
            render(stdscr, solve_canvas)
            stdscr.refresh()

        solve_result = solve(
            mazegen.grid, mazegen.entry, mazegen.exits,
            solve_on_step if solver_anim else None)
        if isinstance(solve_result, Err):
            return

        path = solve_result.value
        validation = validate_path(
            mazegen.grid, path, mazegen.entry, mazegen.exits)
        if isinstance(validation, Err):
            return

        path_cells, path_edges = path_to_edges(path, mazegen.entry)

        while True:
            stdscr.erase()
            if not show_path:
                canvas = build_canvas(mazegen.grid, mazegen.entry,
                                      mazegen.exits,
                                      set(mazegen.logo_cells), None,
                                      None, None)
            else:
                canvas = build_canvas(mazegen.grid,
                                      mazegen.entry, mazegen.exits,
                                      set(mazegen.logo_cells), None,
                                      path_cells, path_edges)
            render(stdscr, canvas)
            height, width = stdscr.getmaxyx()
            try:
                stdscr.addstr(
                    height - 1, round(width/2)-30,
                    "[p] show path  [r] regenerate  [s] save "
                    " [a] animate solver  [q] quit",
                    curses.A_BOLD)
            except curses.error:
                pass
            stdscr.refresh()
            match stdscr.getch():
                case q if q == ord('q'):
                    return
                case p if p == ord('p'):
                    show_path = not show_path
                case r if r == ord('r'):
                    break
                case a if a == ord('a'):
                    solver_anim = not solver_anim
                    solve_result = solve(
                        mazegen.grid, mazegen.entry, mazegen.exits,
                        solve_on_step if solver_anim else None)
                case s if s == ord('s'):
                    save_output(mazegen, output_file)


def blit(stdscr: curses.window, canvas: list[list[int]]) -> None:
    term_h, term_w = stdscr.getmaxyx()
    canvas_h = len(canvas)
    canvas_w = len(canvas[0]) if canvas else 0

    vis_rows = min(term_h, canvas_h)
    vis_cols = min(term_w // 2, canvas_w)
    pad_y = max(0, (term_h - canvas_h) // 2)
    pad_x = max(0, (term_w - canvas_w * 2) // 2)
    off_r = max(0, (canvas_h - vis_rows) // 2)
    off_c = max(0, (canvas_w - vis_cols) // 2)

    for sy in range(vis_rows):
        row = canvas[off_r + sy]
        screen_y = pad_y + sy
        sx = 0
        while sx < vis_cols:
            code = row[off_c + sx]
            run = 1
            while sx + run < vis_cols and row[off_c + sx + run] == code:
                run += 1
            try:
                stdscr.addstr(screen_y, pad_x + sx * 2, "  " * run,
                              curses.color_pair(code))
            except curses.error:
                pass
            sx += run
