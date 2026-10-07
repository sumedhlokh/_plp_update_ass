# Maze Solver Robot - Best Path

A robot finds the **shortest possible path** through a maze. It explores
every route using backtracking, and keeps only the shortest complete
route it finds.

Built in **C++** (main project) with a **Streamlit** web demo (Python port).

## Concepts covered

| Concept | Where |
|---|---|
| Abstract class | `Robot` (`solve`, `getBestPath` are not implemented there) |
| Child class | `SmartRobot` |
| Encapsulation | `Maze` keeps its grid and goal private |
| Stack | the current path: push when stepping forward, pop when backtracking |

## Project structure

```
maze-solver-dfs/
├── maze_solver.cpp      C++ project (main submission)
├── app.py               Streamlit demo (Python)
├── requirements.txt
└── README.md
```

## Run the C++ version

```
g++ -std=c++11 maze_solver.cpp -o maze_solver
./maze_solver
```

## Run the Streamlit demo

```
pip install -r requirements.txt
streamlit run app.py
```

Pick a maze from the dropdown, or paste your own in the text box
(use `#` for wall, `.` for open floor, `S` for start, `G` for goal).
The app shows the best path it found, its length, and how many cells
it had to check to be sure it was the shortest.

## Live demo

Add your Streamlit Cloud link here after deploying.

## How it works

1. Step into a cell and push it onto the current path.
2. Try every direction (up, right, down, left) from there.
3. If the goal is reached, compare this route to the shortest one found
   so far, and keep whichever is shorter.
4. Pop that cell off the path afterwards (backtrack), so other routes
   can be tried.
5. Repeat until every possible path has been explored.

**Note:** this checks every path, so it guarantees the best answer but
is slow on large mazes (keep maze size to about 20x20 or smaller).
Real systems like Google Maps use smarter algorithms (such as Dijkstra's
algorithm or A*) that skip checking most roads, so they stay fast on
huge maps.
