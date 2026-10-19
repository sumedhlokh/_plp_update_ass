#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

struct Position { int row, col; };

class Maze {
private:
    vector<string> grid;
    Position goal;

public:
    Maze(vector<string> g) {
        grid = g;
        for (int r = 0; r < (int)grid.size(); r++)
            for (int c = 0; c < (int)grid[r].size(); c++)
                if (grid[r][c] == 'G') goal = {r, c};
    }

    bool isWall(int r, int c) {
        if (r < 0 || c < 0 || r >= (int)grid.size() || c >= (int)grid[0].size())
            return true;
        return grid[r][c] == '#';
    }

    bool isGoal(Position p) {
        return p.row == goal.row && p.col == goal.col;
    }

    Position getStart() {
        for (int r = 0; r < (int)grid.size(); r++)
            for (int c = 0; c < (int)grid[r].size(); c++)
                if (grid[r][c] == 'S') return {r, c};
        return {0, 0};
    }

    int rows() { return grid.size(); }
    int cols() { return grid[0].size(); }

    void display(vector<Position> path, char label) {
        vector<string> copy = grid;
        for (auto p : path)
            if (copy[p.row][p.col] == '.') copy[p.row][p.col] = label;
        for (auto row : copy) cout << row << "\n";
    }
};

class Robot {
protected:
    Maze* maze;
    Position pos;
    int cellsChecked = 0;

    Position nextCell(Position p, int dir) {
        if (dir == 0) return {p.row - 1, p.col};
        if (dir == 1) return {p.row, p.col + 1};
        if (dir == 2) return {p.row + 1, p.col};
        return {p.row, p.col - 1};
    }

public:
    Robot(Maze* m) { maze = m; pos = m->getStart(); }
    virtual ~Robot() {}

    virtual void solve() = 0;
    virtual vector<vector<Position>> getTopPaths(int k) = 0;

    int getCellsChecked() { return cellsChecked; }
};

class SmartRobot : public Robot {
private:
    vector<vector<bool>> visited;
    vector<Position> currentPath;
    vector<vector<Position>> allPaths;

    void explore() {
        Position current = currentPath.back();

        if (maze->isGoal(current)) {
            allPaths.push_back(currentPath);
            return;
        }

        for (int dir = 0; dir < 4; dir++) {
            Position n = nextCell(current, dir);
            cellsChecked++;
            if (!maze->isWall(n.row, n.col) && !visited[n.row][n.col]) {
                visited[n.row][n.col] = true;
                currentPath.push_back(n);
                explore();
                currentPath.pop_back();
                visited[n.row][n.col] = false;
            }
        }
    }

public:
    SmartRobot(Maze* m) : Robot(m) {
        visited.assign(m->rows(), vector<bool>(m->cols(), false));
    }

    void solve() override {
        currentPath.push_back(pos);
        visited[pos.row][pos.col] = true;
        explore();

        sort(allPaths.begin(), allPaths.end(),
             [](const vector<Position>& a, const vector<Position>& b) {
                 return a.size() < b.size();
             });
    }

    vector<vector<Position>> getTopPaths(int k) override {
        vector<vector<Position>> top;
        for (int i = 0; i < (int)allPaths.size() && i < k; i++)
            top.push_back(allPaths[i]);
        return top;
    }
};

int main() {
    vector<string> layout = {
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
        "###########"
    };

    Maze maze(layout);
    SmartRobot robot(&maze);

    robot.solve();
    vector<vector<Position>> top3 = robot.getTopPaths(3);

    cout << "Total routes checked (cells): " << robot.getCellsChecked() << "\n\n";

    if (top3.empty()) {
        cout << "No path found.\n";
        return 0;
    }

    char labels[3] = {'1', '2', '3'};
    for (int i = 0; i < (int)top3.size(); i++) {
        cout << "Route " << (i + 1) << "  (length: " << top3[i].size() << " cells)\n";
        maze.display(top3[i], labels[i]);
        cout << "\n";
    }

    return 0;
}
