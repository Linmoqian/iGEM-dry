# -*- coding: utf-8 -*-
"""
ood_bench.py — 分布外(OOD)泛化压力测试: 公共基准实例 (PyVRP VRPTW/MDVRPTW/HFVRP)
把基准 .vrp 转为本项目 Instance 结构, 用 贪心/OR-Tools/RL 求解, 报告可行性与目标。
"""
import argparse, json, os, sys, math
import numpy as np
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import Instance, objective
from solvers import greedy_solve, ortools_solve
from model import PolicyNetwork
from train import rollouts

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw", "Instances-main")


def parse_vrp(path):
    secs = {}
    cur = None
    coords, demand, tw, depot = [], [], [], []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            if ":" in ln and ln[0].isalpha():
                k, v = ln.split(":", 1)
                secs[k.strip()] = v.strip()
                cur = k.strip()
                continue
            if ln.upper() in ("NODE_COORD_SECTION", "DEMAND_SECTION", "TIME_WINDOW_SECTION",
                              "DEPOT_SECTION", "VEHICLES_SECTION", "DISPLAY_DATA_SECTION",
                              "EDGE_WEIGHT_SECTION", "SERVICE_TIME_SECTION", "SERVICE_TIME"):
                cur = ln.upper()
                continue
            if ln.upper() == "EOF":
                break
            parts = ln.split()
            try:
                nums = [float(x) for x in parts]
            except ValueError:
                continue
            if cur == "NODE_COORD_SECTION" and len(nums) >= 3:
                coords.append((nums[0], nums[1], nums[2]))
            elif cur == "DEMAND_SECTION" and len(nums) >= 2:
                demand.append((nums[0], nums[1]))
            elif cur == "TIME_WINDOW_SECTION" and len(nums) >= 3:
                tw.append((nums[0], nums[1], nums[2]))
            elif cur == "DEPOT_SECTION" and len(nums) >= 1:
                depot.append(int(nums[0]))
    return secs, coords, demand, tw, depot


def to_instance(name, path, cap_limit=6):
    secs, coords, dem, tw, depots = parse_vrp(path)
    n0 = int(secs.get("DIMENSION", len(coords)))
    if not coords or n0 < 3:
        return None
    coords = sorted(coords)[:n0]
    xy = np.array([[c[1], c[2]] for c in coords])
    scale = 20.0 / max(np.ptp(xy[:, 0]), np.ptp(xy[:, 1]), 1.0)
    xy = (xy - xy.mean(0)) * scale
    demand = np.zeros(n0)
    for (i, d) in dem[:n0]:
        demand[int(i) - 1] = min(3.0, max(0.0, d))   # 截断需求至训练分布(≤3包)
    n_dep = 1
    tw_end = np.full(n0, 180.0)
    for (i, a, b) in tw[:n0]:
        tw_end[int(i) - 1] = min(180.0, b * 0.05)
    risk = np.zeros(n0)
    for i in range(1, n0):
        risk[i] = max(0.05, min(1.0, 0.3 + 0.5 * abs(np.sin(i * 1.7))))
    cap = float(secs.get("CAPACITY", 100))
    m = 3
    speed = 15.0
    T = np.zeros((m, n0, n0))
    for k in range(m):
        for i in range(n0):
            for j in range(n0):
                d = math.hypot(xy[i, 0] - xy[j, 0], xy[i, 1] - xy[j, 1])
                T[k, i, j] = d * 1000.0 / (speed * 60.0)
    inst = Instance(name=name, xy=xy, n_dep=n_dep, T=T, demand=demand, risk=risk, tw_end=tw_end,
                    drone_cap=np.array([min(cap, cap_limit)] * m),
                    drone_energy=np.array([34.0] * m), drone_depot=np.zeros(m, dtype=int),
                    horizon=180.0, late_penalty=2.0, makespan_penalty=0.05, unserved_penalty=50.0)
    return inst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="out/ckpt.pt")
    args = ap.parse_args()
    ckpt = args.ckpt if os.path.exists(args.ckpt) or os.path.isabs(args.ckpt) else os.path.join(os.path.dirname(os.path.abspath(__file__)), args.ckpt)
    rl = None
    if os.path.exists(ckpt):
        from evaluate import load_policy
        rl = load_policy(ckpt)
    cands = []
    for sub in ["VRPTW", "MDVRPTW", "HFVRP"]:
        d = os.path.join(RAW, sub)
        if os.path.isdir(d):
            files = sorted([f for f in os.listdir(d) if f.endswith(".vrp")])
            cands.extend((sub, os.path.join(d, f)) for f in files[:3])
    print("OOD instances:", [(s, os.path.basename(p)) for s, p in cands])
    out_rows = []
    for (sub, p) in cands:
        try:
            inst = to_instance(f"{sub}_{os.path.basename(p)}", p)
        except Exception as e:
            print("parse fail", p, e)
            continue
        if inst is None or len(inst.xy) < 5:
            continue
        idx = np.arange(inst.n_dep, min(len(inst.xy), inst.n_dep + 15))
        keep = np.concatenate([np.arange(inst.n_dep), idx])
        T15 = inst.T[:, keep, :][:, :, keep]
        sub_i = Instance(name=inst.name, xy=inst.xy[keep], n_dep=inst.n_dep, T=T15,
                         demand=inst.demand[keep], risk=inst.risk[keep], tw_end=inst.tw_end[keep],
                         drone_cap=inst.drone_cap, drone_energy=inst.drone_energy,
                         drone_depot=np.zeros(len(inst.drone_cap), dtype=int))
        rg = greedy_solve(sub_i)
        o1, f1 = objective(sub_i, rg)
        r2, ot_status = ortools_solve(sub_i, time_limit=3.0)
        o2, f2 = objective(sub_i, r2)
        if rl is not None:
            with torch.no_grad():
                lp, objs, rts, _ = rollouts(rl, [sub_i] * 16, S=1, greedy=False)
            r3 = rts[int(objs.argmin())]
            o3, f3 = objective(sub_i, r3)
        else:
            r3, o3, f3 = rg, o1, f1
        n_task = len(idx)
        print(f"{sub_i.name:16s} n={n_task:3d} | greedy {o1:8.1f} f={int(f1)} | ortools {o2:8.1f} f={int(f2)} {ot_status} | rl {o3:8.1f} f={int(f3)}")
        out_rows.append(dict(name=sub_i.name, n=n_task, greedy=round(o1, 2), ortools=round(o2, 2), rl=round(o3, 2),
                             f_greedy=bool(f1), f_ortools=bool(f2), f_rl=bool(f3),
                             ot_status=ot_status))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "ood_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(out_rows, f, ensure_ascii=False, indent=1)
    print("saved", out)


if __name__ == "__main__":
    main()
