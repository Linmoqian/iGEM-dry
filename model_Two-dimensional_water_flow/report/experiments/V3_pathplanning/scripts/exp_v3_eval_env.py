# -*- coding: utf-8 -*-
"""exp_v3_eval_env.py — M2/M3 环境配置评测驱动
用法: python exp_v3_eval_env.py --env "{'hover':1.0,'drone_w':[4,4,6],'kappa':1.0,'e_res':0.0}" --ckpts "B=outB/ckpt.pt,E=outE/ckpt.pt"
在指定物理环境下对多个 ckpt 评测: 东湖16 / flow8 / 强风压力测试 / OOD(含CA-LS)。
"""
import sys, json, os, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch
from evaluate import load_policy, solve_rl, local_search, make_inst
from solvers import greedy_solve, ortools_solve
from env import build_instance_from_scenario, objective, risk_weighted_time, Instance
from scenario import build_eastlake, wind_time_matrix


def apply_env(inst, env):
    inst.hover_time = float(env.get("hover", 1.0))
    w = env.get("drone_w")
    inst.drone_w = np.array(w, dtype=float) if w else None
    inst.kappa = float(env.get("kappa", 1.0))
    inst.energy_reserve = float(env.get("e_res", 0.0))
    inst.infeasible_penalty = 1e4
    return inst


def eval_table(pol, mode, n_task, seed0, n_inst, env, samples=32, ot=3.0):
    rows = {}
    for i in range(n_inst):
        inst = make_inst(seed0 + i, n_task, int((i * 37) % 2900), mode)
        apply_env(inst, env)
        rec = {}
        g = greedy_solve(inst); o, f = objective(inst, g)
        rec["greedy"] = (o, int(f))
        r_g, o_g = local_search(inst, g, tsp_iters=800, seed=i)
        o_g, f_g = objective(inst, r_g)
        rec["greedy_ls"] = (o_g, int(f_g))
        r2, st = ortools_solve(inst, time_limit=ot)
        o2, f2 = objective(inst, r2)
        rec["ortools"] = (o2, int(f2))
        if pol is not None:
            r3, o3 = solve_rl(pol, inst, n_try=samples, seed=300 + i)
            o3, f3 = objective(inst, r3)
            rec["rl"] = (o3, int(f3))
            r4, o4 = local_search(inst, r3, tsp_iters=800, seed=i)
            o4, f4 = objective(inst, r4)
            rec["rl_ls"] = (o4, int(f4))
        for k, v in rec.items():
            rows.setdefault(k, []).append(v)
    return {k: dict(obj=float(np.mean([v[0] for v in vv])), feas=f"{sum(v[1] for v in vv)}/{n_inst}")
            for k, vv in rows.items()}


def strong_wind(pol, env, n_inst=8, seed0=30000, samples=24):
    rows = []
    for i in range(n_inst):
        sc = build_eastlake(seed=seed0 + i, n_alerts=12, wind_hour=int((i * 29) % 2900))
        inst_w = build_instance_from_scenario(sc)
        apply_env(inst_w, env)
        inst_w.T = wind_time_matrix(inst_w.xy, drone_speed=15.0, wind=(6.0, 8.0))[None].repeat(
            len(inst_w.drone_cap), 0) / (np.array([15.0, 15.0, 13.0]) / 15.0)[:, None, None]
        inst_e = build_instance_from_scenario(sc)
        apply_env(inst_e, env)
        inst_e.T = wind_time_matrix(inst_e.xy, drone_speed=15.0, wind=(0.0, 0.0))[None].repeat(
            len(inst_e.drone_cap), 0) / (np.array([15.0, 15.0, 13.0]) / 15.0)[:, None, None]
        r_w, _ = solve_rl(pol, inst_w, n_try=samples)
        o_w, _ = objective(inst_w, r_w)
        r_e, _ = solve_rl(pol, inst_e, n_try=samples)
        o_we, _ = objective(inst_w, r_e)
        rows.append(dict(wind=o_w, euclid=o_we))
    return dict(wind=float(np.mean([r["wind"] for r in rows])),
                euclid=float(np.mean([r["euclid"] for r in rows])))


def ood_table(pol, env, RAW='../data/raw/Instances-main'):
    from ood_bench import to_instance
    rows = []
    for sub in ['VRPTW', 'MDVRPTW', 'HFVRP']:
        d = os.path.join(RAW, sub)
        for f in sorted(x for x in os.listdir(d) if x.endswith('.vrp'))[:3]:
            inst0 = to_instance(f"{sub}_{f}", os.path.join(d, f))
            idx = np.arange(inst0.n_dep, min(len(inst0.xy), inst0.n_dep + 15))
            keep = np.concatenate([np.arange(inst0.n_dep), idx])
            inst = Instance(name=inst0.name, xy=inst0.xy[keep], n_dep=inst0.n_dep,
                            T=inst0.T[:, keep, :][:, :, keep], demand=inst0.demand[keep],
                            risk=inst0.risk[keep], tw_end=inst0.tw_end[keep],
                            drone_cap=inst0.drone_cap, drone_energy=inst0.drone_energy,
                            drone_depot=np.zeros(len(inst0.drone_cap), dtype=int))
            apply_env(inst, env)
            g = greedy_solve(inst)
            r_g, _ = local_search(inst, g, tsp_iters=800, seed=0)
            o_g, _ = objective(inst, r_g)
            with torch.no_grad():
                import train as T
                lp, objs, rts, _ = T.rollouts(pol, [inst] * 16, S=1, greedy=False)
            r_ls, _ = local_search(inst, rts[int(objs.argmin())], tsp_iters=800, seed=0)
            o_l, _ = objective(inst, r_ls)
            rows.append(dict(name=inst.name[:20], greedy_ls=round(o_g, 1), rl_ls=round(o_l, 1)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", default="{}", help="物理环境 JSON: {hover, drone_w, kappa, e_res}")
    ap.add_argument("--ckpts", default="E=outE/ckpt.pt")
    args = ap.parse_args()
    env = json.loads(args.env)
    out = {"env": env}
    print("=== 物理环境:", env, "===")
    for label, path in [x.split("=", 1) for x in args.ckpts.split(",")]:
        pol = load_policy(path)
        print(f"\n[{label}] 东湖16 (t_service={env.get('hover',1.0)}):")
        t = eval_table(pol, "eastlake", 10, 9000, 16, env)
        for k, v in t.items():
            print(f"  {k:12s} obj={v['obj']:8.2f} 可行={v['feas']}")
        print(f"[{label}] flow8:")
        t = eval_table(pol, "flow", 10, 9100, 8, env, samples=16)
        for k, v in t.items():
            print(f"  {k:12s} obj={v['obj']:8.2f} 可行={v['feas']}")
        sw = strong_wind(pol, env)
        print(f"[{label}] 强风: 风感知规划 {sw['wind']:.2f} vs 欧氏规划 {sw['euclid']:.2f} "
              f"({100*(sw['euclid']-sw['wind'])/max(sw['euclid'],1e-9):.1f}%)")
        od = ood_table(pol, env)
        wins = sum(1 for r in od if r["rl_ls"] < r["greedy_ls"])
        print(f"[{label}] OOD(9): RL+LS vs 贪心+LS = {wins}/9 优 (明细见 json)")
        out[label] = dict(eastlake=t, flow=t, strong_wind=sw, ood=od, ood_win=f"{wins}/9")
    with open("out/exp_v3_env_eval.json", "w") as f:
        json.dump(out, f, indent=1, default=float, ensure_ascii=False)
    print("\nsaved -> out/exp_v3_env_eval.json")


if __name__ == "__main__":
    main()
