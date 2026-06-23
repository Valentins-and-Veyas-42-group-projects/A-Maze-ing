_This project was created as part of the 42 curriculum by vsack and sfurst._

## Description

This project is primarily about maze generation and solving, but also features terminal visualization in Python.

The subject requires at least one maze generation algorithm and terminal or MLX visualization. We implemented 3 generation algorithms and 2 solving algorithms.

These are as follows:

### Generation

#### 1. DFS (Depth First Search)
This is a reductive algorithm, meaning it starts with all cells of the maze having walls in each direction and removes the walls during generation, as opposed to putting new walls in.
It utilizes 3 lists: `stack`, `visited`, and `candidates`.
It starts at the entry cell and begins adding valid candidate cells to the candidates list. A valid candidate must be:
1. Within the bounds of the grid.
2. Not already visited.
3. Not inside the logo in the middle.

Once at least one valid candidate has been found, we pick a random candidate and remove the wall between it and the stack cell.
The chosen cell is then pushed onto the stack and becomes the new current cell. When no valid candidates exist, the stack pops back to the previous cell. This continues until the stack is empty, meaning every reachable cell has been visited.

#### 2. Binary Tree
This is also a reductive algorithm that removes walls during generation, as opposed to putting new walls in.
It visits every cell in the grid in reading order (left to right, top to bottom). For each cell, it looks at two possible directions to carve: `NORTH` and `EAST`. A direction is valid if:
1. The neighbor in that direction is within bounds.
2. The neighbor is not inside the logo in the middle.

Once the valid options are collected, one is picked at random and the wall between the current cell and that neighbor is removed. If neither direction is valid (top-right corner), nothing happens. This produces a maze with a noticeable diagonal flow toward the top-right corner.

#### 3. Prim's Algorithm
This is also a reductive algorithm that removes walls during generation, as opposed to putting new walls in.
It utilizes 3 lists: `frontier`, `visited`, and `visited_neighbors`. It starts at the entry cell, marks it visited, and adds all its valid neighbors to the frontier. A valid frontier candidate must be:
1. Within the bounds of the grid.
2. Not already visited.
3. Not inside the logo in the middle.

Each step picks a random cell from the frontier, then looks at its neighbors that are already visited. One of those visited neighbors is picked at random and the wall between them is removed, connecting the new cell to the existing maze. The new cell's unvisited neighbors are then added to the frontier.

### Solving

#### 1. BFS (Breadth First Search)
Explores cells layer by layer outward from the entry using a queue. Guarantees the shortest path to the exit.

#### 2. DFS (Depth First Search)
Explores cells by going as deep as possible along one branch before backtracking, using a stack. Does not guarantee the shortest path.

### Loop Mode
If `PERFECT = False` in the config, all three generation algorithms remove an additional ~25% of walls after generation (skipping any removal that would create a 3x3 open area). This turns a perfect maze into one with multiple valid paths.

---

## Instructions

### Requirements
- Python 3.10 or later
- `uv` (recommended) or `pip`

### Install
```bash
make install
```
Or with pip directly:
```bash
make install-pip
```

### Run
```bash
make run
```
Or manually:
```bash
python3 a_maze_ing.py config.txt
```

### Other Makefile Targets

| Target | Description |
|---|---|
| `make build` / `make build-package` | Build the wheel and source distribution packages and copy them to the root |
| `make debug` | Run with pdb debugger |
| `make clean` | Remove build artifacts, root package files, `__pycache__`, etc. |
| `make lint` | Run flake8 + mypy |
| `make lint-strict` | Run flake8 + mypy --strict |
| `make typecheck` | Run mypy, ty, and pyright |
| `make check-modern` | Run ruff and ty |
| `make test` | Run pytest |

---

## Configuration File Format

The config file uses `KEY = VALUE` pairs, one per line. Lines starting with `#` are comments and are ignored.

### Mandatory Keys

| Key | Type | Description | Example |
|---|---|---|---|
| `WIDTH` | int > 0 | Maze width in cells | `WIDTH = 70` |
| `HEIGHT` | int > 0 | Maze height in cells | `HEIGHT = 50` |
| `ENTRY` | x,y | Entry cell coordinates | `ENTRY = 0,0` |
| `EXIT` | x,y | Exit cell coordinates | `EXIT = 55,42` |
| `OUTPUT_FILE` | str | Output filename | `OUTPUT_FILE = maze.txt` |
| `PERFECT` | True/False | Enforce exactly one path | `PERFECT = False` |

### Optional Keys

| Key | Type | Default | Description |
|---|---|---|---|
| `ALGORITHM` | 1/2/3 | 1 | Generation algorithm: 1=DFS, 2=Binary Tree, 3=Prim's |
| `SEED` | str | None | Seed for reproducible generation |
| `ANIMATION` | True/False | False | Animate generation step by step |
| `SHOW_PATH` | True/False | False | Show solution path on start |
| `SPEED` | int > 0 | 1 | Animation speed; the number dictates how many frames are skipped during animation. |
| `WALL_COLOR` | R,G,B | None | Wall color as 0-255 RGB values |

---

## Reusable Module

The maze generator is packaged as a standalone, pip-installable module called `mazegen`.

### Build and Install the Package

To build the wheel and source distribution package and place them at the root of the repository:
```bash
make build-package
```
This runs the standard python/uv build and copies the resulting package files to the root directory:
- `mazegen-1.0.0-py3-none-any.whl` (pip-installable wheel package)
- `mazegen-1.0.0.tar.gz` (pip-installable source distribution)

You can also run:
```bash
make install
```
which builds the package and performs editable installation with all dev tools.

To install the wheel package from the root of the repository via pip:
```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic Usage

Below is a basic example of using the module programmatically to generate and solve a maze:

```python
from mazegen import MazeGenerator, Ok, Err

# Initialize the generator with size (width/height), entry/exit, perfect/imperfect mode, and custom seed
gen = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    perfect=True,
    seed="my_custom_seed_value"  # Seed can be string or integer (optional)
)

# Generate using one of the algorithms (returns Ok[None] or Err[MazeError])
result = gen.generate()  # Randomized DFS
# Alternatively:
# result = gen.bin_tree()  # Binary Tree
# result = gen.prims_algorithm()  # Prim's Algorithm

if isinstance(result, Ok):
    # Access the generated structure directly:
    grid = gen.grid          # list[list[int]]: a 2D grid representing cell wall states (4-bit encoding)
    
    # Access the solution path:
    solution = gen.solver()  # Returns Ok(path_string) (e.g., "NESW...") or Err(MazeError)
    
    if isinstance(solution, Ok):
        print(f"Path to exit: {solution.value}")
    else:
        print(f"Failed to solve: {solution.error}")
        
    output_res = gen.output() # Returns the formatted output string or Err(MazeError)
    if isinstance(output_res, str):
        print(f"Formatted output:\n{output_res}")
else:
    print(f"Failed to generate: {result.error}")
```

### Cell Encoding

Each cell is a 4-bit integer where a set bit means a wall is closed:

| Bit | Direction |
|---|---|
| 0 (LSB) | North |
| 1 | East |
| 2 | South |
| 3 | West |

Example: `0xF` (15) = all walls closed. `0x0` = no walls.

### Configuration Parsing

The module exports a robust configuration parser `parse_config` along with its typed model `Config`. This allows you to easily load configuration files matching the syntax of `config.txt` directly.

#### Using `parse_config` in your Code

```python
from mazegen import parse_config, MazeGenerator, Ok, Err

# Parse the config file
config_result = parse_config("config.txt")

if isinstance(config_result, Ok):
    config = config_result.value  # Access the parsed Config object
    
    # Instantiate the MazeGenerator using the parsed configuration properties
    generator = MazeGenerator(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit=config.exits,  # NOTE: config.exits is used for the generator's exit
        perfect=config.perfect
    )
    
    # Choose and execute the algorithm based on config
    match config.algorithm:
        case 1:
            generator.generate()
        case 2:
            generator.bin_tree()
        case 3:
            generator.prims_algorithm()
            
    # Write output to the configured file
    output_result = generator.output()
    if isinstance(output_result, str):
        with open(config.output_file, "w", encoding="utf-8") as f:
            f.write(output_result)
        print(f"Successfully generated and wrote maze to {config.output_file}")
    else:
        print(f"Error formatting output: {output_result.error}")

else:
    # Handle parsing errors (e.g., file not found, syntax errors, invalid values)
    print(f"Config parsing failed with error code: {config_result.error}")
    if config_result.diagnostic:
        # Prints a beautiful, Rust-style diagnostic with pinpoint carets pointing to the source file
        config_result.print_diagnostic()
```

#### The `Config` Data Class Fields

When `parse_config` succeeds, it returns a `Config` dataclass containing the following fields:

| Field | Type | Default | Description |
|---|---|---|---|
| `width` | `int` | *Required* | Width of the maze in cells. |
| `height` | `int` | *Required* | Height of the maze in cells. |
| `entry` | `tuple[int, int]` | *Required* | The `(x, y)` coordinate of the entrance. |
| `exits` | `tuple[int, int]` | *Required* | The `(x, y)` coordinate of the exit. |
| `output_file` | `str` | `"output.txt"` | Target output file path. |
| `perfect` | `bool` | `False` | Whether to enforce a perfect maze (exactly one path). |
| `verbose` | `bool` | `False` | Enable verbose command-line diagnostics logging. |
| `animation` | `bool` | `False` | Flag to enable animated rendering during generation. |
| `show_path` | `bool` | `False` | Flag to display the solution path on initialization. |
| `force_wait_time`| `float` | `0.5` | Wait time configuration in seconds for curses steps. |
| `speed` | `int` | `1` | Frames to skip during animated generation. |
| `algorithm` | `int` | `1` | Chosen generation algorithm (1=DFS, 2=Binary Tree, 3=Prim's). |
| `seed` | `str \| None` | `None` | Seed value for reproducing specific configurations. |
| `wall_color` | `tuple[int, int, int] \| None` | `None` | RGB tuple specifying the custom wall color. |

---

### Error Handling & Result Types

To avoid unexpected runtime exceptions and promote robust error handling, `mazegen` does not raise exceptions. Instead, it utilizes a Rust-like union type result pattern using generic `Ok` and `Err` wrapper classes.

#### The `Ok` and `Err` Result Wrappers

* **`Ok[T]`**: Represents success. Contains the computed value in the `.value` field.
* **`Err[E]`**: Represents failure. Contains the error enum variant in the `.error` field, and optionally a `Diagnostic` object in the `.diagnostic` field.

#### Maze Operation Errors: `MazeError`

Returned by methods on `MazeGenerator` (like `.generate()`, `.solver()`, and `.output()`).

| Enum Variant | Description |
|---|---|
| `INVALID_WIDTH` | Provided width is less than or equal to 0. |
| `INVALID_HEIGHT` | Provided height is less than or equal to 0. |
| `INVALID_ENTRY` | The entry coordinate is out of bounds of the maze grid. |
| `INVALID_EXIT` | The exit coordinate is out of bounds of the maze grid. |
| `ENTRY_EXIT_SAME` | The entrance and exit coordinates are identical. |
| `INVALID_PATH` | The solved path contains invalid steps or moves. |
| `NO_PATH_FOUND` | No path exists between the entry and exit. |
| `NO_42_LOGO` | Stamping the 42 logo failed or was not found in the grid. |

#### Config Validation Errors: `ConfigError`

Returned by `parse_config()` when parsing configuration files.

| Enum Variant | Description |
|---|---|
| `ERR_FILE_NOT_FOUND` | The specified configuration file could not be found. |
| `ERR_CANT_OPEN_FILE` | Permission error or file lock issue while opening the file. |
| `ERR_INVALID_SYNTAX` | Syntactically invalid line (e.g., missing `=` separator or malformed keys). |
| `ERR_INVALID_WIDTH` | `WIDTH` is missing or not a positive integer. |
| `ERR_INVALID_HEIGHT` | `HEIGHT` is missing or not a positive integer. |
| `ERR_INVALID_ENTRY` | `ENTRY` coordinates are malformed or missing numbers. |
| `ERR_INVALID_EXIT` | `EXIT` coordinates are malformed or missing numbers. |
| `ERR_INVALID_OUTPUT_FILE` | `OUTPUT_FILE` is empty or contains forbidden characters. |
| `ERR_INVALID_PERFECT` | `PERFECT` value is not 'True' or 'False'. |
| `ERR_INVALID_ANIMATION` | `ANIMATION` value is not 'True' or 'False'. |
| `ERR_INVALID_SHOW_PATH` | `SHOW_PATH` value is not 'True' or 'False'. |
| `ERR_INVALID_SPEED` | `SPEED` is not a positive integer. |
| `ERR_INVALID_ALGORITHM` | `ALGORITHM` is not 1/2/3, or not matching DFS/BINARY/PRIM. |
| `ERR_INVALID_WALL_COLOR` | `WALL_COLOR` channels are not a valid 3-channel RGB tuple (0-255). |

#### Rust-Style Diagnostics

When a `ConfigError` occurs, the `Err` object contains a `Diagnostic` object inside its `.diagnostic` field. The `Diagnostic` class keeps track of the:
- `filename`: Config file name.
- `line_num`: Line number where the error was detected (1-indexed).
- `line_text`: Raw contents of that line.
- `col_start` & `col_end`: Exact columns where the invalid token resides.
- `help_msg`: Descriptive suggestions for fixing the issue.

Calling `.print_diagnostic()` on the `Err` instance prints a highly readable visual traceback:

```text
Error: mazegen::config::invalid::width

 × Configuration validation failed
   ╭─[config.txt:3:9]
 3 │ WIDTH = -10
   ·         ╰─── ^^^
   
   help: WIDTH must be a positive integer (e.g., '20')
```

---

### How to Extend the Module

The `mazegen` package is designed to be extensible. Here are common ways you can expand its capabilities:

1. **Add Custom Generation Algorithms**:
   Implement a new method inside [generator.py](file:///home/veya/coding/42/cc/mazeslop/mazegen/generator.py) (e.g., `kruskals_algorithm()` or `recursive_division()`). Ensure it calls `self._validate()` first, initializes the grid, stamps the 42 logo, and updates `self.grid` and `self.cursor` as it carves passages.
2. **Add Custom Logo Stamps**:
   Extend the shapes in [patterns.py](file:///home/veya/coding/42/cc/mazeslop/mazegen/patterns.py). You can define a new `Pattern` subclass with custom character arrays that specify which cells contain the stamped layout.
3. **Custom Step Listeners (Callbacks)**:
   All generation methods take an optional `on_step: Callable[[], None]` callback. You can hook custom CLI visualizations, step counters, or diagnostic logs directly into the generation loop by passing your own handler:
   ```python
   def step_listener():
       print(f"Carving... Cursor currently at: {generator.cursor}")
   
   generator.generate(on_step=step_listener)
   ```
4. **Custom Output Formats**:
   Customize output serialization in `output.py` to support whatever you desire, extending the CLI's utility.

---

## Why These Algorithms

We chose DFS as the first algorithm because we were already familiar with the backtracking concept from BSQ and the tower game rush. Also, it seemed like the most efficient from intuition, which is not technically true, but it is still very efficient. Binary Tree was the second implemented algorithm, primarily because of how easy it was to implement and the interesting patterns it produces. Prim's algorithm was the last one implemented because it seemed interesting. It is pretty similar to DFS, but when watching YouTube videos on maze generation, I liked how it looked.

For solving, we first implemented DFS because we already did it for generation, so translating to a solver was not difficult. It worked fine on perfect mazes, but when we implemented imperfect mazes, we saw that it does not always find the shortest path, which is required in the subject. That is why we implemented BFS next as the primary solver, which always finds the shortest path in imperfect mazes.

---

## Team and Project Management

### Roles and Collaboration

On paper, we split the technical tasks to get things done faster. In practice, our planning was completely collaborative—we threw ideas around and tested them until we found something we liked, regardless of who suggested it.

#### Valentin
* Core maze generation and solving logic.
* Terminal visualizer implementation using `curses`.

#### Veya
* Config file parsing and data validation.
* Error handling and helping steer the coding style.
* Writing and running tests with `pytest`.

### Project Planning & Evolution

Our planning was highly iterative and driven by immediate testing. We began by building a simple visualizer early on, which gave us the visual feedback needed to correctly implement the generation algorithms and handle the center logo boundary. 

While we initially focused on DFS, implementing imperfect mazes made it clear that DFS couldn't guarantee the shortest path required by the subject. To fix this, we adapted our plan and implemented a BFS solver. The final phase of our project was spent refactoring the codebase, replacing early AI visualizer prototypes with our own hand-written logic, and structuring the project into a clean, installable module and adding unittests.

### Retrospective

#### What Worked Well
* **Openness to experimenting:** We tried a lot of different approaches and variations before settling on our final algorithms, which helped us understand the problem a lot better.
* **Quick feedback:** Working closely let us test ideas rapidly and change direction without losing momentum.

#### What Could Be Improved
* **Organization:** Our workflow was pretty informal. In the future, using a Kanban board, GitHub Projects, or a shared notes solution could keep tasks more organized and organized instead of just relying on casual tracking.

### Tools Used
* **Discord**: For communication.
* **GitHub**: For version control and tracking our code history.
---

## Resources

BFS explanation: https://www.geeksforgeeks.org/python/python-program-for-breadth-first-search-or-bfs-for-a-graph/<br>
DFS explanation: https://www.geeksforgeeks.org/python/python-program-for-depth-first-search-or-dfs-for-a-graph/<br>
Video with different algorithms: https://www.youtube.com/watch?v=cQVH4gcb3O4&t=4s<br>
Another video with algorithms: https://www.youtube.com/watch?v=sVcB8vUFlmU<br>
Curses documentation: https://www.w3schools.com/python/ref_module_curses.asp<br>
Curses tutorial: https://codedrome.substack.com/p/an-introduction-to-curses-in-python<br>

---

### AI Usage

In the beginning, we used AI for a simple visualizer to help understand what all the changes to the code were doing. That code was removed when the visualizer was rewritten by hand. AI was used for refactoring the code and adding docstrings to some methods and functions. We kept AI usage low for the final code to learn more in the end. AI was also used to create different visualizer prototypes to decide whether curses or textual would make more sense to use for the TUI. No AI code was used in the final version of the project.
