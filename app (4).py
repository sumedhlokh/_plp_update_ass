"""
Maze Solver Robot - Streamlit demo
Python port of maze_solver.cpp.

Finds the BEST (shortest) path through a maze by exploring every
possible route with backtracking, then keeping the shortest one found.

Concepts: Abstract class, Child class, Encapsulation, Stack (push/pop)

Run:  streamlit run app.py
"""
import streamlit as st

DIRS = {"UP": (-1, 0), "RIGHT": (0, 1), "DOWN": (1, 0), "LEFT": (0, -1)}

WALL, OPEN, PATH, INK = "#1F2F30", "#EAF4F2", "#F2A541", "#0F3D3E"


# =====================================================
#  MAZE  (Encapsulation: grid and goal are private)
# =====================================================
class Maze:
    def __init__(self, layout):
        self.__grid = [list(row) for row in layout]
        self.__goal = (0, 0)
        for r, row in enumerate(self.__grid):
            for c, ch in enumerate(row):
                if ch == "G":
                    self.__goal = (r, c)

    def is_wall(self, r, c):
        if r < 0 or c < 0 or r >= self.rows() or c >= self.cols():
            return True
        return self.__grid[r][c] == "#"

    def is_goal(self, pos):
        return pos == self.__goal

    def get_start(self):
        for r, row in enumerate(self.__grid):
            for c, ch in enumerate(row):
                if ch == "S":
                    return (r, c)
        return (0, 0)

    def rows(self):
        return len(self.__grid)

    def cols(self):
        return len(self.__grid[0])

    def symbol(self, r, c):
        return self.__grid[r][c]


# =====================================================
#  ROBOT  (Abstract class: cannot be created directly)
# =====================================================
class Robot:
    def __init__(self, maze):
        self._maze = maze
        self._pos = maze.get_start()
        self.cells_checked = 0

    def _next_cell(self, pos, direction):
        dr, dc = DIRS[direction]
        return (pos[0] + dr, pos[1] + dc)

    def solve(self):                 # pure virtual: HOW to search
        raise NotImplementedError

    def get_best_path(self):         # pure virtual: the answer found
        raise NotImplementedError


# =====================================================
#  SMART ROBOT  (Child class)
#  Explores every path using backtracking, keeps the shortest one.
# =====================================================
class SmartRobot(Robot):
    def __init__(self, maze):
        super().__init__(maze)
        self.__visited = {self._pos}
        self.__current_path = [self._pos]
        self.__best_path = None

    def __explore(self):
        current = self.__current_path[-1]

        if self._maze.is_goal(current):
            if self.__best_path is None or len(self.__current_path) < len(self.__best_path):
                self.__best_path = list(self.__current_path)   # found a shorter route
            return

        for d in ("UP", "RIGHT", "DOWN", "LEFT"):
            n = self._next_cell(current, d)
            self.cells_checked += 1
            if not self._maze.is_wall(n[0], n[1]) and n not in self.__visited:
                self.__visited.add(n)
                self.__current_path.append(n)     # PUSH: step into this cell
                self.__explore()                   # go deeper (recursion = a stack)
                self.__current_path.pop()          # POP: undo the step (backtrack)
                self.__visited.remove(n)           # un-mark, so other routes can reuse it

    def solve(self):
        self.__explore()

    def get_best_path(self):
        return self.__best_path or []


# =====================================================
#  DRAWING HELPERS
# =====================================================
PRESETS = {
    "Maze 1 - small": [
        "#########",
        "#S..#...#",
        "#.#.#.#.#",
        "#.#...#G#",
        "#########",
    ],
    "Maze 2 - multiple routes": [
        "###########",
        "#S........#",
        "#.##.###.##",
        "#....#....#",
        "#.##.#.##.#",
        "#....#....#",
        "##.#####.##",
        "#.........#",
        "#.##.#.##.#",
        "#....#...G#",
        "###########",
    ],
    "Custom (edit below)": [
        "#########",
        "#S......#",
        "#.#####.#",
        "#......G#",
        "#########",
    ],
}

MAX_CELLS = 20 * 20   # safety limit: exhaustive search is slow on big mazes


def parse_layout(text):
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if not lines:
        return None, "The maze is empty."
    if len({len(ln) for ln in lines}) != 1:
        return None, "All rows must have the same length."
    joined = "".join(lines)
    if set(joined) - set("#.SG"):
        return None, "Use only  #  .  S  G  characters."
    if joined.count("S") != 1 or joined.count("G") != 1:
        return None, "The maze needs exactly one S and one G."
    if len(lines) * len(lines[0]) > MAX_CELLS:
        return None, f"Maze is too big for exhaustive search (max {MAX_CELLS} cells, e.g. 20x20)."
    return lines, None


def cell_html(bg, txt="", fg="#22323A", size=34):
    return (f"<div style='width:{size}px;height:{size}px;background:{bg};color:{fg};display:flex;"
            f"align-items:center;justify-content:center;font-weight:700;"
            f"border-radius:4px;font-size:{max(10, size // 2)}px'>{txt}</div>")


def maze_html(maze, path):
    on_path = set(path)
    size = max(14, min(34, 700 // maze.cols()))
    rows = []
    for r in range(maze.rows()):
        cells = []
        for c in range(maze.cols()):
            sym = maze.symbol(r, c)
            if sym == "#":
                cells.append(cell_html(WALL, size=size))
            elif sym in "SG":
                cells.append(cell_html(INK, sym if size >= 16 else "", "#FFFFFF", size=size))
            elif (r, c) in on_path:
                cells.append(cell_html(PATH, size=size))
            else:
                cells.append(cell_html(OPEN, size=size))
        rows.append("<div style='display:flex;gap:2px'>" + "".join(cells) + "</div>")
    return "<div style='display:flex;flex-direction:column;gap:2px'>" + "".join(rows) + "</div>"


# =====================================================
#  STREAMLIT PAGE
# =====================================================
st.set_page_config(page_title="Maze Solver - Best Path", page_icon="🤖", layout="wide")
st.title("🤖 Maze Solver Robot - Best Path")
st.caption("Explores every possible route, then keeps the shortest one it found.")

with st.sidebar:
    st.header("Settings")
    choice = st.selectbox("Choose a maze", list(PRESETS))
    text = st.text_area(
        "Maze layout (# wall, . open, S start, G goal)",
        "\n".join(PRESETS[choice]),
        height=220,
    )
    st.markdown(
        "**Legend**  \n🟧 cells on the best path  \n⬛ wall  \n"
        "Max maze size: 20 x 20 (exhaustive search gets slow on bigger maps)"
    )

layout, error = parse_layout(text)
if error:
    st.error(error)
    st.stop()

maze = Maze(layout)
robot = SmartRobot(maze)
robot.solve()
path = robot.get_best_path()

m1, m2, m3 = st.columns(3)
m1.metric("Result", "Path found ✅" if path else "No path ❌")
m2.metric("Best path length (cells)", len(path) if path else 0)
m3.metric("Cells checked", robot.cells_checked)

st.markdown(maze_html(maze, path), unsafe_allow_html=True)

with st.expander("How does it work?"):
    st.markdown("""
The robot explores the maze using **backtracking** (a form of DFS that tries every branch):

1. Step into a cell and **push** it onto the current path.
2. Try every direction (up, right, down, left) from there, one at a time, by exploring each recursively.
3. If it reaches `G`, compare this route's length to the best one found so far, and keep whichever is shorter.
4. Either way, **pop** that cell off the path afterwards and un-mark it as visited, so other routes can reuse it.
5. Repeat until every possible path has been tried.

**OOP used:** `Robot` is an abstract class (`solve` and `get_best_path` are not implemented there),
`SmartRobot` is its child class, `Maze` keeps its grid private (encapsulation),
and the current path is built and undone like a **stack** (push / pop).

**Why not just stop at the first path found?** A first-found path (plain DFS) is not
guaranteed to be the shortest. Checking every path guarantees the best answer,
at the cost of checking many more cells — the "Cells checked" number above shows that trade-off.
""")
