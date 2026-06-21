"""Output formatting tests."""

from mazegen.errors import Err, MazeError
from mazegen.output import format_output


def test_format_output_success() -> None:
    grid = [[13, 7]]
    entry = (0, 0)
    exits = (1, 0)

    result = format_output(grid, entry, exits)
    assert isinstance(result, str)

    assert result.startswith("D7")
    assert "0,0\n1,0\nE\n" in result


def test_format_output_no_path() -> None:
    grid = [[15, 15]]
    entry = (0, 0)
    exits = (1, 0)

    result = format_output(grid, entry, exits)
    assert isinstance(result, Err)
    assert result.error == MazeError.NO_PATH_FOUND
