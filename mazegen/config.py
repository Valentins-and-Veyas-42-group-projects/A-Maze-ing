from dataclasses import dataclass

from .errors import ConfigError, Diagnostic, Err, Ok

"""Maze configuration."""


@dataclass
class Config:
    """Maze configuration file options."""

    width: int
    height: int
    entry: tuple[int, int]
    exits: tuple[int, int]
    output_file: str = "output.txt"
    perfect: bool = False
    verbose: bool = False
    animation: bool = False
    show_path: bool = False
    force_wait_time: float = 0.5
    speed: int = 1
    algorithm: int = 1
    seed: str | None = None
    wall_color: tuple[int, int, int] | None = None


def parse_config(config_file: str) -> Ok[Config] | Err[ConfigError]:
    """Parse the config file and return a Config object."""

    config = Config(0, 0, (0, 0), (0, 0))

    valid_keys = {
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
        "VERBOSE",
        "ANIMATION",
        "SHOW_PATH",
        "FORCE_WAIT_TIME",
        "SPEED",
        "ALGORITHM",
        "SEED",
        "WALL_COLOR",
    }

    required_keys = {
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    }

    parsed_values: dict[
        str,
        int | str | tuple[int, int] | tuple[int, int, int] | float | None,
    ] = {}

    try:
        with open(config_file, encoding="utf-8") as f:
            lines = [line.rstrip("\r\n") for line in f.readlines()]

    except FileNotFoundError:
        return Err(ConfigError.ERR_FILE_NOT_FOUND)

    except PermissionError:
        return Err(ConfigError.ERR_CANT_OPEN_FILE)

    for idx, raw_line in enumerate(lines, 1):
        stripped = raw_line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if "=" not in raw_line:
            split_pos = raw_line.find(" ")

            if split_pos == -1:
                split_pos = len(raw_line)

            diag = Diagnostic(
                filename=config_file,
                line_num=idx,
                line_text=raw_line,
                col_start=split_pos,
                col_end=split_pos + 1,
                help_msg="expected '=' to separate key and value",
            )

            return Err(ConfigError.ERR_INVALID_SYNTAX, diag)

        key_part, val_part = raw_line.split("=", 1)

        key = key_part.strip()
        val = val_part.strip()

        match key:
            case "WIDTH" | "HEIGHT" | "SPEED" | "ALGORITHM":
                try:
                    int_val = int(val)

                    if int_val <= 0:
                        raise ValueError
                    if key == "ALGORITHM" and int_val not in (1, 2, 3):
                        raise ValueError

                    parsed_values[key] = int_val
                    required_keys.discard(key)

                    if key == "WIDTH":
                        config.width = int_val
                    elif key == "HEIGHT":
                        config.height = int_val
                    elif key == "ALGORITHM":
                        config.algorithm = int_val
                    else:
                        config.speed = int_val

                except ValueError:
                    start_col = raw_line.find(val)
                    help_msg = f"{key} must be a positive integer (e.g., '20')"
                    if key == "ALGORITHM":
                        help_msg = "ALGORITHM must be 1 for DFS, " \
                            "2 for binary tree, or 3 for Prim's"

                    diag = Diagnostic(
                        filename=config_file,
                        line_num=idx,
                        line_text=raw_line,
                        col_start=start_col,
                        col_end=start_col + len(val),
                        help_msg=help_msg,
                    )

                    int_errors = {
                        "WIDTH": ConfigError.ERR_INVALID_WIDTH,
                        "HEIGHT": ConfigError.ERR_INVALID_HEIGHT,
                        "SPEED": ConfigError.ERR_INVALID_SPEED,
                        "ALGORITHM": ConfigError.ERR_INVALID_ALGORITHM,
                    }
                    return Err(int_errors[key], diag)

            case "ENTRY" | "EXIT":
                if val.count(",") != 1:
                    first_comma = val.find(",")
                    second_comma = val.find(",", first_comma + 1)

                    if second_comma != -1:
                        start_col = raw_line.find(val) + second_comma
                        end_col = start_col + 1
                    else:
                        start_col = raw_line.find(val)
                        end_col = start_col + len(val)

                    diag = Diagnostic(
                        filename=config_file,
                        line_num=idx,
                        line_text=raw_line,
                        col_start=start_col,
                        col_end=end_col,
                        help_msg=(
                            f"{key} must contain exactly one comma "
                            "separating two integers (e.g., '0,0')"
                        ),
                    )

                    err_type = (
                        ConfigError.ERR_INVALID_ENTRY
                        if key == "ENTRY"
                        else ConfigError.ERR_INVALID_EXIT
                    )

                    return Err(err_type, diag)

                x_raw, y_raw = val.split(",")

                coords: list[int] = []

                for part_raw in (x_raw, y_raw):
                    part_stripped = part_raw.strip()

                    if not part_stripped:
                        start_col = raw_line.find(val)

                        diag = Diagnostic(
                            filename=config_file,
                            line_num=idx,
                            line_text=raw_line,
                            col_start=start_col,
                            col_end=start_col + len(val),
                            help_msg=f"Missing coordinate value in '{val}'",
                        )

                        err_type = (
                            ConfigError.ERR_INVALID_ENTRY
                            if key == "ENTRY"
                            else ConfigError.ERR_INVALID_EXIT
                        )

                        return Err(err_type, diag)

                    if not part_stripped.lstrip("-").isdigit():
                        start_col = raw_line.find(part_stripped)

                        diag = Diagnostic(
                            filename=config_file,
                            line_num=idx,
                            line_text=raw_line,
                            col_start=start_col,
                            col_end=start_col + len(part_stripped),
                            help_msg=(
                                "Expected an integer, found invalid "
                                f"characters: '{part_stripped}'"
                            ),
                        )

                        err_type = (
                            ConfigError.ERR_INVALID_ENTRY
                            if key == "ENTRY"
                            else ConfigError.ERR_INVALID_EXIT
                        )

                        return Err(err_type, diag)

                    coords.append(int(part_stripped))

                coord_tuple = (coords[0], coords[1])

                parsed_values[key] = coord_tuple
                required_keys.discard(key)

                if key == "ENTRY":
                    config.entry = coord_tuple
                else:
                    config.exits = coord_tuple

            case "OUTPUT_FILE":
                if not val:
                    start_col = raw_line.find("=") + 1

                    diag = Diagnostic(
                        filename=config_file,
                        line_num=idx,
                        line_text=raw_line,
                        col_start=start_col,
                        col_end=len(raw_line),
                        help_msg="OUTPUT_FILE value cannot be empty",
                    )

                    return Err(
                        ConfigError.ERR_INVALID_OUTPUT_FILE,
                        diag,
                    )

                invalid_chars = set('<>:"/\\|?*')

                found_invalid = [c for c in val if c in invalid_chars]

                if found_invalid:
                    first_bad = next(
                        i for i, c in enumerate(val) if c in invalid_chars
                    )

                    start_col = raw_line.find(val) + first_bad

                    diag = Diagnostic(
                        filename=config_file,
                        line_num=idx,
                        line_text=raw_line,
                        col_start=start_col,
                        col_end=start_col + 1,
                        help_msg=(
                            "OUTPUT_FILE contains invalid "
                            f"character: '{val[first_bad]}'"
                        ),
                    )

                    return Err(
                        ConfigError.ERR_INVALID_OUTPUT_FILE,
                        diag,
                    )

                parsed_values["OUTPUT_FILE"] = val
                required_keys.discard("OUTPUT_FILE")

                config.output_file = val

            case "SEED":
                if not val:
                    start_col = raw_line.find("=") + 1

                    diag = Diagnostic(
                        filename=config_file,
                        line_num=idx,
                        line_text=raw_line,
                        col_start=start_col,
                        col_end=len(raw_line),
                        help_msg="SEED value cannot be empty",
                    )

                    return Err(ConfigError.ERR_INVALID_SYNTAX, diag)

                parsed_values["SEED"] = val
                config.seed = val

            case "PERFECT" | "VERBOSE" | "ANIMATION" | "SHOW_PATH":
                if val not in ("True", "False"):
                    start_col = raw_line.find(val)

                    diag = Diagnostic(
                        filename=config_file,
                        line_num=idx,
                        line_text=raw_line,
                        col_start=start_col,
                        col_end=start_col + len(val),
                        help_msg=f"{key} must be either 'True' or 'False'",
                    )

                    bool_errors = {
                        "PERFECT": ConfigError.ERR_INVALID_PERFECT,
                        "VERBOSE": ConfigError.ERR_INVALID_VERBOSE,
                        "ANIMATION": ConfigError.ERR_INVALID_VERBOSE,
                        "SHOW_PATH": ConfigError.ERR_INVALID_VERBOSE,
                    }
                    return Err(bool_errors[key], diag)

                parsed_values[key] = val
                required_keys.discard(key)

                if key == "PERFECT":
                    config.perfect = val == "True"
                elif key == "VERBOSE":
                    config.verbose = val == "True"
                elif key == "ANIMATION":
                    config.animation = val == "True"
                else:
                    config.show_path = val == "True"

            case "FORCE_WAIT_TIME":
                try:
                    wait_time = float(val)

                    if wait_time <= 0:
                        raise ValueError

                    parsed_values["FORCE_WAIT_TIME"] = wait_time
                    required_keys.discard("FORCE_WAIT_TIME")

                    config.force_wait_time = wait_time

                except ValueError:
                    start_col = raw_line.find(val)

                    diag = Diagnostic(
                        filename=config_file,
                        line_num=idx,
                        line_text=raw_line,
                        col_start=start_col,
                        col_end=start_col + len(val),
                        help_msg=(
                            "FORCE_WAIT_TIME must be a "
                            "positive float (e.g., '0.5')"
                        ),
                    )

                    return Err(
                        ConfigError.ERR_INVALID_FORCE_WAIT_TIME,
                        diag,
                    )

            case "WALL_COLOR":
                parts = [part.strip() for part in val.split(",")]
                if len(parts) != 3:
                    start_col = raw_line.find(val)

                    diag = Diagnostic(
                        filename=config_file,
                        line_num=idx,
                        line_text=raw_line,
                        col_start=start_col,
                        col_end=start_col + len(val),
                        help_msg="WALL_COLOR must contain three "
                        "RGB integers (e.g., '184,2,44')",
                    )

                    return Err(ConfigError.ERR_INVALID_WALL_COLOR, diag)

                try:
                    rgb = tuple(int(part) for part in parts)
                    if any(channel < 0 or channel > 255 for channel in rgb):
                        raise ValueError
                except ValueError:
                    start_col = raw_line.find(val)

                    diag = Diagnostic(
                        filename=config_file,
                        line_num=idx,
                        line_text=raw_line,
                        col_start=start_col,
                        col_end=start_col + len(val),
                        help_msg="WALL_COLOR channels must be"
                        " integers from 0 to 255",
                    )

                    return Err(ConfigError.ERR_INVALID_WALL_COLOR, diag)

                config.wall_color = (rgb[0], rgb[1], rgb[2])

            case _:
                start_col = 0
                max_allowed_distance = min(3, max(1, int(len(key) * 0.4)))
                best_match, dist = min(
                    (
                        (k, levenshteinRecursive(key, k, len(key), len(k)))
                        for k in valid_keys
                    ),
                    key=lambda item: (
                        item[1],
                        -_common_prefix_len(key, item[0]),
                        abs(len(key) - len(item[0])),
                        item[0],
                    ),
                )
                if dist <= max_allowed_distance:
                    help_msg = f"Unknown configuration"\
                        f"key '{key}'. Did you mean '{best_match}'?"
                else:
                    help_msg = f"Unknown configuration key '{key}'"

                diag = Diagnostic(
                    filename=config_file,
                    line_num=idx,
                    line_text=raw_line,
                    col_start=start_col,
                    col_end=len(key),
                    help_msg=help_msg,
                )
                return Err(ConfigError.ERR_INVALID_SYNTAX, diag)

    if required_keys:
        missing_str = ", ".join(sorted(required_keys))

        diag = Diagnostic(
            filename=config_file,
            line_num=len(lines) if lines else 1,
            line_text=lines[-1] if lines else "",
            col_start=0,
            col_end=1,
            help_msg=(
                f"Missing mandatory configuration options: {missing_str}"
            ),
        )

        return Err(ConfigError.ERR_INVALID_SYNTAX, diag)

    return Ok(config)


def levenshteinRecursive(
    str1: str, str2: str, len_str1: int, len_str2: int
) -> int:
    """Calculates the Levenshtein distance between two strings recursively."""
    if len_str1 == 0:
        return len_str2
    if len_str2 == 0:
        return len_str1
    if str1[len_str1 - 1] == str2[len_str2 - 1]:
        return levenshteinRecursive(str1, str2, len_str1 - 1, len_str2 - 1)
    return 1 + min(
        levenshteinRecursive(str1, str2, len_str1, len_str2 - 1),
        min(
            levenshteinRecursive(str1, str2, len_str1 - 1, len_str2),
            levenshteinRecursive(str1, str2, len_str1 - 1, len_str2 - 1),
        ),
    )


def _common_prefix_len(str1: str, str2: str) -> int:
    """Return the number of leading characters shared by two strings."""

    count = 0
    for char1, char2 in zip(str1, str2, strict=False):
        if char1 != char2:
            break
        count += 1
    return count
