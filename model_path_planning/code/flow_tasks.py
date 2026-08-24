# -*- coding: utf-8 -*-
"""
flow_tasks.py — v3.0 任务生成器：水流模型 + 降解动力学 → 规划任务（下游接口契约）
=========================================================
消费上游物理模块的输出，产出 path planning 的 Instance：
  - 投放点（cands 子集，score 排序 + 最小间隔去耦）
  - 需求 d_j = ceil(D*(C0_j, T_limit) / 包剂量)   （降解剂量-时间等值线反演）
  - 软窗 l_j = T_limit（治理目标；超标则按 t_safe(D_max) 延展）
  - 治理生效时滞 eff_lag_j = T_drift + t_safe(d_j, C0_j)（目标函数 t_eff 用）
接口对齐 report/06 §5-A 的 task 契约；所有标定参数带来源注释，属"演示标定"。
"""
import os, math, random
import numpy as np
from dataclasses import dataclass
from env import Instance
from scenario import wind_time_matrix, load_wind, DEPOTS, geo_to_m, LAKE_CENTER

SWF_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "model_Two-dimensional_water_flow", "data", "processed")
DEG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "model_MC-LR_degradation_kinetics", "data", "processed")

# ---- 降解动力学演示标定（对齐降解模型 v1.1 参数口径) ----
K_BASE = 0.25          # h^-1 中位表观速率 (Toxins 2018 m6, D7; k~LogN(0.25,0.35))
F_D0 = 0.15            # 每加 1 包剂量的 k 增益系数（剂量增强, 演示值, 对应等值线族形态）
F_D_MAX = 2.0          # 剂量增强上限
T_DRIFT = 60.0         # min, 菌团漂移形成有效覆盖时间 (SWF T_h=1h 实验设置)
T_LIMIT = 360.0        # min, 治理目标时限 6 h
D_MAX = 6              # 包, 单点最大剂量上限 (单机载荷上限)
PACK_DOSE = 1.0        # 包→剂量单位换算 (演示值 1 包=1 剂量单位)
C_REQ = 1.0            # μg/L, WHO 安全阈值
SEP_M = 300.0          # 投放点最小间隔: 2·R_eff, R_eff=sqrt(A_drop/pi)≈143m (A_drop≈0.065 km²)
N_DEP = 3              # 湖岸停机坪数
DHOURS = list(range(0, 2900, 7))    # 风场小时采样集


def f_dose(D):
    """剂量增强因子 f_D(D) = 1 + F_D0·(D-1), 上限 F_D_MAX"""
    return min(F_D_MAX, 1.0 + F_D0 * max(0.0, D - 1.0))


def t_safe_min(C0, D=1, env_k=1.0):
    """治理达标时间 t_safe = ln(C0/C_req)/(k_base·f_D(D)·env_k), min"""
    k = K_BASE * f_dose(D) * env_k
    if k <= 0:
        return float("inf")
    return math.log(max(C0, 1e-9) / C_REQ) / k * 60.0


def dose_needed(C0, T_limit_min=T_LIMIT, env_k=1.0):
    """目标时限反演剂量: 所需 k_eff = ln(C0/C_req)/T_limit (h^-1); f_D = k_eff/(k_base·env_k);
    D = 1 + (f_D−1)/F_D0, 包。"""
    if C0 <= C_REQ:
        return 1.0
    need = math.log(C0 / C_REQ) / (T_limit_min / 60.0)      # 纯所需速率 h^-1
    f = need / (K_BASE * env_k)
    if f <= 1.0:
        return 1.0
    return 1.0 + (min(f, F_D_MAX) - 1.0) / F_D0


@dataclass
class FlowOpt:
    """从 SWF 模型载入的最优投放数据（缓存）"""
    cands: np.ndarray      # (P,2) 米
    scores: np.ndarray     # (P,) 期望保护分数
    member_scores: np.ndarray
    patch: np.ndarray
    dx: float
    a_drop: float          # km^2 单次有效覆盖 (A_drop, 演示值取 0.065)
    a_patch: float         # km^2 斑块面积


_cache = {}


def load_flow_opt(flow_label="SE_2p5"):
    key = flow_label
    if key in _cache:
        return _cache[key]
    opt = np.load(os.path.join(SWF_DIR, "opt_result.npz"))
    dm = np.load(os.path.join(SWF_DIR, "domain.npz"))
    dx = float(dm["dx"])
    from scenario import wind_time_matrix
    A_drop = 0.065        # km^2, SWF 报告: θ=5%, σ0=25m 时 0.038-0.08 取中值
    a_patch = float(opt["patch"].sum()) * dx * dx / 1e6
    fo = FlowOpt(cands=opt["cands"].astype(float), scores=opt["scores"].astype(float),
                 member_scores=opt["member_scores"].astype(float), patch=opt["patch"],
                 dx=dx, a_drop=A_drop, a_patch=a_patch)
    _cache[key] = fo
    return fo


def select_drop_points(fo, n_task=20, sep_m=SEP_M, seed=0):
    """score 降序 + 最小间隔去耦 → 投放点索引列表 (v3.0: 覆盖单元半径驱动的去耦)"""
    rng = np.random.RandomState(seed)
    order = np.argsort(-fo.scores, kind="stable")
    chosen = []
    for i in order:
        if len(chosen) >= n_task:
            break
        p = fo.cands[i]
        ok = True
        for c in chosen:
            if math.hypot(p[0] - fo.cands[c][0], p[1] - fo.cands[c][1]) < sep_m:
                ok = False
                break
        if ok:
            chosen.append(int(i))
    return chosen


def build_flow_instance(seed=0, wind_hour=0, n_task=20, C0_patch=None, env_k=1.0,
                        sep_m=SEP_M, T_limit_min=T_LIMIT, depot_idx=None, random_device=False):
    """
    构建 v3.0 东湖任务实例：
      投放点 = 水流 cands 去耦选择；需求/窗/时滞 = 降解动力学反演；T = 风修正矩阵。
    返回 (env.Instance, meta)
    """
    fo = load_flow_opt()
    rng = random.Random(seed)
    idxs = select_drop_points(fo, n_task=n_task, sep_m=sep_m, seed=seed)
    if C0_patch is None:
        C0_patch = rng.uniform(1.5, 8.0)          # μg/L, 斑块浓度先验 (演示分布)
    w_patch = min(C0_patch / 6.0, 1.0)            # 风险权重映射 (与 scenario 一致)
    # 坐标: cands 米 -> km; 停机坪沿用 scenario.DEPOTS
    lat0, lon0 = LAKE_CENTER
    dep = [geo_to_m(lat0, lon0, la, lo) for _, la, lo in DEPOTS]
    pts = fo.cands[idxs] / 1000.0
    xy = np.array(dep + [tuple(p) for p in pts], dtype=float)
    n_dep = len(dep); n = len(xy); m = 3
    # 需求/窗/时滞 (降解反演)
    demand = np.zeros(n); tw_end = np.full(n, np.inf)
    risk = np.zeros(n); eff_lag = np.zeros(n)
    for t, i in enumerate(idxs):
        c0 = C0_patch * (0.8 + 0.2 * fo.scores[i] / max(fo.scores.max(), 1e-9))   # 点内浓度微变
        rkw = max(0.05, min(1.0, c0 / 6.0))
        D = min(D_MAX, max(1.0, math.ceil(dose_needed(c0, T_limit_min, env_k) / PACK_DOSE)))
        lag = T_DRIFT + t_safe_min(c0, D, env_k)
        j = n_dep + t
        risk[j] = rkw
        demand[j] = D
        tw_end[j] = T_limit_min
        eff_lag[j] = lag
    # 风修正飞行矩阵 (Open-Meteo 逐时风, 同 scenario 口径)
    times, u, v, wspd, wdir = load_wind()
    w_idx = min(wind_hour, len(wspd) - 1)
    wind = (float(u[w_idx]), float(v[w_idx]))
    T = wind_time_matrix(xy, drone_speed=15.0, wind=wind)
    T_all = np.zeros((m, n, n))
    spd = np.array([15.0, 15.0, 13.0])
    for k in range(m):
        T_all[k] = T / (spd[k] / 15.0)
    cap = np.array([4.0, 4.0, 6.0]); en = np.array([28.0, 28.0, 34.0])
    inst = Instance(name=f"flow_seed{seed}_w{wind_hour}", xy=xy, n_dep=n_dep, T=T_all,
                    demand=demand, risk=risk, tw_end=tw_end,
                    drone_cap=cap, drone_energy=en, drone_depot=np.arange(m) % n_dep,
                    horizon=480.0, late_penalty=2.0, makespan_penalty=0.05, unserved_penalty=50.0,
                    eff_lag=eff_lag, use_eff=True)
    meta = dict(n_dep=n_dep, n_task=len(idxs), C0_patch=C0_patch, wind_text=times[w_idx],
                wind=wind, a_patch=fo.a_patch, a_drop=fo.a_drop, idxs=idxs,
                T_limit=T_limit_min, eff_lag=eff_lag)
    return inst, meta


def build_flow_batch(seed, B, wind_hours, n_task=20, rng_seed=None):
    """训练/评估批次: B 个实例, C0/风况随机"""
    rng = np.random.RandomState(rng_seed if rng_seed is not None else seed)
    out = []
    for b in range(B):
        inst, _ = build_flow_instance(seed=seed * 997 + b, wind_hour=int(rng.choice(wind_hours)),
                                      n_task=n_task)
        out.append(inst)
    return out


if __name__ == "__main__":
    inst, meta = build_flow_instance(seed=1, wind_hour=24, n_task=20)
    print("name:", inst.name, " n:", len(inst.xy), " tasks:", meta["n_task"])
    print("C0_patch:", round(meta["C0_patch"], 2), " a_patch:", round(meta["a_patch"], 3),
          " km^2  a_drop:", meta["a_drop"], " km^2")
    print("demand:", inst.demand[inst.task_ids()].astype(int))
    print("risk:", np.round(inst.risk[inst.task_ids()], 2))
    print("tw_end:", inst.tw_end[inst.task_ids()][:5], "...")
    print("eff_lag:", np.round(inst.eff_lag[inst.task_ids()], 0))
    print("wind:", np.round(meta["wind"], 2), "at", meta["wind_text"])
    from env import objective_times
    print("total demand:", int(inst.demand.sum()), " vs fleet cap:", int(inst.drone_cap.sum()),
          " -> refills needed:", int(inst.demand.sum() - inst.drone_cap.sum()))
