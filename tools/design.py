"""关卡设计与验证器 v2
新增地形：~ 水塘（不能走，只能跳过）/ K 钥匙 / D 门（拿到钥匙才开）/ P、Q 传送门（成对）
程序支持重复组：{'r': [子命令...]} 表示把里面的指令执行两遍。
"""

LEVELS = [
    dict(name="第 1 关 · 一直往前走", dir="right", best=4, map=[".....", "S.C.H", "....."]),
    dict(name="第 2 关 · 学会转弯", dir="right", best=6, map=[".....", "....H", "S.C.."]),
    dict(name="第 3 关 · 石头挡路", dir="right", best=9, map=[".....", "S.C#H", "....."]),
    dict(name="第 4 关 · 两颗萝卜", dir="right", best=9, map=["......", ".###..", "..C...", "S.C.H."]),
    dict(name="第 5 关 · 学会跳跳", dir="right", best=2, jump=True, map=[".....", "S#C.H", "....."]),
    dict(name="第 6 关 · 水塘挡路", dir="right", best=3, jump=True,
         map=["######", "S.~C~H", "######"]),
    dict(name="第 7 关 · 跳过石头", dir="right", best=8, jump=True,
         map=["......", "S..#.H", "...#..", "....C."]),
    dict(name="第 8 关 · 水塘迷宫", dir="right", best=8, jump=True,
         map=[".#~...", "S.~...", "..~.C.", ".#~...", "..~..H"]),
    dict(name="第 9 关 · 钥匙与门", dir="right", best=10, jump=True,
         map=["..####", "S..D.H", ".K####", ".C####"]),
    dict(name="第 10 关 · 钥匙在水那边", dir="right", best=4, jump=True,
         map=["#######", "S.~KD.H", "#######"]),
    dict(name="第 11 关 · 传送门", dir="right", best=4, jump=True,
         map=["S..1..", "######", "######", "#2CH.#"]),
    dict(name="第 12 关 · 传送门迷宫", dir="right", best=10, jump=True,
         map=["S.....#", "..1...#", "#######", "#######", "#C...2#", "#..H..#"]),
    dict(name="第 13 关 · 小迷宫", dir="right", best=8, jump=True,
         map=["......", "S.#...", "..#.#.", "C...C.", "....#H"]),
    dict(name="第 14 关 · 绕来绕去", dir="right", best=10, jump=True,
         map=["......", "S.#..H", "..#...", "C.#...", "....C."]),
    dict(name="第 15 关 · 三颗萝卜", dir="up", best=15, jump=True,
         map=["..#..C", ".C#...", "..#.#.", "S...#H", ".C...."]),
    dict(name="第 16 关 · 重复积木", dir="right", best=5, repeat=True, max=6,
         map=[".........", "S..C..C.H", "........."]),
    dict(name="第 17 关 · 重复转弯", dir="right", best=7, repeat=True, max=9,
         map=["S..C..", "......", "......", ".....C", "......", ".....H"]),
    dict(name="第 18 关 · 终极挑战", dir="right", best=17, jump=True,
         map=["S.C.#..", ".##.#..", "....#.C", ".#.....", ".#.##..", "C....#H"]),
]

DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
D0 = {"up": 0, "right": 1, "down": 2, "left": 3}
WALL = {"#", "~"}          # 走不进去
BLOCK_IF_NO_KEY = {"D"}


class Level:
    def __init__(self, spec):
        self.spec = spec
        g = spec["map"]
        self.g = [list(r) for r in g]
        self.rows, self.cols = len(g), len(g[0])
        for r in range(self.rows):
            assert len(g[r]) == self.cols, (spec["name"], r)
        self.carrots = {(r, c) for r in range(self.rows) for c in range(self.cols) if self.g[r][c] == "C"}
        self.start = [(r, c) for r in range(self.rows) for c in range(self.cols) if self.g[r][c] == "S"][0]
        self.home = [(r, c) for r in range(self.rows) for c in range(self.cols) if self.g[r][c] == "H"][0]
        self.portals = {}
        for r in range(self.rows):
            for c in range(self.cols):
                if self.g[r][c] in "12PQ":
                    self.portals[self.g[r][c]] = (r, c)

    def cell(self, r, c):
        return self.g[r][c]

    def can_enter(self, r, c, has_key):
        if r < 0 or c < 0 or r >= self.rows or c >= self.cols:
            return False
        ch = self.g[r][c]
        if ch in WALL:
            return False
        if ch in BLOCK_IF_NO_KEY and not has_key:
            return False
        return True


def step(st, lv, cmd):
    """返回新状态或 None（失败）"""
    r, c, d, key, got = st
    if cmd == "L":
        return (r, c, (d + 3) % 4, key, got)
    if cmd == "R":
        return (r, c, (d + 1) % 4, key, got)
    n = 2 if cmd == "J" else 1
    nr, nc = r + DIRS[d][0] * n, c + DIRS[d][1] * n
    if not lv.can_enter(nr, nc, key):
        return None
    if n == 2 and not key:
        # 关着的门太高，跳不过去
        mr, mc = r + DIRS[d][0], c + DIRS[d][1]
        if 0 <= mr < lv.rows and 0 <= mc < lv.cols and lv.g[mr][mc] == "D":
            return None
    ch = lv.g[nr][nc]
    if ch == "K":
        key = True
    if ch in "12PQ":                     # 传送门：落到另一个门
        other = {"1": "2", "2": "1", "P": "Q", "Q": "P"}[ch]
        nr, nc = lv.portals[other]
        ch2 = lv.g[nr][nc]
        if ch2 == "K":
            key = True
    got = frozenset(got | ({(nr, nc)} & lv.carrots))
    return (nr, nc, d, key, got)


def bfs(lv, cmds):
    from collections import deque
    init = (lv.start[0], lv.start[1], D0[lv.spec["dir"]], False, frozenset())
    dq = deque([(init, [])])
    seen = {init}
    while dq:
        st, path = dq.popleft()
        if (st[0], st[1]) == lv.home and st[4] == frozenset(lv.carrots):
            return path
        for cmd in cmds:
            ns = step(st, lv, cmd)
            if ns is None:
                continue
            if ns in seen:
                continue
            seen.add(ns)
            dq.append((ns, path + [cmd]))
    return None


def simulate(lv, prog):
    """prog: 元素为 'M'/'L'/'R'/'J' 或 ('r', [子程序])"""
    st = (lv.start[0], lv.start[1], D0[lv.spec["dir"]], False, frozenset())

    def run(items, st):
        for it in items:
            if isinstance(it, tuple):
                for _ in range(2):
                    st = run(it[1], st)
                    if st is None:
                        return None
                    if (st[0], st[1]) == lv.home and st[4] == frozenset(lv.carrots):
                        return st
            else:
                st = step(st, lv, it)
                if st is None:
                    return None
                if (st[0], st[1]) == lv.home and st[4] == frozenset(lv.carrots):
                    return st
        return st

    return run(prog, st)


def blocks(prog):
    n = 0
    for it in prog:
        n += 1
        if isinstance(it, tuple):
            n += blocks(it[1])
    return n


def show(prog):
    out = []
    for it in prog:
        out.append("[" + show(it[1]) + "]×2" if isinstance(it, tuple) else it)
    return " ".join(out)


if __name__ == "__main__":
    import json, sys
    tests = {}
    okall = True
    for spec in LEVELS:
        lv = Level(spec)
        if spec.get("repeat"):
            continue
        cmds = "MLR" + ("J" if spec.get("jump") else "")
        p = bfs(lv, cmds)
        if p is None:
            print("!! 无解:", spec["name"]); okall = False; continue
        mark = "OK " if len(p) == spec["best"] else "≠  "
        if len(p) != spec["best"]:
            okall = False
        print(f'{mark}{spec["name"]:<22} best={len(p):<3} 记录={spec["best"]:<3} {"".join(p)}')
        tests[spec["name"]] = p

    # 重复关卡：手写解并验证
    lp = {
        "第 16 关 · 重复积木": [("r", ["M", "M", "M", "M"]), "M"],
        "第 17 关 · 重复转弯": [("r", ["M", "M", "M", "M", "M", "R"])],
    }
    # 第 16 关：8 步走廊 + 2 萝卜，repeat×2 走 8 步正好到 H
    lp["第 16 关 · 重复积木"] = [("r", ["M", "M", "M", "M"])]
    for spec in LEVELS:
        if not spec.get("repeat"):
            continue
        lv = Level(spec)
        pr = lp[spec["name"]]
        res = simulate(lv, pr)
        win = res is not None and (res[0], res[1]) == lv.home and res[4] == frozenset(lv.carrots)
        n = blocks(pr)
        good = win and n <= spec.get("max", 99)
        okall = okall and good
        print(f'{"OK " if good else "!! "}{spec["name"]:<22} 积木={n} 上限={spec.get("max")} 解={show(pr)} win={win}')
        tests[spec["name"]] = pr

    json.dump(tests, open("tools/programs.json", "w"), ensure_ascii=False, indent=1)
    print("ALL OK" if okall else "FAILED")
