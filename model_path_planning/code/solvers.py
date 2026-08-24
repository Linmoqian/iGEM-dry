# -*- coding: utf-8 -*-
"""
solvers.py — 基线求解器: 风险邻接贪心 + OR-Tools(MDVRPTW 代理目标)
说明: OR-Tools 无法直接表达 Σ w_i*t_i, 采用代理代价 c[i][j] = T[i][j]*(1+γ*w_j)
      + 风险加权软时间窗惩罚; 最终所有方法用 env.objective() 统一评分。
"""
import numpy as np
from env import Instance, objective_times


# ---------------- 贪心 ----------------
def greedy_solve(inst, gamma=1.0, seed=0):
    m = len(inst.drone_cap)
    n = len(inst.xy)
    routes = [[] for _ in range(m)]
    t = np.zeros(m)
    load = inst.drone_cap.copy()
    energy = inst.drone_energy.copy()
    pos = inst.drone_depot.copy()
    done = np.zeros(n, dtype=int)          # 已投放包计数
    tasks = inst.task_ids()
    remaining = {j: inst.demand[j] for j in tasks}
    rng = np.random.RandomState(seed)
    while True:
        best = None
        for k in range(m):
            for j in tasks:
                if remaining[j] <= 0:
                    continue
                if load[k] < 1:
                    continue
                leg = inst.T[k][pos[k]][j]
                if energy[k] - leg < inst.T[k][j][inst.drone_depot[k]]:
                    continue                     # 能量不足返回
                score = leg * (1.0 + gamma * inst.risk[j]) + 0.2 * rng.rand()
                if best is None or score < best[0]:
                    best = (score, k, j)
        if best is None:
            break
        _, k, j = best
        leg = inst.T[k][pos[k]][j]
        t[k] += leg + inst.hover_time
        energy[k] -= leg
        load[k] -= 1
        remaining[j] -= 1
        routes[k].append(int(j))
        pos[k] = int(j)
        # 需要补货 or 无可用任务的无人机 -> 回停机坪
        if load[k] < 1 or all(remaining[l] <= 0 for l in tasks):
            ret = inst.T[k][pos[k]][inst.drone_depot[k]]
            t_ = t[k] + ret
            routes[k].append(int(inst.drone_depot[k]))
            t[k] = t_
            energy[k] = inst.drone_energy[k]
            load[k] = inst.drone_cap[k]
            pos[k] = int(inst.drone_depot[k])
    return routes


# ---------------- OR-Tools ----------------
def ortools_solve(inst, gamma=1.0, time_limit=8.0):
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    n = len(inst.xy)
    m = len(inst.drone_cap)
    T0 = inst.T[0]  # 用速度因子=1 的矩阵(异构差异小, 基线可接受)
    manager = pywrapcp.RoutingIndexManager(n, m, inst.drone_depot.tolist(), inst.drone_depot.tolist())
    routing = pywrapcp.RoutingModel(manager)

    def cost_cb(frm, to):
        i = manager.IndexToNode(frm); j = manager.IndexToNode(to)
        return int(round(T0[i][j] * (1.0 + gamma * inst.risk[j]) * 10.0))
    cost_idx = routing.RegisterTransitCallback(cost_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(cost_idx)

    def demand_cb(frm):
        j = manager.IndexToNode(frm)
        return int(inst.demand[j])
    dm_idx = routing.RegisterUnaryTransitCallback(demand_cb)
    routing.AddDimensionWithVehicleCapacity(dm_idx, 0, [int(c) for c in inst.drone_cap], True, "Cap")

    def time_cb(frm, to):
        i = manager.IndexToNode(frm); j = manager.IndexToNode(to)
        return int(round(T0[i][j] * 10.0))
    tm_idx = routing.RegisterTransitCallback(time_cb)
    horizon_i = int(inst.horizon * 10.0)
    routing.AddDimension(tm_idx, 0, horizon_i, True, "Time")
    time_dim = routing.GetDimensionOrDie("Time")
    # 软时间窗: 超时按 w_i * λ 惩罚
    for j in inst.task_ids():
        idx = manager.NodeToIndex(j)
        time_dim.SetCumulVarSoftUpperBound(idx, int(inst.tw_end[j] * 10.0),
                                           int(inst.late_penalty * inst.risk[j] * 10.0))
    time_dim.SetGlobalSpanCostCoefficient(30)  # 近似最小化 makespan

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = int(time_limit)
    params.log_search = False
    sol = routing.SolveWithParameters(params)
    if sol is None:
        return greedy_solve(inst, gamma)
    routes = [[] for _ in range(m)]
    for k in range(m):
        idx = sol.Value(routing.NextVar(routing.Start(k)))  # 跳过起点停机坪
        while not routing.IsEnd(idx):
            node = manager.IndexToNode(idx)
            routes[k].append(node)
            idx = sol.Value(routing.NextVar(idx))
    return routes
