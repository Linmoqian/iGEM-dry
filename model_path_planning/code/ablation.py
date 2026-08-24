# -*- coding: utf-8 -*-
"""
ablation.py — 消融与敏感性实验 (v2.7 版)
1) 风修正矩阵  vs  欧氏矩阵 (同一场景集)
2) 软窗惩罚系数 λ 敏感性 [F5 修复: 评估端对 RL 采样轨迹集合按不同 λ 重排, 报告固定 λ 决策的后悔]
3) 推理采样数 S 敏感性 (1 / 8 / 32 / 128)
输出: out/ablation_results.json
"""
import argparse, json, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenario import build_eastlake
from env import build_instance_from_scenario, objective, risk_weighted_time
from evaluate import solve_rl, local_search, load_policy
from model import PolicyNetwork


def euclidean_scenario(sc):
    """把 Scenario 的 T 换成欧氏(无风)矩阵, 其余不变"""
    import copy
    sc2 = copy.deepcopy(sc)
    from scenario import wind_time_matrix
    sc2.T = wind_time_matrix(sc2.xy, drone_speed=15.0, wind=(0.0, 0.0))
    return sc2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="out/ckpt.pt")
    ap.add_argument("--n-inst", type=int, default=10)
    ap.add_argument("--seed0", type=int, default=20000)
    args = ap.parse_args()
    ckpt = args.ckpt if os.path.exists(args.ckpt) or os.path.isabs(args.ckpt) else os.path.join(os.path.dirname(os.path.abspath(__file__)), args.ckpt)
    policy = load_policy(ckpt)
    out = {"wind_vs_euclid": [], "lambda_sens": [], "s_sens": []}
    # 1) wind vs euclid: RL greedy + baseline greedy
    rows = []
    for i in range(args.n_inst):
        sc = build_eastlake(seed=args.seed0 + i, n_alerts=10, wind_hour=int((i * 53) % 2900))
        inst = build_instance_from_scenario(sc)
        instr = build_instance_from_scenario(euclidean_scenario(sc))
        # RL(采样8, 贪心) 在两套矩阵上
        batch = [inst] * 8
        with torch.no_grad():
            from train import rollouts
            lp, objs_o, rts_o, _ = rollouts(policy, batch, S=1, greedy=False)
        o_wind = float(objs_o.min())
        batch2 = [instr] * 8
        with torch.no_grad():
            lp2, objs2, rts2, _ = rollouts(policy, batch2, S=1, greedy=False)
        o_eucl = float(objs2.min())
        # 同场景 风 vs 欧氏 的"真实目标"(在风矩阵上评)
        r1, _ = objective(inst, rts_o[int(objs_o.argmin())])
        r2, _ = objective(inst, rts2[int(objs2.argmin())])
        rows.append(dict(wind_plan_vs_true=r1, euclid_plan_vs_true=r2))
    out["wind_vs_euclid"] = rows
    # 2) lambda sensitivity [F5 修复]: 同一批场景, RL 采样32条轨迹;
    #    (a) 按 λ=2.0 选的路线, 在各 λ 下评分 = 固定决策后悔
    #    (b) 在 32 条中按各 λ 重选最优 = 理想重排
    lambdas = [0.5, 1.0, 2.0, 4.0, 8.0]
    l_rows = []
    for i in range(8):
        sc = build_eastlake(seed=args.seed0 + 300 + i, n_alerts=10, wind_hour=int((i * 67) % 2900))
        inst = build_instance_from_scenario(sc)
        with torch.no_grad():
            from train import rollouts
            lp, objs, rts, _ = rollouts(policy, [inst] * 32, S=1, greedy=False)
        fixed_idx = int(objs.argmin())                     # 训练目标(λ=2.0)下的最优轨迹
        lam_rec = {}
        for lam in lambdas:
            inst2 = inst
            inst2.late_penalty = lam
            # (a) 固定 λ=2 决策在 λ 下的真实代价
            o_fixed, _ = objective(inst2, rts[fixed_idx])
            # (b) 该 λ 下于轨迹集合中重排
            vals = []
            for rt in rts:
                o, _ = objective(inst2, rt)
                vals.append(o)
            lam_rec[str(lam)] = dict(fixed=float(o_fixed), reopt=float(min(vals)),
                                     gap=float(o_fixed - min(vals)))
        l_rows.append(lam_rec)
    out["lambda_sens"] = l_rows
    # 3) S sensitivity
    s_rows = []
    for i in range(8):
        sc = build_eastlake(seed=args.seed0 + 100 + i, n_alerts=10, wind_hour=int((i * 61) % 2900))
        inst = build_instance_from_scenario(sc)
        powers = {1: None, 8: None, 32: None, 128: None}
        for S in powers:
            with torch.no_grad():
                from train import rollouts
                lp, objs, rts, _ = rollouts(policy, [inst] * S, S=1, greedy=False)
            powers[S] = float(objs.min())
        s_rows.append({k: v for k, v in powers.items()})
    out["s_sens"] = s_rows
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "ablation_results.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p)
    print("wind vs euclid mean:", np.mean([r["wind_plan_vs_true"] for r in rows]),
          np.mean([r["euclid_plan_vs_true"] for r in rows]))
    s_mean = {k: np.mean([r[k] for r in s_rows]) for k in s_rows[0]}
    print("S sens:", s_mean)
    print("lambda sens (mean over scenarios):")
    for lam in [str(x) for x in lambdas]:
        print(f"  λ={lam}: fixed={np.mean([r[lam]['fixed'] for r in l_rows]):.2f} "
              f"reopt={np.mean([r[lam]['reopt'] for r in l_rows]):.2f} "
              f"gap={np.mean([r[lam]['gap'] for r in l_rows]):.2f}")


if __name__ == "__main__":
    main()
