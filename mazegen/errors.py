"""Shared result and error types for maze operations."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Generic, TypeVar


class MazeError(Enum):
    """Enumerate failure modes returned by maze operations."""

    INVALID_WIDTH = auto()
    INVALID_HEIGHT = auto()
    INVALID_ENTRY = auto()
    INVALID_EXIT = auto()
    INVALID_PATH = auto()
    ENTRY_EXIT_SAME = auto()
    NO_PATH_FOUND = auto()
    NO_42_LOGO = auto()


T = TypeVar("T")


@dataclass(frozen=True)
class Ok(Generic[T]):
    """Wrap a successful result value of type T."""

    value: T


@dataclass(frozen=True)
class Err:
    """Wrap a failure result carrying a MazeError variant."""

    error: MazeError
