_This project has been created as part of the 42 curriculum by vsack,sfurst_

## Description

This project is primarily about Maze generation and solving but also a big part 
is Terminal visualization in python. 

The subject requires atleast one maze generation
algorithm and terminal or MLX visualization. We implemented 3 generation algs 
and 2 solving algorithms.
<br>These are as follows:

### Generation <br>
#### 1. BFS (breadth first search):<br>
This is a reductive algorithm meaning it starts with all cells of the maze having walls in each direction
and it removes the walls during generation opposed to putting new walls in.<br>
It has 3 lists  called `stack`,`visited` and `candidates`. 
It starts at the entry cell and begins adding valid candidate cells to the candidates list. A valid candidate must be:<br>
1. Inbounds of the grid
2. Not already visited
3. Not be inside the logo in the middle

Once atleast one valid candidate has been found we pick a random candidate and remove the wall between it and the stack cell. 
