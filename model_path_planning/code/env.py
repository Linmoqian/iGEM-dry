# -*- coding: utf-8 -*-
"""
env.py — MD-MUAV-VRPTWP 问题求解/仿真核心
形式化: 多停机坪、多无人机、带时间窗(软)与优先级、容量、能量、风致非对称飞时
    的"最快投放"路径规划问题（应急降解菌投放）。
所有求解器(贪心/OR-Tools/RL)共用同一 Instance + simulate() 评分器，保证可比性。
"""
from dataclasses import dataclass, field
import numpy as np


@dataclass
class Instance:
    name: str
    xy: np.ndarray                 # (n,2) km, 前 n_dep 为停机坪
    n_dep: int
    T: np.ndarray                  # (m,n,n) 每架无人机的飞行时间矩阵 (min, 风修正+机型速度因子)
    demand: np.ndarray             # (n,) 任务所需投放包数 (depot 为 0)
    risk: np.ndarray               # (n,) 风险权重 w_i (depot 为 0)
    tw_end: np.ndarray             # (n,) 软截止时刻 (min) (depot=inf)
    drone_cap: np.ndarray          # (m,) 载荷上限 (包)
    drone_energy: np.ndarray       # (m,) 续航 (min, 能量≈飞行时间, 按安全余量使用)
    drone_depot: np.ndarray        # (m,) 每架无人机所属停机坪索引
    horizon: float = 180.0         # 计划时域 (min)
    late_penalty: float = 2.0      # λ: 迟到惩罚系数 (乘 w_i)
    makespan_penalty: float = 0.05 # μ: 最晚返航惩罚
    unserved_penalty: float = 50.0 # ν: 未服务惩罚 (乘 w_i)
    refill_time: float = 12.0      # 停机坪补货/充电时间 (min)
    hover_time: float = 0.13       # 每次投放悬停时间 (min)

    def task_ids(self):
        return np.arange(self.n_dep, len(self.xy))


def build_instance_from_scenario(sc):
    """scenario.Scenario -> env.Instance"""
    n = len(sc.xy)
    m = sc.n_drone
    T_all = np.zeros((m, n, n))
    for k in range(m):
        s = sc.drone_speed_k[k] / sc.drone_speed
        T_all[k] = sc.T / s
    ndep = int(sc.depot_idx.size)
    demand = np.array(sc.demand, dtype=float)
    risk = np.array(sc.risk, dtype=float)
    tw = np.array(sc.tw_end, dtype=float)
    risk[:ndep] = 0.0
    tw[:ndep] = np.inf
    demand[:ndep] = 0.0
    inst = Instance(
        name=sc.name, xy=sc.xy, n_dep=ndep, T=T_all, demand=demand, risk=risk,
        tw_end=tw, drone_cap=sc.drone_capacity.copy(), drone_energy=sc.drone_energy.copy(),
        drone_depot=np.arange(m) % ndep, horizon=180.0,
        late_penalty=2.0, makespan_penalty=0.05, unserved_penalty=50.0, refill_time=12.0)
    return inst


def objective_times(inst, routes):
    """
    给定解 routes (list[list[int]], 每架无人机访问序列, 元素为停机坪编号表示补货),
    返回 (完成时刻数组 t_complete[n], 访问计数, 无人机结束时刻, 可行性标志)。
    能量约束: 任意时刻剩余能量 >= 返回所属停机坪所需时间 (安全余量)。
    """
    n = len(inst.xy)
    m = len(routes)
    t_complete = np.full(n, np.inf)
    visit_count = np.zeros(n, dtype=int)
    end_time = np.zeros(m)
    feasible = True
    for k in range(m):
        t = 0.0
        energy = inst.drone_energy[k]
        depot = inst.drone_depot[k]
        cur = depot
        for nxt in routes[k]:
            if nxt == depot:
                t += inst.T[k][cur][depot]
                cur = depot
                t += inst.refill_time
                energy = inst.drone_energy[k]
                continue
            leg = inst.T[k][cur][nxt]
            t += leg
            energy = max(0.0, energy - leg)
            ret = inst.T[k][nxt][depot]
            if energy < ret:
                feasible = False
            visit_count[nxt] += 1
            t += inst.hover_time
            if visit_count[nxt] >= inst.demand[nxt]:
                t_complete[nxt] = min(t_complete[nxt], t)
            cur = nxt
        leg = inst.T[k][cur][depot]
        end_time[k] = t + leg
    return t_complete, visit_count, end_time, feasible


def objective(inst, routes):
    """
    总目标 = Σ w_i*t_i + λ*Σ w_i*max(0,t_i-l_i) + μ*makespan + ν*Σ(未服务 w_i)
    未服务点按 horizon+10 计入(软惩罚)。
    """
    t_complete, vc, end_time, feasible = objective_times(inst, routes)
    tasks = inst.task_ids()
    w = inst.risk[tasks]
    tc = np.where(np.isfinite(t_complete[tasks]), t_complete[tasks], inst.horizon + 10.0)
    late = np.maximum(0.0, tc - inst.tw_end[tasks])
    unserved_mask = tc >= inst.horizon + 10.0
    obj = float(np.sum(w * tc) + inst.late_penalty * float(np.sum(w * late))
                + inst.makespan_penalty * float(np.max(end_time)) if len(end_time) else 0.0)
    obj += inst.unserved_penalty * float(np.sum(w * unserved_mask))
    return obj, feasible


def risk_weighted_time(inst, routes):
    """指标: (风险加权完成时间 Σ w_i t_i, makespan max_end, 已服务任务数)"""
    t_complete, vc, end_time, _ = objective_times(inst, routes)
    tasks = inst.task_ids()
    w = inst.risk[tasks]
    tc = np.where(np.isfinite(t_complete[tasks]), t_complete[tasks], inst.horizon + 10.0)
    return float(np.sum(w * tc)), float(np.max(end_time)), int(np.sum(np.isfinite(t_complete[tasks])))
