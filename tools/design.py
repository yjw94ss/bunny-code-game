"""关卡设计与验证器 v3

地形：
  .  草地        #  石头        C  萝卜       S  起点      H  家
  ~  水塘（不能走，只能跳过）     *  冰面（走上去会一直滑到尽头）
  ^  弹簧板（踩上自动往前弹两格，不花积木）
  B  按钮（踩上去，所有桥出现）   =  桥（按钮按下前是墙）
  K  钥匙        D  门（拿到钥匙才开）      1 2  传送门（成对）

指令：M 前进 / L 左转 / R 右转 / J 跳两格 / ('r', [...]) 重复两遍
"""

LEVELS = [
    dict(name="一直往前走", dir="right", map=[".....", "S.C.H", "....."]),
    dict(name="学会转弯", dir="right", map=[".....", "....H", "S.C.."]),
    dict(name="石头挡路", dir="right", map=[".....", "S.C#H", "....."]),
    dict(name="两颗萝卜", dir="right", map=["......", ".###..", "..C...", "S.C.H."]),
    dict(name="学会跳跳", dir="right", jump=True, map=[".....", "S#C.H", "....."]),
    dict(name="水塘挡路", dir="right", jump=True,
         map=["######", "S.~C~H", "######"]),
    # ---- 冰面：走上去会一直滑 ----
    dict(name="冰面滑行", dir="right", jump=True,
         map=["##########", "S.C*****.H", "##########"]),
    dict(name="冰面拐弯", dir="right", jump=True,
         map=["########", "S*****C#", "######.#", "######C#", "######H#"]),
    dict(name="跳过石头", dir="right", jump=True,
         map=["......", "S..#.H", "...#..", "....C."]),
    dict(name="水塘迷宫", dir="right", jump=True,
         map=[".#~...", "S.~...", "..~.C.", ".#~...", "..~..H"]),
    # ---- 弹簧板：踩上自动弹两格 ----
    dict(name="弹簧板", dir="right", jump=True,
         map=["#######", "S.^..C#", "#####H#"]),
    dict(name="弹簧接力", dir="right", jump=True,
         map=["##########", "S.^~^..C.H", "##########"]),
    # ---- 钥匙与门 ----
    dict(name="钥匙与门", dir="right", jump=True,
         map=["..####", "S..D.H", ".K####", ".C####"]),
    dict(name="钥匙在水那边", dir="right", jump=True,
         map=["#######", "S.~KD.H", "#######"]),
    # ---- 传送门 ----
    dict(name="传送门", dir="right", jump=True,
         map=["S..1..", "######", "######", "#2CH.#"]),
    dict(name="传送门迷宫", dir="right", jump=True,
         map=["S.....#", "..1...#", "#######", "#######", "#C...2#", "#..H..#"]),
    dict(name="小迷宫", dir="right", jump=True,
         map=["......", "S.#...", "..#.#.", "C...C.", "....#H"]),
    # ---- 按钮与桥 ----
    dict(name="按下按钮", dir="right", jump=True,
         map=["#########", "SB..=.C.H", "#########"]),
    dict(name="去按按钮", dir="right", jump=True,
         map=["#########", "S.~..=..H", "###.#####", "###B#####"]),
    dict(name="绕来绕去", dir="right", jump=True,
         map=["......", "S.#..H", "..#...", "C.#...", "....C."]),
    dict(name="冰面弹簧", dir="right", jump=True,
         map=["##########", "S*.*^~..C#", "########H#"]),
    dict(name="三颗萝卜", dir="up", jump=True,
         map=["..#..C", ".C#...", "..#.#.", "S...#H", ".C...."]),
    # ---- 重复 ----
    dict(name="重复积木", dir="right", repeat=True,
         map=[".........", "S..C..C.H", "........."]),
    dict(name="重复转弯", dir="right", repeat=True,
         map=["S..C..", "......", "......", ".....C", "......", ".....H"]),
    # ---- 综合 ----
    dict(name="终极挑战", dir="right", jump=True,
         map=["S.C.#..", ".##.#..", "....#.C", ".#.....", ".#.##..", "C....#H"]),
    dict(name="大师关", dir="right", jump=True,
         map=["##########", "#S*.*.C..#", "#.#.#.#..#", "#.^~.^~..#",
              "#.#.#.#..#", "#C..~.C..#", "#.#.#.#..#", "#..^~..H.#", "##########"]),
]

DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
D0 = {"up": 0, "right": 1, "down": 2, "left": 3}
WALL = {"#", "~"}          # 走不进去，也会挡住滑行


class Level:
    def __init__(self, spec):
        self.spec = spec
        g = spec["map"]
        self.g = [list(r) for r in g]
        self.rows, self.cols = len(g), len(g[0])
        for r in range(self.rows):
            assert len(g[r]) == self.cols, (spec["name"], r, len(g[r]))
        cells = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        self.carrots = {(r, c) for r, c in cells if self.g[r][c] == "C"}
        self.start = [(r, c) for r, c in cells if self.g[r][c] == "S"][0]
        self.home = [(r, c) for r, c in cells if self.g[r][c] == "H"][0]
        self.portals = {}
        for r, c in cells:
            if self.g[r][c] in "12PQ":
                self.portals[self.g[r][c]] = (r, c)

    def ch(self, r, c):
        if r < 0 or c < 0 or r >= self.rows or c >= self.cols:
            return "#"
        return self.g[r][c]

    def can_enter(self, r, c, key, bridge):
        ch = self.ch(r, c)
        if ch in WALL:
            return False
        if ch == "D" and not key:
            return False
        if ch == "=" and not bridge:
            return False
        return True

    def door_blocks_jump(self, r, c, key, bridge):
        """跳/弹的中途格：关着的门、关着的桥都太高，跳不过去"""
        ch = self.ch(r, c)
        if ch == "D" and not key:
            return True
        if ch == "=" and not bridge:
            return True
        return False


def settle(st, lv):
    """落点结算：按钮 / 钥匙 / 传送门 / 弹簧 / 冰面滑行，直到停下来"""
    r, c, d, key, bridge, got = st
    for _ in range(20):
        ch = lv.g[r][c]
        if ch == "K":
            key = True
        if ch == "B":
            bridge = True
        if ch in "12PQ":
            other = {"1": "2", "2": "1", "P": "Q", "Q": "P"}[ch]
            r, c = lv.portals[other]
            got = frozenset(got | ({(r, c)} & lv.carrots))
            break                                  # 传送门是落点终点
        if ch == "^":
            dr, dc = DIRS[d]
            nr, nc = r + dr * 2, c + dc * 2
            if not lv.can_enter(nr, nc, key, bridge):
                return None                        # 弹到墙上/水里
            if lv.door_blocks_jump(r + dr, c + dc, key, bridge):
                return None
            r, c = nr, nc
            got = frozenset(got | ({(r, c)} & lv.carrots))
            continue
        if ch == "*":
            moved = False
            while True:
                nr, nc = r + DIRS[d][0], c + DIRS[d][1]
                if not lv.can_enter(nr, nc, key, bridge):
                    break
                r, c = nr, nc
                moved = True
                if (r, c) in lv.carrots:
                    got = frozenset(got | {(r, c)})
                if lv.g[r][c] == "K":
                    key = True
                if lv.g[r][c] == "B":
                    bridge = True
                if lv.g[r][c] != "*":
                    break
            if not moved:
                break
            continue
        break
    else:
        return None
    return (r, c, d, key, bridge, got)


def step(st, lv, cmd):
    """返回新状态或 None（撞墙/失败）"""
    r, c, d, key, bridge, got = st
    if cmd == "L":
        return (r, c, (d + 3) % 4, key, bridge, got)
    if cmd == "R":
        return (r, c, (d + 1) % 4, key, bridge, got)
    n = 2 if cmd == "J" else 1
    nr, nc = r + DIRS[d][0] * n, c + DIRS[d][1] * n
    if not lv.can_enter(nr, nc, key, bridge):
        return None
    if n == 2 and lv.door_blocks_jump(r + DIRS[d][0], c + DIRS[d][1], key, bridge):
        return None
    got = frozenset(got | ({(nr, nc)} & lv.carrots))
    return settle((nr, nc, d, key, bridge, got), lv)


def is_win(lv, st):
    return st is not None and (st[0], st[1]) == lv.home and st[5] == frozenset(lv.carrots)


def bfs(lv, cmds):
    from collections import deque
    init = (lv.start[0], lv.start[1], D0[lv.spec["dir"]], False, False, frozenset())
    dq = deque([(init, [])])
    seen = {init}
    while dq:
        st, path = dq.popleft()
        if is_win(lv, st):
            return path
        for cmd in cmds:
            ns = step(st, lv, cmd)
            if ns is None or ns in seen:
                continue
            seen.add(ns)
            dq.append((ns, path + [cmd]))
    return None


def simulate(lv, prog):
    st = (lv.start[0], lv.start[1], D0[lv.spec["dir"]], False, False, frozenset())

    def run(items, st):
        for it in items:
            reps = 2 if isinstance(it, tuple) else 1
            seq = it[1] if isinstance(it, tuple) else [it]
            for _ in range(reps):
                for x in seq:
                    st = step(st, lv, x)
                    if st is None:
                        return None
                    if is_win(lv, st):
                        return st
        return st

    return run(prog, st)


def blocks(prog):
    return sum(1 + (blocks(it[1]) if isinstance(it, tuple) else 0) for it in prog)


def show(prog):
    out = []
    for it in prog:
        out.append("[" + show(it[1]) + "]×2" if isinstance(it, tuple) else it)
    return " ".join(out)


def cmds_of(spec):
    return "MLR" + ("J" if spec.get("jump") else "")


if __name__ == "__main__":
    import json
    tests = {}
    okall = True
    for i, spec in enumerate(LEVELS, 1):
        lv = Level(spec)
        if spec.get("repeat"):
            continue
        p = bfs(lv, cmds_of(spec))
        if p is None:
            print("!! 无解:", spec["name"]); okall = False; continue
        best = spec.get("best", len(p))
        mark = "OK " if len(p) == best else "≠  "
        if len(p) != best:
            okall = False
        print(f'{mark}{i:2d}. {spec["name"]:<12} best={len(p):<3} 记录={best:<3} {"".join(p)}')
        tests[spec["name"]] = {"name": spec["name"], "prog": p, "best": len(p)}

    # 重复关卡：手写解
    lp = {
        "重复积木": [("r", ["M", "M", "M", "M"])],
        "重复转弯": [("r", ["M", "M", "M", "M", "M", "R"])],
    }
    for i, spec in enumerate(LEVELS, 1):
        if not spec.get("repeat"):
            continue
        lv = Level(spec)
        pr = lp[spec["name"]]
        res = simulate(lv, pr)
        win = is_win(lv, res)
        n = blocks(pr)
        cap = spec.get("max", max(len(pr) + 6, 8))
        good = win and n <= cap
        okall = okall and good
        print(f'{"OK " if good else "!! "}{i:2d}. {spec["name"]:<12} 积木={n} 上限={cap} 解={show(pr)} win={win}')
        tests[spec["name"]] = {"name": spec["name"], "prog": pr, "best": n}

    ordered = [tests[sp["name"]] for sp in LEVELS if sp["name"] in tests]
    json.dump(ordered, open("tools/programs.json", "w"), ensure_ascii=False, indent=1)
    print("ALL OK" if okall else "FAILED")
