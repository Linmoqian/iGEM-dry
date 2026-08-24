# -*- coding: utf-8 -*-
"""
replan_demo.py — 动态警报注入下的滚动重规划演示（离散事件仿真器 DES）
事件: t=0 初始5点; t=20 +2点; t=45 +3点; t=70 +2点
策略: ①固定计划(事件0求解,后续点排队续飞) ②事件重规划(全部未完成重解) ③邻接贪心重规划(F9: 原"最近邻"名不副实, 改名披露)
指标: 风险加权响应延迟 Σ w_i·(t_i - t_alert_i); 服务数; 最晚完成
输出: out/replan_results.json + out/figs/fig8_replan_gantt.png
"""
import argparse, json, os, sys, math
import numpy as np
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenario import build_eastlake
from env import build_instance_from_scenario, Instance
from solvers import greedy_solve, ortools_solve
from model import PolicyNetwork
from train import rollouts

REFILL = 12.0
HOVER = 0.13


def make_replan_instance(base, drones, tasks, demand_of=1.0):
    """drones: list of dict(pos_node, cap, en, t); tasks: 原任务节点id列表"""
    m = len(drones)
    ndep = m
    ntask = len(tasks)
    n = ndep + ntask
    xy = np.zeros((n, 2))
    for i, d in enumerate(drones):
        xy[i] = base.xy[d["pos"]]
    for t, nd in enumerate(tasks):
        xy[ndep + t] = base.xy[nd]
    T = np.zeros((m, n, n))
    # 直接用节点索引映射(更稳): 保留索引表
    idx_map = [d["pos"] for d in drones] + list(tasks)
    for k in range(m):
        for i in range(n):
            for j in range(n):
                ni, nj = idx_map[i], idx_map[j]
                T[k, i, j] = base.T[k, ni, nj] if ni != nj else 0.0
    demand = np.zeros(n); risk = np.zeros(n); tw = np.full(n, np.inf)
    for t, nd in enumerate(tasks):
        demand[ndep + t] = demand_of
        risk[ndep + t] = base.risk[nd]
        tw[ndep + t] = base.tw_end[nd]
    cap = np.array([d["cap"] for d in drones], dtype=float)
    en = np.array([d["en"] for d in drones], dtype=float)
    dep = np.zeros(m, dtype=int)
    inst = Instance(name="replan", xy=xy, n_dep=ndep, T=T, demand=demand, risk=risk, tw_end=tw,
                    drone_cap=cap, drone_energy=en, drone_depot=dep)
    return inst, idx_map


def solve(rl, inst, greedy=False, prob_n=16, method="rl"):
    if method == "greedy":
        return greedy_solve(inst)
    if method == "ortools":
        routes, _ = ortools_solve(inst, time_limit=4.0)
        return routes
    with torch.no_grad():
        lp, objs, rts, _ = rollouts(rl, [inst] * prob_n, S=1, greedy=False)
    return rts[int(objs.argmin())]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="out/ckpt.pt")
    ap.add_argument("--seed", type=int, default=9100)
    ap.add_argument("--event-mode", default="original", choices=["original", "highprio"],
                    help="original=原演示流; highprio=M6: 后到点风险最高(穿插高优先级警报)")
    args = ap.parse_args()
    ckpt = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.ckpt)
    rl = None
    if os.path.exists(ckpt):
        from evaluate import load_policy
        rl = load_policy(ckpt)
    sc = build_eastlake(seed=args.seed, n_alerts=10, wind_hour=24)
    base = build_instance_from_scenario(sc)
    tasks_all = [int(j) for j in list(base.task_ids())]
    n0 = 5
    if args.event_mode == "highprio":
        # M6: 高风险点穿插后到 — 按风险排序: 波1=风险最低5点, 波2=次低3点, 波3=最高风险2点(t=45), 波4=余下
        order = sorted(tasks_all, key=lambda j: -float(base.risk[j]))
        low, high = order[5:], order[:5]
        events = [(0.0, sorted(low[:5], key=lambda j: float(base.risk[j]))), (20.0, low[5:8]),
                  (45.0, high), (70.0, low[8:])]
        print("[M6] 高优先级穿插流: t=45 到达风险点:", [(j, round(float(base.risk[j]), 2)) for j in high], flush=True)
    else:
        events = [(0.0, tasks_all[:n0]), (20.0, tasks_all[n0:n0 + 2]),
                  (45.0, tasks_all[n0 + 2:n0 + 5]), (70.0, tasks_all[n0 + 5:])]

    results = {}
    for strategy in ["static", "replan", "greedy_replan"]:
        A = base.xy[base.drone_depot.astype(int)].astype(float)
        m = len(base.drone_cap)
        dron = [dict(pos=int(base.drone_depot[k]), t=0.0, cap=float(base.drone_cap[k]),
                     en=float(base.drone_energy[k])) for k in range(m)]
        served = set()
        arrival = {}
        task_alert = {j: float("inf") for j in tasks_all}
        committed = []          # 已下发但未完成的路线(节点序列,按机)
        n_wave = 0
        for (te, tks) in events:
            for j in tks:
                task_alert[j] = te
            n_wave += 1
            # 推进无人机至 te: 各机按 committed 队列飞行
            for k in range(m):
                queue = committed[k] if k < len(committed) else []
                t = dron[k]["t"]
                cur = dron[k]["pos"]
                while queue and t < te:
                    nxt = queue.pop(0)
                    if nxt is None:
                        break
                    leg = base.T[k, cur, nxt]
                    if t + leg <= te:
                        t += leg
                        cur = nxt
                        if cur >= base.n_dep:
                            served.add(cur)
                            arrival.setdefault(cur, t)
                    else:
                        # 行程中: 停在当前节点, 剩余leg计入下一阶段(近似: 到达te时仍在cur, 计划重排)
                        break
                dron[k]["t"] = max(t, te)
                dron[k]["pos"] = cur
                if cur == 0 or cur in base.drone_depot.tolist():
                    # 在停机坪 -> 可补货
                    dron[k]["cap"] = base.drone_cap[k]
                    dron[k]["en"] = base.drone_energy[k]
            # 待服务 = 所有已到达且未服务
            outstanding = [j for j in tasks_all if task_alert[j] <= te and j not in served]
            if not outstanding:
                committed = [[] for _ in range(m)]
                continue
            if strategy == "static":
                # 固定计划: 分批"先到先服务"(新点仅在后续批次排入, 不透支旧计划)
                if n_wave == 1:
                    sub = outstanding
                else:
                    sub = [j for j in tks if j not in served]
            else:
                sub = outstanding
            if not sub:
                committed = [[] for _ in range(m)]
                continue
            inst_r, idx_map = make_replan_instance(base, dron, sub)
            if strategy == "greedy_replan":  # F9 修正: 原"nearest"实为邻接贪心+全量重规划, 改名如实披露
                routes = greedy_solve(inst_r)
            elif rl is not None:
                routes = solve(rl, inst_r, prob_n=24)
            else:
                routes, _ = ortools_solve(inst_r, time_limit=4.0)
            committed = []
            for k in range(m):
                seq = []
                for jj in routes[k]:
                    seq.append(idx_map[jj])
                committed.append(seq)
        # 剩余执行到完成(贪心推进)
        for k in range(m):
            queue = committed[k] if k < len(committed) else []
            t = dron[k]["t"]
            cur = dron[k]["pos"]
            while queue:
                nxt = queue.pop(0)
                t += base.T[k, cur, nxt] + HOVER
                cur = nxt
                if cur >= base.n_dep and cur not in served:
                    served.add(cur)
                    arrival.setdefault(cur, t)
            dron[k]["t"] = t
        print("   arrivals:", {str(j): round(arrival.get(j, -1), 1) for j in tasks_all}, flush=True)
        print("   alerts:", {str(j): task_alert[j] for j in tasks_all}, flush=True)
        rwt = sum(float(base.risk[j]) * (arrival.get(j, 1000.0) - task_alert[j]) for j in tasks_all)
        results[strategy] = dict(served=len(served), rwt=rwt,
                                 arr={str(j): round(arrival.get(j, -1), 1) for j in tasks_all},
                                 alert={str(j): task_alert[j] for j in tasks_all})
        print(strategy, "| served:", len(served), "| risk-wt delay:", round(rwt, 2),
              "| max completion:", round(max(arrival.values(), default=0), 1))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    with open(os.path.join(out, "replan_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    cols = {"static": "#9e9e9e", "replan": "#2e7d32", "greedy_replan": "#e65100"}
    tasks_plot = [j for j in tasks_all]
    ys = {st: i for i, st in enumerate(["static", "replan", "greedy_replan"])}
    for st, res in results.items():
        for j in tasks_plot:
            t = res["arr"].get(str(j), -1)
            if t >= 0:
                ax.barh(ys[st] + 0.4, t - res["alert"][str(j)], left=res["alert"][str(j)],
                        height=0.4, color=cols[st], alpha=0.8)
    for (te, tks) in events:
        ax.axvline(te, ls="--", color="#7b1fa2", lw=0.9)
        if tks:
            ax.text(te, 2.85, f"t={te:.0f}min +{len(tks)}", ha="center", fontsize=8, color="#7b1fa2")
    ax.set_yticks([0.6, 1.6, 2.6])
    ax.set_yticklabels(["固定计划(按波次)", "事件重规划", "邻接贪心重规划"], fontsize=10)
    ax.set_xlabel("时间 (min)"); ax.set_xlim(-2, 130)
    ax.grid(alpha=0.3, axis="x")
    ax.set_title("图8 动态警报下各策略的投放完成时间（条=任务, 起点=警报时刻）", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "figs", "fig8_replan_gantt.png"), dpi=200, facecolor="white")
    print("saved fig8")


if __name__ == "__main__":
    main()
