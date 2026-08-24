# -*- coding: utf-8 -*-
"""exp_v3_m5_scale.py — M5 规模外推验证: n∈{50,100} 下 贪心+LS vs RL+LS (B 零样本 / D 分布内)"""
import sys, json, time
sys.path.insert(0, '.')
import numpy as np
from evaluate import load_policy, solve_rl, local_search, make_inst
from solvers import greedy_solve
from env import objective, risk_weighted_time

pols = {'B(10训练零样本)': load_policy('outB/ckpt.pt'),
        'D(50训练)': load_policy('outD/ckpt.pt')}
out = {}
for n_task in [50, 100]:
    n_inst = 16 if n_task == 50 else 8
    rows = []
    for i in range(n_inst):
        inst = make_inst(9000 + i, n_task, int((i * 37) % 2900), 'eastlake')
        inst.infeasible_penalty = 1e4
        rec = {'name': inst.name}
        g = greedy_solve(inst)
        o_g, _ = objective(inst, g)
        rec['greedy'] = o_g
        t0 = time.time()
        r_gl, o_gl = local_search(inst, g, tsp_iters=800, seed=i)
        rec['greedy_ls'] = (o_gl, time.time() - t0)
        for label, pol in pols.items():
            t0 = time.time()
            r, o = solve_rl(pol, inst, n_try=32, seed=400 + i)
            rec[f'rl_{label}'] = o
            r_ls, o_ls = local_search(inst, r, tsp_iters=800, seed=i)
            rec[f'rl_ls_{label}'] = (o_ls, time.time() - t0)
        rows.append(rec)
        if i % 4 == 0:
            print(f"  n={n_task} inst{i}/{n_inst} done", flush=True)
    agg = {}
    for k in rows[0]:
        if k == 'name':
            continue
        if isinstance(rows[0][k], tuple):
            agg[k] = dict(obj=float(np.mean([r[k][0] for r in rows])),
                          t=float(np.mean([r[k][1] for r in rows])))
        else:
            agg[k] = float(np.mean([r[k] for r in rows]))
    out[str(n_task)] = agg
    print(f"\n===== n={n_task} ({n_inst} 场景均值) =====")
    for k, v in agg.items():
        if isinstance(v, dict):
            print(f"  {k:16s} obj={v['obj']:10.2f}  time={v['t']:6.3f}s")
        else:
            print(f"  {k:16s} obj={v:10.2f}")
    rl_col = [k for k in agg if k.startswith('rl_ls')]
    if len(rl_col) >= 2:
        g_base = agg['greedy_ls']['obj']
        best = min(rl_col, key=lambda k: agg[k]['obj'])
        gains = ', '.join(f"{k}: {100*(g_base-agg[k]['obj'])/g_base:.1f}%" for k in rl_col)
        print(f"  → RL+LS 最优变体: {best} | 各 RL+LS vs 贪心+LS 提升: {gains}")
json.dump({k: {kk: (vv if not isinstance(vv, dict) else vv) for kk, vv in v.items()} for k, v in out.items()},
          open('out/exp_v3_m5_scale.json', 'w'), indent=1, default=float, ensure_ascii=False)
print("saved -> out/exp_v3_m5_scale.json")
