"""42 logo patterns stamped into generated mazes."""

from typing import NamedTuple

from .shared import Cell


class Pattern(NamedTuple):
    """A logo stencil: relative cells plus its bounding box."""

    cells: list[Cell]
    width: int
    height: int

    def offset(self, grid_width: int, grid_height: int) -> Cell:
        """Top-left corner that centers the pattern in the grid."""

        return (
            (grid_width - self.width) // 2,
            (grid_height - self.height) // 2,
        )

    def placed_cells(
        self, grid_width: int, grid_height: int
    ) -> list[Cell]:
        """Absolute cells the pattern occupies, centered in the grid."""

        ox, oy = self.offset(grid_width, grid_height)
        return [(ox + dx, oy + dy) for (dx, dy) in self.cells]

    def fits(self, grid_width: int, grid_height: int) -> bool:
        """Whether the grid is large enough to hold the pattern."""

        return grid_width > self.width and grid_height > self.height


PATTERN_SMALL = Pattern(
    cells=[
        # 4
        (0, 0),         (2, 0),
        (0, 1),         (2, 1),
        (0, 2), (1, 2), (2, 2),
        (2, 3),
        (2, 4),
        # 2
        (4, 0), (5, 0), (6, 0),
        (6, 1),
        (4, 2), (5, 2), (6, 2),
        (4, 3),
        (4, 4), (5, 4), (6, 4),
    ],
    width=7,
    height=5,
)

PATTERN_LARGE = Pattern(
    cells=[
        # 4
        (0, 0),          (4, 0),
        (0, 1),          (4, 1),
        (0, 2),          (4, 2),
        (0, 3),          (4, 3),
        (0, 4), (1, 4), (2, 4), (3, 4), (4, 4),
        (4, 5),
        (4, 6),
        (4, 7),
        (4, 8),
        # 2
        (6, 0), (7, 0), (8, 0), (9, 0), (10, 0),
        (10, 1),
        (10, 2),
        (10, 3),
        (6, 4), (7, 4), (8, 4), (9, 4), (10, 4),
        (6, 5),
        (6, 6),
        (6, 7),
        (6, 8), (7, 8), (8, 8), (9, 8), (10, 8),
    ],
    width=11,
    height=9,
)


def select_pattern(grid_width: int, grid_height: int) -> Pattern:
    """Pick the logo pattern sized for the given grid."""

    if 8 < grid_width < 25 and 6 < grid_height < 23:
        return PATTERN_SMALL
    return PATTERN_LARGE
