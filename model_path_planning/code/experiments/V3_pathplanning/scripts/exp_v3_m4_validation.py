# -*- coding: utf-8 -*-
"""exp_v3_m4_validation.py — M4 约束感知局部搜索验证 (B 策略, t_service=1.0)"""
import sys, json
sys.path.insert(0, '.')
import numpy as np
from evaluate import load_policy, solve_rl, local_search, make_inst
from solvers import greedy_solve
from env import objective

pol = load_policy('outB/ckpt.pt')
res = {}

# 1) 东湖 16: old-LS vs constraint-aware LS (输入: RL 解)
rows = []
for i in range(16):
    inst = make_inst(9000 + i, 10, int((i * 37) % 2900), 'eastlake')
    inst.infeasible_penalty = 1e4
    r3, o3 = solve_rl(pol, inst, n_try=32, seed=100 + i)
    r_old, o_old = local_search(inst, r3, tsp_iters=800, seed=i, constraint_aware=False)
    r_new, o_new = local_search(inst, r3, tsp_iters=800, seed=i, constraint_aware=True)
    of, f = objective(inst, r_new)
    rows.append(dict(old=o_old, new=o_new, feas=int(f)))
res['eastlake'] = dict(old_ls=float(np.mean([r['old'] for r in rows])),
                       new_ls=float(np.mean([r['new'] for r in rows])),
                       feas=f"{sum(r['feas'] for r in rows)}/16")
print("东湖16: old-LS", round(res['eastlake']['old_ls'], 2),
      "| constraint-aware LS", round(res['eastlake']['new_ls'], 2),
      "| 可行", res['eastlake']['feas'])

# 2) flow 8: 同上 (多访问, 高需求)
rows = []
for i in range(8):
    inst, _ = __import__('flow_tasks').build_flow_instance(seed=9100 + i, n_task=10, wind_hour=int((i * 41) % 2900))
    inst.infeasible_penalty = 1e4
    r3, o3 = solve_rl(pol, inst, n_try=16, seed=200 + i)
    r_old, o_old = local_search(inst, r3, tsp_iters=800, seed=i, constraint_aware=False)
    r_new, o_new = local_search(inst, r3, tsp_iters=800, seed=i, constraint_aware=True)
    of, f = objective(inst, r_new)
    rows.append(dict(old=o_old, new=o_new, feas=int(f)))
res['flow'] = dict(old_ls=float(np.mean([r['old'] for r in rows])),
                   new_ls=float(np.mean([r['new'] for r in rows])),
                   feas=f"{sum(r['feas'] for r in rows)}/8")
print("flow8: old-LS", round(res['flow']['old_ls'], 2),
      "| constraint-aware LS", round(res['flow']['new_ls'], 2),
      "| 可行", res['flow']['feas'])

# 3) OOD: RL→new-LS 可行性修复效果 (3 个代表实例)
from ood_bench import to_instance, parse_vrp
import os
RAW = '../data/raw/Instances-main'
ood_rows = []
for sub, fname in [('VRPTW', 'C1_10_1.vrp'), ('VRPTW', 'C1_10_10.vrp'), ('HFVRP', 'X101-FSMFD.vrp')]:
    inst0 = to_instance(f"{sub}_{fname}", os.path.join(RAW, sub, fname))
    idx = np.arange(inst0.n_dep, min(len(inst0.xy), inst0.n_dep + 15))
    keep = np.concatenate([np.arange(inst0.n_dep), idx])
    from env import Instance
    inst = Instance(name=inst0.name, xy=inst0.xy[keep], n_dep=inst0.n_dep, T=inst0.T[:, keep, :][:, :, keep],
                    demand=inst0.demand[keep], risk=inst0.risk[keep], tw_end=inst0.tw_end[keep],
                    drone_cap=inst0.drone_cap, drone_energy=inst0.drone_energy,
                    drone_depot=np.zeros(len(inst0.drone_cap), dtype=int))
    inst.infeasible_penalty = 1e4
    with __import__('torch').no_grad():
        import train
        lp, objs, rts, _ = train.rollouts(pol, [inst] * 16, S=1, greedy=False)
    r_rl = rts[int(objs.argmin())]
    o_rl, f_rl = objective(inst, r_rl)
    r_nls, o_nls = local_search(inst, r_rl, tsp_iters=800, seed=0, constraint_aware=True)
    o_nls, f_nls = objective(inst, r_nls)
    o_g, f_g = objective(inst, greedy_solve(inst))
    ood_rows.append(dict(name=inst.name, rl=round(o_rl, 1), rl_f=int(f_rl),
                         rl_cals_ls=round(o_nls, 1), rl_cals_ls_f=int(f_nls),
                         greedy=round(o_g, 1), greedy_f=int(f_g)))
    print(f"OOD {inst.name[:20]:20s}: RL {o_rl:8.1f} f={int(f_rl)} | RL→CA-LS {o_nls:8.1f} f={int(f_nls)} | 贪心 {o_g:8.1f} f={int(f_g)}")
res['ood'] = ood_rows
json.dump(res, open('out/exp_v3_m4_ls_validation.json', 'w'), indent=1)
print("saved -> out/exp_v3_m4_ls_validation.json")
