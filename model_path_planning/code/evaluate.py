# -*- coding: utf-8 -*-
"""
evaluate.py — 统一评测: greedy / OR-Tools / RL / RL+局部搜索 在 N 个东湖测试场景上的对比
输出: out/eval_results.json (各方法指标), 打印对比表
"""
import argparse, json, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenario import build_eastlake
from env import build_instance_from_scenario, objective, risk_weighted_time
from solvers import greedy_solve, ortools_solve
from model import PolicyNetwork
from train import rollouts, make_batch


def local_search(inst, routes, tsp_iters=600, seed=0):
    """简单 2-opt/relocate 局部搜索: 改进即接受, 始终维护当前最好解(修复版)。
    修复说明: 旧版在拒绝扰动时将解重置回'最初输入'而非'当前最好解', 导致爬山退化(详见 05_质量审查报告 F1)。"""
    import copy
    rng = np.random.RandomState(seed)
    cur = copy.deepcopy(routes)
    best, _ = objective(inst, cur)
    best_rts = copy.deepcopy(cur)
    for it in range(tsp_iters):
        mode = rng.rand()
        trial = copy.deepcopy(cur)
        if mode < 0.5 and len(trial) > 1:
            k1 = rng.randint(len(trial))
            k2 = rng.randint(len(trial))
            if len(trial[k1]) < 1 or not trial[k2]:
                continue
            p = rng.randint(len(trial[k1]))
            q = rng.randint(len(trial[k2]) + 1)
            node = trial[k1][p]
            trial[k1].pop(p)
            trial[k2].insert(q, node)
        else:
            k = rng.randint(len(trial))
            if len(trial[k]) >= 3:
                i = rng.randint(len(trial[k]) - 1)
                j = rng.randint(i + 1, len(trial[k]))
                trial[k][i:j + 1] = trial[k][i:j + 1][::-1]
        o, _ = objective(inst, trial)
        if o < best - 1e-9:
            best = o
            best_rts = copy.deepcopy(trial)
            cur = copy.deepcopy(trial)
        else:
            cur = copy.deepcopy(cur)   # 保持当前最好(拒绝即回到 cur)
            if rng.rand() < 0.02:      # 少量随机重启扰动, 增强逃离局部最优
                cur = copy.deepcopy(best_rts)
    return best_rts, best


def solve_rl(policy, inst, n_try=32, n_task=10):
    """RL: 批量采样 n_try 条轨迹取最优(允许自增强)"""
    batch = [inst] * n_try
    with torch.no_grad():
        logps, objs, rts_list, _ = rollouts(policy, batch, S=1, greedy=False)
    objs = objs.cpu().numpy()
    bi = int(np.argmin(objs))
    return rts_list[bi], float(objs[bi])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=None)
    ap.add_argument("--n-inst", type=int, default=16)
    ap.add_argument("--n-task", type=int, default=10)
    ap.add_argument("--ot-time", type=float, default=5.0)
    ap.add_argument("--seed0", type=int, default=9000)
    ap.add_argument("--ls-iters", type=int, default=800)
    args = ap.parse_args()

    policy = None
    if args.ckpt and os.path.exists(args.ckpt):
        for (d, L) in [(128, 3), (96, 3), (64, 2)]:
            try:
                policy = PolicyNetwork(d=d, L=L)
                policy.load_state_dict(torch.load(args.ckpt, map_location="cpu"))
                policy.eval()
                print("loaded ckpt d=", d, "L=", L)
                break
            except Exception:
                policy = None
                continue
    results = {"methods": {}, "per_instance": []}
    rows = []
    for i in range(args.n_inst):
        sc = build_eastlake(seed=args.seed0 + i, n_alerts=args.n_task, wind_hour=int((i * 37) % 2900))
        inst = build_instance_from_scenario(sc)
        rec = {"name": inst.name}
        # greedy
        t0 = time.time()
        r = greedy_solve(inst)
        rt = time.time() - t0
        rwg, ms, sv = risk_weighted_time(inst, r)
        obj, _ = objective(inst, r)
        rec["greedy"] = dict(rwt=rwg, makespan=ms, served=sv, obj=obj, t=rt)
        # ortools
        t0 = time.time()
        r2 = ortools_solve(inst, time_limit=args.ot_time)
        rt = time.time() - t0
        rwg, ms, sv = risk_weighted_time(inst, r2)
        obj, _ = objective(inst, r2)
        rec["ortools"] = dict(rwt=rwg, makespan=ms, served=sv, obj=obj, t=rt)
        if policy is not None:
            t0 = time.time()
            r3, o3 = solve_rl(policy, inst)
            rt = time.time() - t0
            rwg, ms, sv = risk_weighted_time(inst, r3)
            rec["rl_sampled"] = dict(rwt=rwg, makespan=ms, served=sv, obj=o3, t=rt)
            t0 = time.time()
            r4, o4 = local_search(inst, r3, tsp_iters=args.ls_iters, seed=i)
            rt = time.time() - t0
            rwg, ms, sv = risk_weighted_time(inst, r4)
            rec["rl_ls"] = dict(rwt=rwg, makespan=ms, served=sv, obj=o4, t=rt)
        # greedy + LS
        t0 = time.time()
        r5, o5 = local_search(inst, r, tsp_iters=args.ls_iters, seed=i)
        rt = time.time() - t0
        rwg, ms, sv = risk_weighted_time(inst, r5)
        rec["greedy_ls"] = dict(rwt=rwg, makespan=ms, served=sv, obj=o5, t=rt)
        results["per_instance"].append(rec)
        rows.append((inst.name, rec))
    # 汇总
    for meth in ["greedy", "greedy_ls", "ortools", "rl_sampled", "rl_ls"]:
        vals = [(k, rec[meth]) for (k, rec) in rows if meth in rec]
        if not vals:
            continue
        means = {mk: float(np.mean([v[mk] for _, v in vals])) for mk in ["rwt", "makespan", "served", "obj"]}
        means["time"] = float(np.mean([v["t"] for _, v in vals]))
        means["n"] = len(vals)
        results["methods"][meth] = means
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "eval_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1, default=float)
    print(f"{'method':12s} {'rwt(风险加权时间)':>16s} {'makespan':>10s} {'served':>8s} {'obj':>10s} {'solve_s':>9s}")
    for meth, m in results["methods"].items():
        print(f"{meth:12s} {m['rwt']:16.2f} {m['makespan']:10.2f} {m['served']:8.2f} {m['obj']:10.2f} {m['time']:9.2f}")
    print("saved ->", os.path.join(out_dir, "eval_results.json"))


if __name__ == "__main__":
    main()
