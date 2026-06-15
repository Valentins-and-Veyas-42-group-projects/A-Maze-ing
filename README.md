_This project has been created as part of the 42 curriculum by vsack, sfurst_

## Description

This project is primarily about Maze generation and solving but also a big part
is Terminal visualization in python.

The subject requires atleast one maze generation
algorithm and terminal or MLX visualization. We implemented 3 generation algs
and 2 solving algorithms.
<br>These are as follows:

### Generation <br>
#### 1. DFS (depth first search):<br>
This is a reductive algorithm meaning it starts with all cells of the maze having walls in each direction
and it removes the walls during generation opposed to putting new walls in.<br>
It has 3 lists called `stack`, `visited` and `candidates`.
It starts at the entry cell and begins adding valid candidate cells to the candidates list. A valid candidate must be:<br>
1. Inbounds of the grid
2. Not already visited
3. Not be inside the logo in the middle

Once atleast one valid candidate has been found we pick a random candidate and remove the wall between it and the stack cell.
The chosen cell is then pushed onto the stack and becomes the new current cell. When no valid candidates exist the stack pops back to the previous cell. This continues until the stack is empty meaning every reachable cell has been visited.

#### 2. Binary Tree:<br>
This is a also reductive algorithm 
and it removes the walls during generation opposed to putting new walls in.<br>
It visits every cell in the grid in reading order (left to right, top to bottom). For each cell it looks at two possible directions to carve: `NORTH` and `EAST`. A direction is valid if:<br>
1. The neighbor in that direction is inbounds
2. The neighbor is not inside the logo in the middle

Once the valid options are collected, one is picked at random and the wall between the current cell and that neighbor is removed. If neither direction is valid (top-right corner) nothing happens. This produces a maze with a noticeable diagonal flow toward the top-right corner.

#### 3. Prim's Algorithm:<br>
This is again reductive algorithm 
and it removes the walls during generation opposed to putting new walls in.<br>
It has 3 lists called `frontier`, `visited` and `visited_neighbors`. It starts at the entry cell, marks it visited, and adds all its valid neighbors to the frontier. A valid frontier candidate must be:<br>
1. Inbounds of the grid
2. Not already visited
3. Not be inside the logo in the middle

Each step picks a random cell from the frontier, then looks at its neighbors that are already visited. One of those visited neighbors is picked at random and the wall between them is removed, connecting the new cell to the existing maze. The new cell's unvisited neighbors are then added to the frontier.

### Solving <br>
#### 1. BFS (breadth first search):<br>
Explores cells layer by layer outward from the entry using a queue. Guarantees the shortest path to the exit.

#### 2. DFS (depth first search):<br>
Explores cells by going as deep as possible along one branch before backtracking, using a stack. Does not guarantee the shortest path.

### Loop mode
If `PERFECT = False` in the config, all three generation algorithms remove an additional ~25% of walls after generation (skipping any removal that would create a 3x3 open area). This turns a perfect maze into one with multiple valid paths.

---

## Instructions

### Requirements
- Python 3.10 or later
- `uv` (recommended) or `pip`

### Install
```
make install
```
Or with pip directly:
```
make install-pip
```

### Run
```
make run
```
Or manually:
```
python3 a_maze_ing.py config.txt
```

### Other Makefile targets
| Target | Description |
|---|---|
| `make debug` | Run with pdb debugger |
| `make clean` | Remove `__pycache__`, `.mypy_cache`, etc. |
| `make lint` | Run flake8 + mypy |
| `make lint-strict` | Run flake8 + mypy --strict |
| `make test` | Run pytest |

---

## Configuration file format

The config file uses `KEY = VALUE` pairs, one per line. Lines starting with `#` are comments and are ignored.

### Mandatory keys

| Key | Type | Description | Example |
|---|---|---|---|
| `WIDTH` | int > 0 | Maze width in cells | `WIDTH = 70` |
| `HEIGHT` | int > 0 | Maze height in cells | `HEIGHT = 50` |
| `ENTRY` | x,y | Entry cell coordinates | `ENTRY = 0,0` |
| `EXIT` | x,y | Exit cell coordinates | `EXIT = 55,42` |
| `OUTPUT_FILE` | str | Output filename | `OUTPUT_FILE = maze.txt` |
| `PERFECT` | True/False | Enforce exactly one path | `PERFECT = False` |

### Optional keys

| Key | Type | Default | Description |
|---|---|---|---|
| `ALGORITHM` | 1/2/3 | 1 | Generation algorithm: 1=DFS, 2=Binary Tree, 3=Prim's |
| `SEED` | str | None | Seed for reproducible generation |
| `ANIMATION` | True/False | False | Animate generation step by step |
| `SHOW_PATH` | True/False | False | Show solution path on start |
| `SPEED` | int > 0 | 1 | Animation speed the number dictates how many frames are skipped during animation|
| `FORCE_WAIT_TIME` | float > 0 | 0.5 | Seconds between animation frames |
| `WALL_COLOR` | R,G,B | None | Wall color as 0-255 RGB values |
| `VERBOSE` | True/False | False | Enable verbose output |

---

## Reusable module

The maze generator is packaged as a standalone pip-installable module called `mazegen`.

### Install the package
```
pip install mazegen-*.whl
```

### Basic usage
```python
from mazegen.generator import MazeGenerator

gen = MazeGenerator(width=20, height=15, entry=(0, 0), exit=(19, 14), perfect=True)
gen.generate()          # DFS — or gen.bin_tree() / gen.prims_algorithm()

grid = gen.grid         # list[list[int]], one hex value per cell
solution = gen.solver() # returns Ok("NESW...") or Err(...)
output = gen.output()   # returns the formatted output file string
```

### Cell encoding
Each cell is a 4-bit integer where a set bit means a wall is closed:

| Bit | Direction |
|---|---|
| 0 (LSB) | North |
| 1 | East |
| 2 | South |
| 3 | West |

Example: `0xF` (15) = all walls closed. `0x0` = no walls.

### Build the package from source
```
pip install build
python -m build
```
This produces `mazegen-*.whl` and `mazegen-*.tar.gz` in the `dist/` directory.

---

## Why these algorithms

We chose DFS as the first algorithm because we were already familiar with the 
backtracking concept from BSQ and the tower game rush. Also it seemed like 
the most efficent from inuition which isnt technically true but it is still 
very efficient. Binary Tree was the second implemented algorithm primarily
because of how easy it was to implement and the interesting patterns it produces.
Prim's algorithm was the last one implemented because it seemed interesting. 
It is pretty similar to DFS but when watching youtube videos on maze generation
I liked how it looked.

For solving we first implemented DFS because we already did it for generation so
translating to a solver wasnt difficult. It worked fine on perfect mazes but 
when we implemented imperfect mazes we saw that it does not always find the 
shortest path which is required in the subject. Thats why we implemented BFS next
as the primary solver which always finds the shortest path in imperfected mazes.

---

## Team and project management

### Roles:
#### Valentin:
Generation/Solving logic<br>
Visualizer
#### Veya:
Parsing<br>
Error handling<br>
Testing<br>

### Planning:

TODO!!!


## Resources

BFS explanation: https://www.geeksforgeeks.org/python/python-program-for-breadth-first-search-or-bfs-for-a-graph/
DFS explanation: https://www.geeksforgeeks.org/python/python-program-for-depth-first-search-or-dfs-for-a-graph/
Video with different algs: https://www.youtube.com/watch?v=cQVH4gcb3O4&t=4s
Another Video with algs: https://www.youtube.com/watch?v=sVcB8vUFlmU
Curses documentation: https://www.w3schools.com/python/ref_module_curses.asp
Curses tutorial: https://codedrome.substack.com/p/an-introduction-to-curses-in-python



### AI usage

In the beginning we used AI for a simple visualizer to help understand what all 
the changes to the code where doing. That code was removed when the visualizer 
was rewritten by hand. AI was used for refactoring the code and adding docstrings
to some methods and functions. We tried to keep AI usage low to learn more in the end.
No AI code was used in this project.
