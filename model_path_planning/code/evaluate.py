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


def load_policy(ckpt_path):
    """按 ckpt_config.json 加载; 无配置时回退旧式结构猜测 (兼容 V2.6 ckpt)"""
    cfg_path = os.path.join(os.path.dirname(ckpt_path), "ckpt_config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, encoding="utf-8") as f:
            cfg = json.load(f)
        pol = PolicyNetwork(d=cfg.get("d", 128), L=cfg.get("L", 3),
                            n_feat=cfg.get("n_feat", 6), use_edge=cfg.get("use_edge", False),
                            tanh_prior=cfg.get("tanh_prior", False))
        pol.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
        pol.eval()
        print("loaded cfg:", cfg.get("mode", "?"), "d=", cfg.get("d"), "use_edge=", cfg.get("use_edge"),
              "tanh_prior=", cfg.get("tanh_prior"))
        return pol
    for (d, L) in [(128, 3), (96, 3), (64, 2)]:
        try:
            pol = PolicyNetwork(d=d, L=L)
            pol.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
            pol.eval()
            print("loaded legacy ckpt d=", d, "L=", L)
            return pol
        except Exception:
            continue
    return None


def augment8(inst):
    """×8 实例增广 (POMO/RRNCO 惯例, 纯推理层):
      变体1 风逆转: T'[k,i,j]=T[k,j,i] (精确对称: 顺/逆风互换, 几何不变);
      变体2/3 xy 镜像 (x→−x / y→−y, T 不变); 变体4-7 = 组合。
    变换后节点索引不变, 解可直接映射回原实例。"""
    import copy
    outs = []
    for v in range(8):
        it = copy.copy(inst)
        if v % 2 == 1:                                   # 风逆转
            it.T = inst.T.transpose(0, 2, 1).copy()
        xy = inst.xy.copy()
        if (v // 2) % 2 == 1:
            xy = xy.copy(); xy[:, 0] = -xy[:, 0]
        if (v // 4) % 2 == 1:
            xy = xy.copy(); xy[:, 1] = -xy[:, 1]
        it.xy = xy
        outs.append(it)
    return outs


def solve_rl(policy, inst, n_try=32, n_task=10, augment=False):
    """RL: 批量采样 n_try 条轨迹取最优; augment=True 时对 8 个变换各采样 n_try//8 条, 统一评分选最优"""
    aug_vs = augment8(inst) if augment else [inst]
    per = max(1, n_try // len(aug_vs))
    best = None
    for it in aug_vs:
        batch = [it] * per
        with torch.no_grad():
            logps, objs, rts_list, _ = rollouts(policy, batch, S=1, greedy=False)
        objs = objs.cpu().numpy()
        bi = int(np.argmin(objs))
        o, _ = objective(inst, rts_list[bi])            # 一律回原实例评分 (变换后 T 不同, 必须重评)
        if best is None or o < best[1]:
            best = (rts_list[bi], o)
    return best[0], best[1]


def make_inst(seed, n_task, wind_hour, mode):
    if mode == "flow":
        from flow_tasks import build_flow_instance
        inst, _ = build_flow_instance(seed=seed, wind_hour=wind_hour, n_task=n_task)
        return inst
    sc = build_eastlake(seed=seed, n_alerts=n_task, wind_hour=wind_hour)
    return build_instance_from_scenario(sc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=None)
    ap.add_argument("--n-inst", type=int, default=16)
    ap.add_argument("--n-task", type=int, default=10)
    ap.add_argument("--ot-time", type=float, default=5.0)
    ap.add_argument("--seed0", type=int, default=9000)
    ap.add_argument("--ls-iters", type=int, default=800)
    ap.add_argument("--samples", type=int, default=32)
    ap.add_argument("--augment", action="store_true", help="推理 ×8 增广 (风逆转+镜像)")
    ap.add_argument("--mode", default="eastlake", choices=["eastlake", "flow"])
    args = ap.parse_args()

    policy = load_policy(args.ckpt) if args.ckpt and os.path.exists(args.ckpt) else None
    results = {"methods": {}, "per_instance": [], "config": vars(args)}
    rows = []
    for i in range(args.n_inst):
        inst = make_inst(args.seed0 + i, args.n_task, int((i * 37) % 2900), args.mode)
        rec = {"name": inst.name}
        # greedy
        t0 = time.time()
        r = greedy_solve(inst)
        rt = time.time() - t0
        rwg, ms, sv, *rest = risk_weighted_time(inst, r)
        obj, _ = objective(inst, r)
        rec["greedy"] = dict(rwt=rwg, makespan=ms, served=sv, obj=obj, t=rt)
        if rest:
            rec["greedy"]["rwt_eff"] = rest[0]
        # ortools
        t0 = time.time()
        r2, ot_status = ortools_solve(inst, time_limit=args.ot_time)
        rt = time.time() - t0
        rwg, ms, sv, *rest = risk_weighted_time(inst, r2)
        obj, _ = objective(inst, r2)
        rec["ortools"] = dict(rwt=rwg, makespan=ms, served=sv, obj=obj, t=rt, status=ot_status)
        if rest:
            rec["ortools"]["rwt_eff"] = rest[0]
        if policy is not None:
            t0 = time.time()
            r3, o3 = solve_rl(policy, inst, n_try=args.samples, augment=args.augment)
            rt = time.time() - t0
            rwg, ms, sv, *rest = risk_weighted_time(inst, r3)
            rec["rl_sampled"] = dict(rwt=rwg, makespan=ms, served=sv, obj=o3, t=rt)
            if rest:
                rec["rl_sampled"]["rwt_eff"] = rest[0]
            t0 = time.time()
            r4, o4 = local_search(inst, r3, tsp_iters=args.ls_iters, seed=i)
            rt = time.time() - t0
            rwg, ms, sv, *rest = risk_weighted_time(inst, r4)
            rec["rl_ls"] = dict(rwt=rwg, makespan=ms, served=sv, obj=o4, t=rt)
            if rest:
                rec["rl_ls"]["rwt_eff"] = rest[0]
        # greedy + LS
        t0 = time.time()
        r5, o5 = local_search(inst, r, tsp_iters=args.ls_iters, seed=i)
        rt = time.time() - t0
        rwg, ms, sv, *rest = risk_weighted_time(inst, r5)
        rec["greedy_ls"] = dict(rwt=rwg, makespan=ms, served=sv, obj=o5, t=rt)
        if rest:
            rec["greedy_ls"]["rwt_eff"] = rest[0]
        results["per_instance"].append(rec)
        rows.append((inst.name, rec))
    # 汇总
    for meth in ["greedy", "greedy_ls", "ortools", "rl_sampled", "rl_ls"]:
        vals = [(k, rec[meth]) for (k, rec) in rows if meth in rec]
        if not vals:
            continue
        keys = [k for k in vals[0][1] if k in ("rwt", "rwt_eff", "makespan", "served", "obj")]
        means = {mk: float(np.mean([v[mk] for _, v in vals])) for mk in keys}
        means["time"] = float(np.mean([v["t"] for _, v in vals]))
        means["n"] = len(vals)
        if "status" in vals[0][1]:
            means["ot_fallback"] = int(np.sum([v["status"] == "fallback" for _, v in vals]))
        results["methods"][meth] = means
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out_dir, exist_ok=True)
    out_name = "eval_results.json" if args.mode == "eastlake" else f"eval_{args.mode}.json"
    with open(os.path.join(out_dir, out_name), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1, default=float)
    print(f"{'method':12s} {'rwt(风险加权)':>14s} {'makespan':>10s} {'served':>8s} {'obj':>10s} {'solve_s':>9s}")
    for meth, m in results["methods"].items():
        extra = f"  (ot_fallback={m['ot_fallback']}/{m['n']})" if "ot_fallback" in m else ""
        print(f"{meth:12s} {m['rwt']:14.2f} {m['makespan']:10.2f} {m['served']:8.2f} {m['obj']:10.2f} {m['time']:9.2f}{extra}")
    print("saved ->", os.path.join(out_dir, out_name))


if __name__ == "__main__":
    main()
