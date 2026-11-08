"""快速试关卡：python3 tools/probe.py cand.json
cand.json = [{"name":..,"dir":..,"jump":true,"map":[...]}, ...]
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from design import Level, bfs, is_win, simulate, blocks, show, cmds_of

for spec in json.load(open(sys.argv[1], encoding="utf-8")):
    lv = Level(spec)
    p = bfs(lv, cmds_of(spec))
    if p is None:
        print(f'!! 无解  {spec["name"]}')
    else:
        print(f'{len(p):2d} 步  {spec["name"]:<14} {"".join(p)}')
