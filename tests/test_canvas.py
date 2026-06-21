"""Canvas building tests."""

from mazegen.canvas import (
    CURSOR,
    ENTRY,
    EXIT,
    OPEN,
    PATH,
    build_canvas,
    rgb_to_curses,
)


def test_rgb_to_curses() -> None:
    assert rgb_to_curses((0, 0, 0)) == (0, 0, 0)
    assert rgb_to_curses((255, 255, 255)) == (1000, 1000, 1000)
    assert rgb_to_curses((127, 127, 127)) == (
        127 * 1000 // 255,
        127 * 1000 // 255,
        127 * 1000 // 255,
    )


def test_build_canvas_basic() -> None:
    grid = [[15]]
    entry = (0, 0)
    exits = (0, 0)

    canvas = build_canvas(grid, entry, exits)
    assert len(canvas) == 3
    assert len(canvas[0]) == 3
    assert canvas[1][1] == ENTRY


def test_build_canvas_with_path() -> None:
    grid = [[13, 7]]
    entry = (0, 0)
    exits = (1, 0)
    path_cells = {(0, 0), (1, 0)}
    path_edges = {((0, 0), (1, 0)), ((1, 0), (0, 0))}

    canvas = build_canvas(
        grid, entry, exits, path_cells=path_cells, path_edges=path_edges
    )

    assert canvas[1][1] == ENTRY
    assert canvas[1][2] == PATH
    assert canvas[1][3] == EXIT


def test_build_canvas_with_cursor() -> None:
    grid = [[15]]
    entry = (0, 0)
    exits = (0, 0)
    cursor = (0, 0)

    canvas = build_canvas(grid, entry, exits, cursor=cursor)
    assert canvas[1][1] == CURSOR


def test_build_canvas_pillar_filling() -> None:
    grid = [[0, 0], [0, 0]]
    entry = (0, 0)
    exits = (1, 1)

    canvas = build_canvas(grid, entry, exits)
    assert canvas[2][2] == OPEN
