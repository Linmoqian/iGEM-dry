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
    hover_time: float = 1.0        # 单点投放作业时间 t_service (min) [V3 默认 1.0; 0.13 为 V2.7 旧值, 敏感性见 07 M1]
    eff_lag: np.ndarray = None     # (n,) 治理生效时滞 = T_drift + t_safe(D_j,C0_j) (min, 0 for depot); 为 None 时目标退化为 t_arrival
    use_eff: bool = False          # 目标是否使用 t_eff = t_arrival + eff_lag (v3.0 治理生效目标)
    infeasible_penalty: float = 0.0  # 能量审计不通过时的固定罚 (V2.7+: 默认 0 保持 V2.6 可比, 实验协议设 1e4)
    drone_w: np.ndarray = None     # (m,) 空重 kg; 非 None 时启用载荷耦合能量 E∝(W+m·kg)^{3/2}
    pack_kg: float = 0.5           # 每包质量 kg (文献 D: 500 mL 菌液瓶)
    kappa: float = 1.0             # 返航余量系数 κ (BER RETURNOK; 1.0=V2.7 语义, 建议 1.15)
    energy_reserve: float = 0.0    # 绝对能量储备 E_res (min 等效)

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
        late_penalty=2.0, makespan_penalty=0.05, unserved_penalty=50.0, refill_time=12.0,
        hover_time=float(getattr(sc, 't_service', 1.0)))
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
    visit_times = [[] for _ in range(n)]   # 每次访问的时刻（升序）
    end_time = np.zeros(m)
    feasible = True
    W = inst.drone_w
    for k in range(m):
        t = 0.0
        energy = inst.drone_energy[k]
        load = inst.drone_cap[k]
        depot = inst.drone_depot[k]
        cur = depot
        for nxt in routes[k]:
            if nxt == depot:
                t += inst.T[k][cur][depot]
                cur = depot
                t += inst.refill_time
                energy = inst.drone_energy[k]
                load = inst.drone_cap[k]
                continue
            # M2: 载荷耦合能量 E_leg = T_leg · ((W + pack_kg·load)/W)^{3/2} (空载=基准)
            fac = 1.0 if W is None else ((W[k] + inst.pack_kg * load) / W[k]) ** 1.5
            leg = inst.T[k][cur][nxt] * fac
            t += inst.T[k][cur][nxt]
            energy = max(0.0, energy - leg)
            load = max(0.0, load - 1.0)
            fac_ret = 1.0 if W is None else ((W[k] + inst.pack_kg * load) / W[k]) ** 1.5
            ret = inst.T[k][nxt][depot] * fac_ret
            if energy < inst.kappa * ret + inst.energy_reserve:
                feasible = False
            visit_count[nxt] += 1
            visit_times[nxt].append(t)
            t += inst.hover_time
            cur = nxt
        leg = inst.T[k][cur][depot]
        end_time[k] = t + leg
    # 完成时刻 = 第 demand 次访问的时刻（严格语义；旧版用 min 会把多访问任务完成时刻取早）
    for j in range(n):
        need = int(inst.demand[j])
        if need > 0 and len(visit_times[j]) >= need:
            t_complete[j] = visit_times[j][need - 1]
    return t_complete, visit_count, end_time, feasible


def eff_time(inst, t_complete):
    """治理生效时刻 t_eff_j = t_arrival_j + eff_lag_j（未服务用 horizon+10）"""
    tasks = inst.task_ids()
    tc = np.where(np.isfinite(t_complete[tasks]), t_complete[tasks], inst.horizon + 10.0)
    if inst.eff_lag is not None and inst.use_eff:
        tc = tc + inst.eff_lag[tasks]
    return tc


def objective(inst, routes):
    """
    总目标 = Σ w_i*t_eff_i + λ*Σ w_i*max(0,t_eff_i-l_i) + μ*makespan + ν*Σ(未服务 w_i)
    t_eff = t_arrival (+ eff_lag 若 use_eff, v3.0 治理生效目标)。
    未服务点按 horizon+10 计入(软惩罚)。
    """
    t_complete, vc, end_time, feasible = objective_times(inst, routes)
    tasks = inst.task_ids()
    w = inst.risk[tasks]
    tc = eff_time(inst, t_complete)
    late = np.maximum(0.0, tc - inst.tw_end[tasks])
    unserved_mask = tc >= inst.horizon + 10.0
    obj = float(np.sum(w * tc) + inst.late_penalty * float(np.sum(w * late))
                + inst.makespan_penalty * float(np.max(end_time)) if len(end_time) else 0.0)
    obj += inst.unserved_penalty * float(np.sum(w * unserved_mask))
    if not feasible and inst.infeasible_penalty > 0.0:
        # 不可行解(能量审计不通过)固定重罚——防止"掩码盲"计划作弊
        obj += inst.infeasible_penalty
    return obj, feasible


def risk_weighted_time(inst, routes):
    """指标: (风险加权完成时间 Σ w_i t_i, makespan max_end, 已服务任务数)
    t 为到达时刻; 若 use_eff 则同时返回治理生效版 Σw·t_eff。"""
    t_complete, vc, end_time, _ = objective_times(inst, routes)
    tasks = inst.task_ids()
    w = inst.risk[tasks]
    tc = np.where(np.isfinite(t_complete[tasks]), t_complete[tasks], inst.horizon + 10.0)
    base = (float(np.sum(w * tc)), float(np.max(end_time)), int(np.sum(np.isfinite(t_complete[tasks]))))
    if inst.use_eff:
        tce = eff_time(inst, t_complete)
        return base + (float(np.sum(w * tce)),)
    return base
