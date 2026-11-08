"""BFS 求解器：验证每一关可解，并算出最少指令数（用来自动设定三星标准）"""
from collections import deque
import json

# 0=up 1=right 2=down 3=left
DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
NAME2D = {"up": 0, "right": 1, "down": 2, "left": 3}

LEVELS = [
    {
        "name": "第 1 关 · 一直往前走",
        "dir": "right",
        "map": [
            ".....",
            "S.C.H",
            ".....",
        ],
    },
    {
        "name": "第 2 关 · 学会转弯",
        "dir": "right",
        "map": [
            ".....",
            "....H",
            "S.C..",
        ],
    },
    {
        "name": "第 3 关 · 大石头挡路",
        "dir": "right",
        "map": [
            ".....",
            "S#C.H",
            ".....",
        ],
    },
    {
        "name": "第 4 关 · 两颗萝卜",
        "dir": "right",
        "map": [
            "......",
            ".###..",
            "..C...",
            "S.C.H.",
        ],
    },
    {
        "name": "第 5 关 · 学会跳跃",
        "dir": "right",
        "map": [
            ".....",
            "S#C.H",
            ".....",
            "..#..",
        ],
    },
    {
        "name": "第 6 关 · 绕来绕去",
        "dir": "right",
        "map": [
            ". . . . . .".replace(" ", ""),
            "S # # C . .".replace(" ", ""),
            ". . . # . .".replace(" ", ""),
            ". C . # . H".replace(" ", ""),
        ],
    },
    {
        "name": "第 7 关 · 跳过去",
        "dir": "up",
        "map": [
            "..#..H",
            "..#...",
            "S.#.C.",
            "..#...",
            "...C..",
        ],
    },
    {
        "name": "第 8 关 · 小迷宫",
        "dir": "right",
        "map": [
            "S.#...",
            "..#.#.",
            "C...C.",
            ".##.#.",
            "....#H",
        ],
    },
    {
        "name": "第 9 关 · 三颗萝卜",
        "dir": "up",
        "map": [
            "..#..C",
            ".C#...",
            "..#.#.",
            "S...#H",
            ".C....",
        ],
    },
    {
        "name": "第 10 关 · 终极挑战",
        "dir": "right",
        "map": [
            "S.C.#..",
            ".##.#..",
            "....#.C",
            ".#.....",
            ".#.##..",
            "C....#H",
        ],
    },
]


def solve(lv):
    g = lv["map"]
    rows, cols = len(g), len(g[0])
    for r in range(rows):
        assert len(g[r]) == cols, (lv["name"], r, len(g[r]), cols)
    carrots = set()
    home = None
    start = None
    for r in range(rows):
        for c in range(cols):
            ch = g[r][c]
            if ch == "C":
                carrots.add((r, c))
            elif ch == "H":
                home = (r, c)
            elif ch == "S":
                start = (r, c)
    assert home and start, lv["name"]
    all_c = frozenset(carrots)

    def wall(r, c):
        return r < 0 or c < 0 or r >= rows or c >= cols or g[r][c] == "#"

    d0 = NAME2D[lv["dir"]]
    init = (start[0], start[1], d0, frozenset())
    dq = deque([(init, 0)])
    seen = {init}
    best = None
    while dq:
        (r, c, d, got), n = dq.popleft()
        if (r, c) == home and got == all_c:
            best = n
            break
        nxt = []
        for cmd in ("M", "L", "R", "J"):
            if cmd == "M":
                nr, nc = r + DIRS[d][0], c + DIRS[d][1]
                if wall(nr, nc):
                    continue
                ng = got | ({(nr, nc)} & carrots)
                nxt.append((nr, nc, d, frozenset(ng)))
            elif cmd == "J":
                mr, mc = r + DIRS[d][0], c + DIRS[d][1]
                nr, nc = r + DIRS[d][0] * 2, c + DIRS[d][1] * 2
                if wall(nr, nc):
                    continue
                ng = got | ({(nr, nc)} & carrots)
                nxt.append((nr, nc, d, frozenset(ng)))
            elif cmd == "L":
                nxt.append((r, c, (d + 3) % 4, got))
            else:
                nxt.append((r, c, (d + 1) % 4, got))
        for s in nxt:
            if s not in seen:
                seen.add(s)
                dq.append((s, n + 1))
    return best, len(carrots), rows, cols


ok = True
for lv in LEVELS:
    best, nc, rows, cols = solve(lv)
    if best is None:
        ok = False
        print("UNSOLVABLE:", lv["name"])
    else:
        print(f'{lv["name"]}  grid={cols}x{rows} carrots={nc} best={best}')
print("ALL OK" if ok else "FAILED")
