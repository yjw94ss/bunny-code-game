"""关卡体检

1. 最优解是否真的用到了新机制（最优路径踩过哪些格子）
2. 障碍类机制是否"必须"：把对应的能力拿走，关卡应该无解
      水塘   -> 不许跳跃
      门     -> 不许拿钥匙
      桥     -> 不许按按钮
      传送门 -> 拆掉传送门
3. 加速类机制（冰面、弹簧）是否让最优解变短
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from design import Level, bfs, cmds_of, LEVELS, blocks, simulate, is_win, step, DIRS

HAND = {
    "重复积木": [("r", ["M", "M", "M", "M"])],
    "重复转弯": [("r", ["M", "M", "M", "M", "M", "R"])],
}
NAME = {"*": "冰面", "^": "弹簧", "~": "水塘", "B": "按钮", "=": "桥",
        "K": "钥匙", "D": "门", "1": "传送门", "2": "传送门"}


def strip(spec, chars, repl="."):
    return dict(spec, map=["".join(repl if ch in chars else ch for ch in row) for row in spec["map"]])


def solve_len(spec, cmds=None):
    lv = Level(spec)
    if spec.get("repeat"):
        r = simulate(lv, HAND[spec["name"]])
        return blocks(HAND[spec["name"]]) if is_win(lv, r) else None
    p = bfs(lv, cmds or cmds_of(spec))
    return None if p is None or len(p) == 0 else len(p)


def touched(spec, path):
    """沿最优路径走一遍，收集踩过（含滑过/飞过）的格子类型"""
    lv = Level(spec)
    st = (lv.start[0], lv.start[1], {"up": 0, "right": 1, "down": 2, "left": 3}[spec["dir"]], False, False, frozenset())
    seen = set()
    for cmd in path:
        ns = step(st, lv, cmd)
        if ns is None:
            break
        r0, c0 = st[0], st[1]
        r1, c1 = ns[0], ns[1]
        # 直线段上的所有格子（滑行的中间格、跳过的中间格都算）
        if r0 == r1:
            for c in range(min(c0, c1), max(c0, c1) + 1):
                seen.add(lv.g[r0][c])
        elif c0 == c1:
            for r in range(min(r0, r1), max(r0, r1) + 1):
                seen.add(lv.g[r][c0])
        st = ns
    return seen


def has(spec, ch):
    return any(ch in row for row in spec["map"])


def main():
    problems = []
    for i, spec in enumerate(LEVELS, 1):
        lv = Level(spec)
        if spec.get("repeat"):
            path = None
            base = solve_len(spec)
        else:
            path = bfs(lv, cmds_of(spec))
            base = len(path) if path else None
        notes = []
        if path:
            seen = touched(spec, path)
            used = sorted({NAME[c] for c in seen if c in NAME})
            notes.append("踩到:" + ("/".join(used) if used else "无特殊格"))
            for ch, label in [("*", "冰面"), ("^", "弹簧")]:
                if has(spec, ch) and ch not in seen:
                    notes.append(f"⚠{label}没用上")
                    problems.append((spec["name"], f"{label}没被用到"))

        # 障碍类：拿掉能力应该无解
        if has(spec, "~") and not spec.get("repeat") and not has(spec, "^"):
            alt = solve_len(spec, "MLR")
            if alt is not None:
                notes.append(f"⚠水塘能绕过({alt})")
                problems.append((spec["name"], "不用跳也能过水塘"))
        if has(spec, "D") and not spec.get("repeat"):
            alt = solve_len(strip(spec, "K"))   # 只有钥匙没了，门依然锁着
            if alt is not None:
                notes.append(f"⚠门能绕过({alt})")
                problems.append((spec["name"], "不用钥匙也能过门"))
        if has(spec, "=") and not spec.get("repeat"):
            alt = solve_len(strip(spec, "B"))
            if alt is not None:
                notes.append(f"⚠桥能绕过({alt})")
                problems.append((spec["name"], "不用按按钮也能过桥"))
        if has(spec, "1") and not spec.get("repeat"):
            alt = solve_len(strip(spec, "12"))
            if alt is not None:
                notes.append(f"⚠传送门能绕过({alt})")
                problems.append((spec["name"], "不用传送门也能过"))

        # 加速类：拆掉后应该更长（或者至少最优解里真的用到了）
        for ch, label in [("*", "冰面"), ("^", "弹簧")]:
            if has(spec, ch) and not spec.get("repeat"):
                alt = solve_len(strip(spec, ch))
                touched_it = path and ch in touched(spec, path)
                if alt is not None and alt <= base and not touched_it:
                    notes.append(f"⚠{label}没起作用({alt})")
                    problems.append((spec["name"], f"{label}不影响最优解"))
                elif alt is not None and alt <= base:
                    notes.append(f"{label}省不了积木但用到了")

        print(f'{i:2d}. {spec["name"]:<12} 最优={base}\t' + "  ".join(notes))

    print()
    if problems:
        print("可以再打磨：")
        for n, d in problems:
            print(" -", n, ":", d)
    else:
        print("全部机制都真的在起作用 ✓")


if __name__ == "__main__":
    main()
