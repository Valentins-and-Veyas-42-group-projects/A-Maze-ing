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


class ConfigError(Enum):
    """Enumerate failure modes returned by config operations."""

    ERR_INVALID_WIDTH = auto()
    ERR_INVALID_HEIGHT = auto()
    ERR_INVALID_ENTRY = auto()
    ERR_INVALID_EXIT = auto()
    ERR_INVALID_OUTPUT_FILE = auto()
    ERR_INVALID_WAIT_TIME = auto()
    ERR_INVALID_SYNTAX = auto()
    ERR_CANT_OPEN_FILE = auto()
    ERR_FILE_NOT_FOUND = auto()
    ERR_INVALID_PERFECT = auto()
    ERR_INVALID_VERBOSE = auto()
    ERR_INVALID_FORCE_WAIT_TIME = auto()
    ERR_INVALID_SPEED = auto()
    ERR_INVALID_ALGORITHM = auto()
    ERR_INVALID_WALL_COLOR = auto()


E = TypeVar("E", bound=Enum)
T = TypeVar("T")


@dataclass(frozen=True)
class Diagnostic:
    """Stores the exact location and context of an error for Rust-style reporting."""

    filename: str
    line_num: int
    line_text: str
    col_start: int
    col_end: int
    help_msg: str | None = None


@dataclass(frozen=True)
class Ok(Generic[T]):
    """Wrap a successful result value of type T."""

    value: T


@dataclass(frozen=True)
class Err(Generic[E]):
    """Wrap a failure result carrying an error variant and optional diagnostic context."""

    error: E
    diagnostic: Diagnostic | None = None

    def print_diagnostic(self) -> None:
        """Prints a rust-style diagnostic message with dynamic caret alignment."""
        RED = "\033[1;31m"
        PINK = "\033[1;35m"
        BLUE = "\033[1;34m"
        CYAN = "\033[1;36m"
        RESET = "\033[0m"
        BOLD = "\033[1m"

        err_name_str = str(self.error.name)
        err_namespace = (
            err_name_str.lower().replace("err_", "").replace("_", "::")
        )
        print(f"{BOLD}Error:{RESET} {PINK}mazegen::{err_namespace}{RESET}\n")

        if not self.diagnostic:
            print(f" {RED}×{RESET} {BOLD}Operation failed{RESET}")
            print(
                f"   {RED}╰─▶{RESET} {err_name_str.replace('ERR_', '').replace('_', ' ').title()}"
            )
            return

        d = self.diagnostic

        print(f" {RED}×{RESET} {BOLD}Configuration validation failed{RESET}")
        print(
            f"   {BLUE}╭─[{RESET}{BOLD}{d.filename}:"
            f"{d.line_num}:{d.col_start + 1}{RESET}{BLUE}]{RESET}"
        )
        print(f"{d.line_num:2} {BLUE}│{RESET} {d.line_text}")

        hook_text = "╰─── "
        prefix = f"{RED}{hook_text}{BOLD}"
        carets = "^" * max(1, (d.col_end - d.col_start))

        hook_width = len(hook_text)

        if d.col_start >= hook_width:
            padding = " " * (d.col_start - hook_width)
            print(f"   {BLUE}·{RESET} {padding}{prefix}{carets}{RESET}")
        else:
            padding = " " * d.col_start
            print(f"   {BLUE}·{RESET} {padding}{RED}{carets}{RESET}")

        if d.help_msg:
            print(f"\n   {CYAN}help:{RESET} {d.help_msg}")
