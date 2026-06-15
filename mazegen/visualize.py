"""Interactive curses viewer for maze generation and solving."""

import curses
import random
from collections.abc import Callable

from .canvas import PALETTE, WALL, apply_path_step, build_canvas, rgb_to_curses
from .errors import Err
from .generator import MazeGenerator
from .output import save_output
from .shared import Cell, DIRECTION_DELTAS, LETTER_TO_DIRECTION
from .solver import path_to_edges, solve, solve_dfs, validate_path


def setup_colors() -> None:
    """Initialize curses color pairs from the PALETTE mapping.

    Registers each palette entry as both a curses color (via init_color)
    and a color pair with a transparent foreground (via init_pair), so
    color IDs from canvas.py can be passed directly to color_pair().
    """
    curses.start_color()
    curses.use_default_colors()
    for k, v in PALETTE.items():
        conv = rgb_to_curses(v)
        curses.init_color(k, *conv)
        curses.init_pair(k, -1, k)


def blit(stdscr: curses.window, canvas: list[list[int]]) -> None:
    """Draw the canvas to the terminal, centered and run-length encoded.

    Clips the canvas to the visible terminal area, then paints each
    horizontal run of equal color IDs with a single addstr call to
    minimize curses overhead. Each canvas column is two terminal columns
    wide so the cells appear square on most terminals.
    """
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
                stdscr.addstr(
                    screen_y, pad_x + sx * 2,
                    "  " * run,
                    curses.color_pair(code),
                )
            except curses.error:
                pass
            sx += run


def path_anim(
    stdscr: curses.window, mazegen: MazeGenerator, path: str
) -> None:
    """Animate the solution path step by step on the screen.

    Builds the base canvas once, then per step updates only the new
    cell slot, wall slot, and adjacent pillar slots via apply_path_step,
    avoiding a full canvas rebuild on every frame.
    """
    canvas = build_canvas(
        mazegen.grid, mazegen.entry, mazegen.exits,
        set(mazegen.logo_cells),
    )
    x, y = mazegen.entry

    for letter in path:
        direction = LETTER_TO_DIRECTION[letter]
        dx, dy = DIRECTION_DELTAS[direction]
        nx, ny = x + dx, y + dy
        apply_path_step(canvas, (x, y), (nx, ny))
        x, y = nx, ny
        stdscr.erase()
        blit(stdscr, canvas)
        stdscr.refresh()


def runviewer(
    stdscr: curses.window,
    make_mazegen: Callable[[], MazeGenerator],
    alge: int,
    show_path: bool = False,
    output_file: str = "output.txt",
    animation: bool = False,
    solver_anim: bool = False,
) -> None:
    """Run the interactive maze viewer loop.

    Generates a maze with the selected algorithm, optionally animating
    both construction and solving, then enters a key-driven display loop.

    Keys:
        p — toggle solution path overlay
        r — regenerate maze
        s — save maze to output_file
        a — replay solver animation with current algorithm
        d — toggle solver algorithm between BFS and DFS
        c — randomize wall color
        q — quit
    """
    setup_colors()
    curses.curs_set(0)
    use_dfs = False
    speed_skip = 6  # steps between renders; lower = slower, higher = faster

    while True:
        mazegen = make_mazegen()
        step_count = 0

        def on_step() -> None:
            nonlocal step_count, speed_skip
            step_count += 1
            if step_count % speed_skip != 0:
                return
            stdscr.nodelay(True)
            key = stdscr.getch()
            stdscr.nodelay(False)
            if key == ord('.'):
                speed_skip = min(256, speed_skip + 1)
            elif key == ord(','):
                speed_skip = max(1, speed_skip - 1)
            stdscr.erase()
            anim_canvas = build_canvas(
                mazegen.grid, mazegen.entry, mazegen.exits, None,
                mazegen.cursor, None, None, True,
            )
            blit(stdscr, anim_canvas)
            height, width = stdscr.getmaxyx()
            hint = f"[,] slower  [.] faster  (speed: {speed_skip})"
            try:
                stdscr.addstr(
                    height - 1, max(0, round(width / 2) - len(hint) // 2),
                    hint, curses.A_BOLD,
                )
            except curses.error:
                pass
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
            nonlocal solve_step_count, speed_skip
            solve_step_count += 1
            if solve_step_count % speed_skip != 0:
                return
            stdscr.nodelay(True)
            key = stdscr.getch()
            stdscr.nodelay(False)
            if key == ord('.'):
                speed_skip = min(256, speed_skip + 1)
            elif key == ord(','):
                speed_skip = max(1, speed_skip - 1)
            stdscr.erase()
            solve_canvas = build_canvas(
                mazegen.grid, mazegen.entry, mazegen.exits,
                set(mazegen.logo_cells), None, None, None,
                False, visited, frontier,
            )
            blit(stdscr, solve_canvas)
            height, width = stdscr.getmaxyx()
            hint = f"[,] slower  [.] faster  (speed: {speed_skip})"
            try:
                stdscr.addstr(
                    height - 1, max(0, round(width / 2) - len(hint) // 2),
                    hint, curses.A_BOLD,
                )
            except curses.error:
                pass
            stdscr.refresh()

        active_solver = solve_dfs if use_dfs else solve
        solve_result = active_solver(
            mazegen.grid, mazegen.entry, mazegen.exits,
            solve_on_step if solver_anim else None,
        )
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
                canvas = build_canvas(
                    mazegen.grid, mazegen.entry, mazegen.exits,
                    set(mazegen.logo_cells),
                )
            else:
                canvas = build_canvas(
                    mazegen.grid, mazegen.entry, mazegen.exits,
                    set(mazegen.logo_cells), None,
                    path_cells, path_edges,
                )
            blit(stdscr, canvas)
            height, width = stdscr.getmaxyx()
            alg_label = "DFS" if use_dfs else "BFS"
            hint = (
                f"[p] path  [r] regen  [s] save  [a] anim"
                f"  [d] solver:{alg_label}  [,/.] speed  [q] quit"
            )
            try:
                stdscr.addstr(
                    height - 1, max(0, round(width / 2) - len(hint) // 2),
                    hint,
                    curses.A_BOLD,
                )
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
                    active_solver = solve_dfs if use_dfs else solve
                    solve_result = active_solver(
                        mazegen.grid, mazegen.entry, mazegen.exits,
                        solve_on_step,
                    )
                    path_anim(stdscr, mazegen, path)
                case d if d == ord('d'):
                    use_dfs = not use_dfs
                    active_solver = solve_dfs if use_dfs else solve
                    solve_result = active_solver(
                        mazegen.grid, mazegen.entry, mazegen.exits,
                    )
                    if isinstance(solve_result, Err):
                        continue
                    path = solve_result.value
                    path_cells, path_edges = path_to_edges(
                        path, mazegen.entry)
                case dot if dot == ord('.'):
                    speed_skip = min(256, speed_skip + 1)
                case comma if comma == ord(','):
                    speed_skip = max(1, speed_skip - 1)
                case s if s == ord('s'):
                    save_output(mazegen, output_file)
                case c if c == ord('c'):
                    col: tuple[int, int, int] = (
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255),
                    )
                    curses.init_color(WALL, *rgb_to_curses(col))
