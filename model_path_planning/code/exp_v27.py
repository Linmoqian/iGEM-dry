# -*- coding: utf-8 -*-
"""
exp_v27.py — V2.7 优化实验统一驱动器
=====================================
对若干 checkpoint 统一执行并汇总:
  1) 东湖 16 场景主对比 (greedy / greedy+LS / OR-Tools / RL / RL+LS), 记录求解状态
  2) 强风压力测试: 合成 10 m/s 斜侧风下 "风感知规划 vs 欧氏规划" 的按真实成本差距 (风敏感度)
  3) v3.0 水流任务 16 场景主对比 (t_eff 治理生效目标), 含 OR-Tools 状态
输出: out/exp_v27.json  + 控制台表格 (实验日志 07 的数据来源)
"""
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenario import build_eastlake, wind_time_matrix
from env import build_instance_from_scenario, objective, risk_weighted_time
from solvers import greedy_solve, ortools_solve
from evaluate import load_policy, solve_rl, local_search, make_inst


def eval_main(policy, mode, n_inst, n_task, seed0, ot_time, samples, augment, ls_iters, save_suffix=None):
    """主对比; 返回 {'methods': {...}, 'per_instance': [...]}"""
    results = {}
    per = []
    for i in range(n_inst):
        inst = make_inst(seed0 + i, n_task, int((i * 37) % 2900), mode)
        rec = {"name": inst.name}
        rg = greedy_solve(inst)
        rwg, ms, sv, *rest = risk_weighted_time(inst, rg)
        obj, _ = objective(inst, rg)
        rec["greedy"] = dict(rwt=rwg, makespan=ms, served=sv, obj=obj, t=0.0,
                             **({"rwt_eff": rest[0]} if rest else {}))
        t0 = time.time()
        r2, st = ortools_solve(inst, time_limit=ot_time)
        rwg, ms, sv, *rest = risk_weighted_time(inst, r2)
        obj, _ = objective(inst, r2)
        rec["ortools"] = dict(rwt=rwg, makespan=ms, served=sv, obj=obj, t=time.time() - t0, status=st,
                              **({"rwt_eff": rest[0]} if rest else {}))
        if policy is not None:
            t0 = time.time()
            r3, o3 = solve_rl(policy, inst, n_try=samples, augment=augment)
            rwg, ms, sv, *rest = risk_weighted_time(inst, r3)
            rec["rl"] = dict(rwt=rwg, makespan=ms, served=sv, obj=o3, t=time.time() - t0,
                             **({"rwt_eff": rest[0]} if rest else {}))
            t0 = time.time()
            r4, o4 = local_search(inst, r3, tsp_iters=ls_iters, seed=i)
            rwg, ms, sv, *rest = risk_weighted_time(inst, r4)
            rec["rl_ls"] = dict(rwt=rwg, makespan=ms, served=sv, obj=o4, t=time.time() - t0,
                                **({"rwt_eff": rest[0]} if rest else {}))
        t0 = time.time()
        r5, o5 = local_search(inst, [list(rr) for rr in rg], tsp_iters=ls_iters, seed=i)
        rwg, ms, sv, *rest = risk_weighted_time(inst, r5)
        rec["greedy_ls"] = dict(rwt=rwg, makespan=ms, served=sv, obj=o5, t=time.time() - t0,
                                **({"rwt_eff": rest[0]} if rest else {}))
        per.append(rec)
    for meth in ["greedy", "greedy_ls", "ortools", "rl", "rl_ls"]:
        vals = [r[meth] for r in per if meth in r]
        if not vals:
            continue
        keys = [k for k in vals[0] if k in ("rwt", "rwt_eff", "makespan", "served", "obj")]
        m = {k: float(np.mean([v[k] for v in vals])) for k in keys}
        m["time"] = float(np.mean([v["t"] for v in vals]))
        m["n"] = len(vals)
        if "status" in vals[0]:
            m["ot_fallback"] = int(np.sum([v["status"] == "fallback" for v in vals]))
        results[meth] = m
    if save_suffix:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", f"exp27_{save_suffix}.json"),
                  "w", encoding="utf-8") as f:
            json.dump(dict(methods=results, per_instance=per), f, ensure_ascii=False, indent=1, default=float)
    return results


def print_table(res, title):
    print(f"\n[{title}]")
    print(f"{'method':12s} {'rwt':>10s} {'rwt_eff':>10s} {'makespan':>9s} {'served':>7s} {'obj':>10s} {'time_s':>8s}")
    for meth, m in res.items():
        extra = f"  (ot_fb={m['ot_fallback']}/{m['n']})" if "ot_fallback" in m else ""
        print(f"{meth:12s} {m.get('rwt', 0):10.2f} {m.get('rwt_eff', 0):10.2f} {m['makespan']:9.2f} "
              f"{m['served']:7.1f} {m['obj']:10.2f} {m['time']:8.3f}{extra}")


def strong_wind(policy, policy_label, n_inst=10, seed0=30000, samples=24):
    """强风压力测试: 用 10 m/s 合成强风矩阵替换真实 T; 风感知规划 vs 欧氏规划均按真实(强风)成本评分"""
    rows = []
    for i in range(n_inst):
        sc = build_eastlake(seed=seed0 + i, n_alerts=12, wind_hour=int((i * 29) % 2900))
        inst_w = build_instance_from_scenario(sc)
        inst_w.T = wind_time_matrix(inst_w.xy, drone_speed=15.0, wind=(6.0, 8.0))[None].repeat(
            len(inst_w.drone_cap), 0) / (np.array([15.0, 15.0, 13.0]) / 15.0)[:, None, None]
        inst_e = build_instance_from_scenario(sc)
        inst_e.T = wind_time_matrix(inst_e.xy, drone_speed=15.0, wind=(0.0, 0.0))[None].repeat(
            len(inst_e.drone_cap), 0) / (np.array([15.0, 15.0, 13.0]) / 15.0)[:, None, None]
        _, o_w = solve_rl(policy, inst_w, n_try=samples)
        _, o_e = solve_rl(policy, inst_e, n_try=samples)
        rows.append(dict(wind_aware=o_w, euclid_plan=o_e))
    wm = float(np.mean([r["wind_aware"] for r in rows]))
    em = float(np.mean([r["euclid_plan"] for r in rows]))
    print(f"\n[强风 10 m/s 压力测试: {policy_label}]  (按真实强风成本评分)")
    print(f"  风感知规划 {wm:.2f} vs 欧氏规划 {em:.2f}  | 差距 {100*(em-wm)/em:.1f}%")
    return dict(n=n_inst, wind_aware=wm, euclid_plan=em, gap_pct=100 * (em - wm) / em)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpts", default="", help="逗号分隔 label=path")
    ap.add_argument("--n-inst", type=int, default=16)
    ap.add_argument("--n-task", type=int, default=10)
    ap.add_argument("--ot-time", type=float, default=5.0)
    ap.add_argument("--samples", type=int, default=32)
    ap.add_argument("--augment", action="store_true")
    ap.add_argument("--ls-iters", type=int, default=800)
    args = ap.parse_args()
    ckpts = []
    for item in filter(None, args.ckpts.split(",")):
        if "=" in item:
            label, path = item.split("=", 1)
        else:
            label, path = os.path.basename(item), item
        ckpts.append((label, path))
    out = {"eastlake": {}, "strong_wind": {}, "flow": {}}
    for label, path in ckpts:
        pol = load_policy(path) if os.path.exists(path) else None
        res = eval_main(pol, "eastlake", args.n_inst, args.n_task, 9000, args.ot_time,
                        args.samples, args.augment, args.ls_iters, save_suffix=f"eastlake_{label}")
        print_table(res, f"东湖16场景 | {label}")
        out["eastlake"][label] = res
        if pol is not None:
            sw = strong_wind(pol, label)
            out["strong_wind"][label] = sw
        # v3.0 水流任务 (use_eff 目标; RL 采样 16 即可, 规模大)
        res_f = eval_main(pol, "flow", args.n_inst, args.n_task, 9000, args.ot_time,
                          max(8, args.samples // 2), False, args.ls_iters, save_suffix=f"flow_{label}")
        print_table(res_f, f"v3.0 水流任务16场景 (t_eff 目标) | {label}")
        out["flow"][label] = res_f
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "exp_v27.json"),
              "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=float)
    print("\nsaved -> out/exp_v27.json")


if __name__ == "__main__":
    main()
