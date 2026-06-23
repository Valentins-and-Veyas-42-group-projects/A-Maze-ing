"""Configuration parsing tests."""

from pathlib import Path

import pytest

from mazegen.config import Config, parse_config
from mazegen.errors import ConfigError, Diagnostic, Err, Ok


def write_config(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "config.txt"
    path.write_text(content, encoding="utf-8")
    return path


def parse_text(tmp_path: Path, content: str) -> Ok[Config] | Err[ConfigError]:
    return parse_config(str(write_config(tmp_path, content)))


def valid_config(extra: str = "") -> str:
    return (
        "WIDTH = 20\n"
        "HEIGHT = 15\n"
        "ENTRY = 0,0\n"
        "EXIT = 19,14\n"
        "OUTPUT_FILE = maze.txt\n"
        "PERFECT = True\n"
        f"{extra}"
    )


def assert_config_error(
    result: Ok[Config] | Err[ConfigError],
    error: ConfigError,
) -> Diagnostic:
    assert isinstance(result, Err)
    assert result.error is error
    assert result.diagnostic is not None
    return result.diagnostic


def test_parse_config_accepts_required_and_optional_values(
    tmp_path: Path,
) -> None:
    result = parse_text(
        tmp_path,
        valid_config(
            "ANIMATION = True\n"
            "SHOW_PATH = True\n"
            "SPEED = 4\n"
            "ALGORITHM = 2\n"
            "SEED = fixed-seed\n"
            "WALL_COLOR = 10,20,30\n"
        ),
    )

    assert isinstance(result, Ok)
    assert result.value == Config(
        width=20,
        height=15,
        entry=(0, 0),
        exits=(19, 14),
        output_file="maze.txt",
        perfect=True,
        verbose=False,
        animation=True,
        show_path=True,
        force_wait_time=0.5,
        speed=4,
        algorithm=2,
        seed="fixed-seed",
        wall_color=(10, 20, 30),
    )


def test_parse_config_uses_defaults_for_optional_values(
    tmp_path: Path,
) -> None:
    result = parse_text(tmp_path, valid_config())

    assert isinstance(result, Ok)
    assert result.value.verbose is False
    assert result.value.animation is False
    assert result.value.show_path is False
    assert result.value.force_wait_time == 0.5
    assert result.value.speed == 1
    assert result.value.algorithm == 1
    assert result.value.seed is None
    assert result.value.wall_color is None


@pytest.mark.parametrize(
    ("line", "error", "help_text"),
    [
        ("WIDTH = zero", ConfigError.ERR_INVALID_WIDTH, "WIDTH must be"),
        ("HEIGHT = -1", ConfigError.ERR_INVALID_HEIGHT, "HEIGHT must be"),
        ("SPEED = 0", ConfigError.ERR_INVALID_SPEED, "SPEED must be"),
        (
            "ALGORITHM = 4",
            ConfigError.ERR_INVALID_ALGORITHM,
            "ALGORITHM must be",
        ),
    ],
)
def test_parse_config_rejects_non_positive_integers(
    tmp_path: Path,
    line: str,
    error: ConfigError,
    help_text: str,
) -> None:
    result = parse_text(tmp_path, valid_config(f"{line}\n"))

    diagnostic = assert_config_error(result, error)
    assert help_text in str(diagnostic.help_msg)


@pytest.mark.parametrize(
    ("line", "error"),
    [
        ("PERFECT = yes", ConfigError.ERR_INVALID_PERFECT),
        ("ANIMATION = yes", ConfigError.ERR_INVALID_ANIMATION),
        ("SHOW_PATH = yes", ConfigError.ERR_INVALID_SHOW_PATH),
    ],
)
def test_parse_config_rejects_invalid_booleans(
    tmp_path: Path,
    line: str,
    error: ConfigError,
) -> None:
    result = parse_text(tmp_path, valid_config(f"{line}\n"))

    diagnostic = assert_config_error(result, error)
    assert "must be either 'True' or 'False'" in str(diagnostic.help_msg)


@pytest.mark.parametrize(
    ("line", "error", "help_text"),
    [
        ("ENTRY = 0,", ConfigError.ERR_INVALID_ENTRY, "Missing coordinate"),
        (
            "ENTRY = 0,zero",
            ConfigError.ERR_INVALID_ENTRY,
            "Expected an integer",
        ),
        ("EXIT = 1,2,3", ConfigError.ERR_INVALID_EXIT, "exactly one comma"),
    ],
)
def test_parse_config_rejects_invalid_coordinates(
    tmp_path: Path,
    line: str,
    error: ConfigError,
    help_text: str,
) -> None:
    result = parse_text(tmp_path, valid_config(f"{line}\n"))

    diagnostic = assert_config_error(result, error)
    assert help_text in str(diagnostic.help_msg)


@pytest.mark.parametrize(
    ("line", "help_text"),
    [
        ("OUTPUT_FILE = ", "cannot be empty"),
        ("OUTPUT_FILE = bad/name.txt", "invalid character"),
    ],
)
def test_parse_config_rejects_invalid_output_files(
    tmp_path: Path,
    line: str,
    help_text: str,
) -> None:
    result = parse_text(tmp_path, valid_config(f"{line}\n"))

    diagnostic = assert_config_error(
        result, ConfigError.ERR_INVALID_OUTPUT_FILE)
    assert help_text in str(diagnostic.help_msg)


@pytest.mark.parametrize(
    ("line", "help_text"),
    [
        ("WALL_COLOR = 1,2", "three RGB integers"),
        ("WALL_COLOR = 1,blue,3", "integers from 0 to 255"),
        ("WALL_COLOR = 1,2,300", "integers from 0 to 255"),
    ],
)
def test_parse_config_rejects_invalid_wall_color(
    tmp_path: Path,
    line: str,
    help_text: str,
) -> None:
    result = parse_text(tmp_path, valid_config(f"{line}\n"))

    diagnostic = assert_config_error(
        result, ConfigError.ERR_INVALID_WALL_COLOR)
    assert help_text in str(diagnostic.help_msg)


def test_parse_config_rejects_empty_seed(tmp_path: Path) -> None:
    result = parse_text(tmp_path, valid_config("SEED = \n"))

    diagnostic = assert_config_error(result, ConfigError.ERR_INVALID_SYNTAX)
    assert diagnostic.help_msg == "SEED value cannot be empty"


def test_parse_config_rejects_missing_delimiter(tmp_path: Path) -> None:
    result = parse_text(tmp_path, "WIDTH 20\n")

    diagnostic = assert_config_error(result, ConfigError.ERR_INVALID_SYNTAX)
    assert diagnostic.help_msg == "expected '=' to separate key and value"


def test_parse_config_reports_missing_required_keys(tmp_path: Path) -> None:
    result = parse_text(tmp_path, valid_config().replace("WIDTH = 20\n", ""))

    diagnostic = assert_config_error(result, ConfigError.ERR_INVALID_SYNTAX)
    assert diagnostic.help_msg == (
        "Missing mandatory configuration options: WIDTH"
    )


def test_parse_config_suggests_known_key_for_typos(tmp_path: Path) -> None:
    result = parse_text(tmp_path, valid_config("SPED = 5\n"))

    diagnostic = assert_config_error(result, ConfigError.ERR_INVALID_SYNTAX)
    assert diagnostic.help_msg == (
        "Unknown configuration key 'SPED'. Did you mean 'SPEED'?"
    )


def test_parse_config_returns_file_not_found_for_missing_file(
    tmp_path: Path,
) -> None:
    result = parse_config(str(tmp_path / "missing.txt"))

    assert isinstance(result, Err)
    assert result.error is ConfigError.ERR_FILE_NOT_FOUND
    assert result.diagnostic is None
