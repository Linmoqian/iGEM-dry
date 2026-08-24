# -*- coding: utf-8 -*-
"""
E13: 管线接口定稿演示 — 端到端 (opt_result) -> 需求生成(物理 thr_rel 接口) ->
异构多航次无人机调度 (E5 的 19_interface_mv_vrp.py 升级版)。

E5 (19) 遗留接口待办 (E5 结论④): 需求生成函数用"风险比例线性模型" (1..3 载荷),
真实剂量应由 E4 联标的物理阈值决定。本脚本把该接口定稿:
  需求剂量 dose_i = max(1, round(2*s_i/s_max * (1 + 2*thr_phys/0.25)))
  thr_phys      = swflow.deployment.physical_thr_rel(C0=2.85, t_ok=24, T=25, M=1)
  (物理含义: 单架次剂量 M 倍参考密度时, 达标所需相对阈值 D_req/M;
   dose_i 个载荷单元 => 该点等效 M_eff = dose_i * M)
其余链路全部复用 E5: 坐标换算 / 风修正非对称时间矩阵 /
3 无人机 (cap 4/4/6 kg, en 28/28/34 min, spd 15/15/13 m/s) / 列表调度+NN+2-opt。

===================== 接口契约 (input/output fields) =====================
Stage A 上游: 水流模块 (scripts/04_run_optimization.py, 04b_seed_stability.py)
          -> data/processed/opt_result.npz
  in : cands         (N,2)  float  候选投放点流场坐标 (米, 原点 114.3956E/30.5566N)
       scores        (N,)   float  期望保护率 (演示单位; 本脚本不用, 用 ensemble 均值)
       member_scores (E,N)  float  各风场景成员评分 (E=5)
       patch         (Ny,Nx) bool  华藻斑块掩膜 (未用, 契约字段)
  out: top-K 点 pts (K,2) + 期望保护评分 s_i (K=8) + s_max

Stage B 下游联标: 降解模块 <-> 水流模块 需求生成 (swflow.deployment 真实接口)
  in : C0    (ug/L, 东湖 MC-LR 包络上限 2.85)
       t_ok  (h, 目标处理时限 24)
       T_w   (degC, 水温 25)
       M     (单架次剂量, 参考 m6 密度当量倍数; 此处 1.0)
       s_i, s_max (Stage A)
  out: thr_phys = physical_thr_rel(C0,t_ok,T_w,M)   [本场景 0.2465]
       dose_i   = max(1, round(2*s_i/s_max*(1+2*thr_phys/0.25)))  载荷单元
       (0.25 为 M=1/t_ok=24h 的物理阈值锚点; 锚点归一使剂量在物理阈值下
        自动放大: 顶层点 dose=6 => M_eff=6, 对应 E4 表格 M=5~6 补偿路径)

Stage C 坐标换算: 流场(米) -> 路径规划框架(km)
  in : pts (K,2) 米; LON0=114.3956, LAT0=30.5566;
       LAKE_CENTER=(30.5667,114.3833), equirect 投影
  out: pts_km (K,2) km

Stage D 时间矩阵: 路径规划模块 wind_time_matrix 同式
  in : xy (km); WIND=[-2.5*sin135, -2.5*cos135] m/s (SE 2.5);
       v0=15 m/s; safety=1.25; hover=0.13 min/航段
  out: T (n,n) min 非对称 (顺风/逆风不等)

Stage E 机队+调度: 路径规划模块规格 3 机 + 列表调度
  in : CAP=[4,4,6] kg; EN=[28,28,34] min; SPD=[15,15,13] m/s
       visits = dose_i 次重复的点指标, 风险优先序 (s 降序)
       每机每次架次: 容量/续航约束内按风险序装填; NN 构建 + 2-opt 改进
       (慢机时间 = 快机 T * 15.0/SPD_m, 与 E5 相同)
  out: 每机架次表 (route 顺序, 载荷数, 飞行时间, 累计用时), makespan
       单机基线 (cap 6 kg, 15 m/s, 同 2-opt)
       指标: 加速比 = t1/makespan; 评分加权交付 = sum_i s_i*dose_i;
             评分/分钟 (三机 与 单机)
  契约歧义 (本实验发现): E5 原实现门限为 "累计 elapsed + t_rt > EN[m]" (续航当
  累计软约束, 且 E5 自身输出已越限 31.4>28)。物理需求 48 单元下该语义把所有后续
  架次压成单载荷碎片, 三机反而劣于单机。契约定稿语义: 续航=单架次电池、架次间
  换电, 门限 t_rt <= EN[m] (运行时给两种语义的对照, 后一种为定稿)。
=======================================================================
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from swflow.deployment import physical_thr_rel

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
opt = dict(np.load(os.path.join(PROC, "opt_result.npz")))
cands, member_scores = opt["cands"], opt["member_scores"]
score = member_scores.mean(axis=0)
K = 8
order = np.argsort(-score)[:K]
pts = cands[order]
s = score[order]
s_max = s[0]

print("=== Stage A: 水流模块输出 data/processed/opt_result.npz ===")
print("候选点 %d, 风场景成员 %d; Top-%d 期望保护评分:" % (len(score), member_scores.shape[0], K))
for k in range(K):
    print("  #%d (%7.0f,%7.0f) m  score=%.4f" % (k, pts[k, 0], pts[k, 1], s[k]))

# --- Stage B: 需求生成 (真实接口, 非硬编码) ---
thr_phys = physical_thr_rel(2.85, 24.0, 25.0, 1.0)
factor = 1.0 + 2.0 * thr_phys / 0.25
dose = np.maximum(1, np.round(2.0 * s / s_max * factor).astype(int))
print("\n=== Stage B: 需求生成 (deployment.physical_thr_rel 真实接口) ===")
print("thr_phys = physical_thr_rel(C0=2.85, t_ok=24h, T_water=25C, M=1) = %.4f" % thr_phys)
print("剂量因子 (1 + 2*thr_phys/0.25) = %.3f" % factor)
print("dose_i = max(1, round(2*s_i/s_max * %.3f)): %s" % (factor, dose.tolist()))
print("总载荷单元 = %d  (E5 风险比例需求为 %d)  => 物理阈值剂量放大 x%.1f"
      % (int(dose.sum()), 17, dose.sum() / 17.0))

# --- Stage C: 流场(米) -> 路径规划(km) ---
LON0, LAT0 = 114.3956, 30.5566
MLON = 111320.0 * math.cos(math.radians(LAT0))

def flow_to_pp(x, y):
    lon = LON0 + x / MLON
    lat = LAT0 + y / 111320.0
    return ((lon - 114.3833) * 111.320 * math.cos(math.radians(30.5667)),
            (lat - 30.5667) * 110.574)  # km

points_km = np.array([flow_to_pp(*p) for p in pts])
DEPOTS_PP = [("北岸", 30.5990, 114.3920), ("西南岸", 30.5400, 114.3560), ("东岸", 30.5620, 114.4250)]
fun = lambda la, lo: ((lo - 114.3833) * 111.320 * math.cos(math.radians(30.5667)),
                      (la - 30.5667) * 110.574)
dep_km = np.array([fun(la, lo) for _, la, lo in DEPOTS_PP])
n_d = len(dep_km)
print("\n=== Stage C: 坐标换算 流场(米) -> 路径规划 (km) ===")
for k in range(K):
    print("  #%d  pp=(%6.2f,%6.2f) km  dose=%d  (M_eff=%d x M=1)" %
          (k, points_km[k, 0], points_km[k, 1], dose[k], dose[k]))

# --- Stage D: 风修正非对称时间矩阵 (同 path_planning wind_time_matrix) ---
WIND = np.array([-2.5 * np.sin(np.radians(135.0)), -2.5 * np.cos(np.radians(135.0))])  # SE 2.5 m/s

def time_matrix(xy, v0=15.0, wind=WIND, safety=1.25, hover=0.13):
    n = len(xy)
    T = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dvec = xy[j] - xy[i]
            d = math.hypot(*dvec) * 1000.0  # km -> m
            ux, uy = dvec / d
            vp = wind[0] * ux + wind[1] * uy
            vg = math.sqrt(max(v0 ** 2 - (np.dot(wind, wind) - vp ** 2), 4.0)) + vp
            T[i, j] = safety * d / max(vg, 1.0) / 60.0 + hover
    return T

allxy = np.vstack([dep_km, points_km])
T = time_matrix(allxy)
print("\n=== Stage D: 时间矩阵 T (min, 非对称; SE 2.5 m/s) ===")
print("  T[depot北岸 -> tasks]:", np.round(T[0, n_d:], 2))
print("  T[tasks -> depot北岸]:", np.round(T[n_d:, 0], 2))

# --- Stage E: 机队 + 列表调度 (NN+2-opt 每架次) ---
CAP = [4, 4, 6]
EN = [28.0, 28.0, 34.0]
SPD = [15.0, 15.0, 13.0]

def route_time(dep, visits, T, spd_k):
    n = len(visits)
    if n == 0:
        return 0.0, []
    cl = list(visits)
    cur = dep
    route = []
    while cl:
        j = int(np.argmin([T[cur, n_d + i] for i in cl]))
        i = cl.pop(j)
        route.append(i)
        cur = n_d + i

    def cost(r):
        c = T[dep, n_d + r[0]] + sum(T[n_d + r[k], n_d + r[k + 1]] for k in range(len(r) - 1)) \
            + T[n_d + r[-1], dep]
        return c * (15.0 / spd_k)

    rr = list(route)
    improved = True
    while improved:
        improved = False
        for a in range(len(rr) - 1):
            for b in range(a + 1, len(rr)):
                r2 = rr[:a] + rr[a:b + 1][::-1] + rr[b + 1:]
                if cost(r2) < cost(rr) - 1e-9:
                    rr = r2
                    improved = True
    return cost(rr), rr

visits_all = []
for i in range(K):
    visits_all += [i] * int(dose[i])
# 风险优先序 (覆盖感知; 与 E5 相同)
visits_all = sorted(visits_all, key=lambda i: -s[i])

schedule = [[] for _ in range(3)]
makespan = np.zeros(3)
sortie_log = [[] for _ in range(3)]  # per drone: (route, t_rt, elapsed_after)
rem = list(visits_all)
while rem:
    m = int(np.argmin(makespan))
    trip = []
    cap_left = CAP[m]
    t_now = makespan[m]
    i0 = 0
    while i0 < len(rem):
        i = rem[i0]
        if cap_left <= 0:
            break
        cand = trip + [i]
        t_rt, _ = route_time(0, cand, T, SPD[m])
        if t_now + t_rt > EN[m] and trip:
            break
        trip.append(i)
        cap_left -= 1
        rem.pop(i0)
        i0 = 0
    if not trip:
        trip = [rem.pop(0)]
        t_rt, r0 = route_time(0, trip, T, SPD[m])
        makespan[m] += t_rt
        schedule[m].append(r0)
        sortie_log[m].append((list(r0), t_rt, float(makespan[m])))
        continue
    t_rt, r0 = route_time(0, trip, T, SPD[m])
    schedule[m].append(r0)
    makespan[m] += t_rt
    sortie_log[m].append((list(r0), t_rt, float(makespan[m])))

print("\n=== Stage E: 机队 %d 机 (cap %s kg, en %s min, spd %s m/s) 列表调度+NN+2-opt ===" %
      (3, CAP, EN, SPD))
for m in range(3):
    print("drone %d (cap %d kg, en %.0f min, spd %.0f m/s): 累计 %.1f min"
          % (m, CAP[m], EN[m], SPD[m], makespan[m]))
    for si, (r0, t_rt, el) in enumerate(sortie_log[m]):
        print("  sortie %d: %d 载荷, 点序 %s, t=%.1f min (累计 %.1f min)"
              % (si + 1, len(r0), [("p%d" % i) for i in r0], t_rt, el))
mk3 = float(makespan.max())
print("makespan (3 drones) = %.1f min   (drone%d 瓶颈)" % (mk3, int(np.argmax(makespan))))

# --- 单机基线 (cap 6 kg, 15 m/s, 同 2-opt) ---
def single_drone():
    rem2 = list(visits_all)
    t = 0.0
    n_s = 0
    routes = []
    while rem2:
        trip = []
        cap = 6
        while rem2 and cap > 0:
            trip.append(rem2.pop(0))
            cap -= 1
        t_rt, r0 = route_time(0, trip, T, 15.0)
        t += t_rt
        n_s += 1
        routes.append((list(r0), t_rt))
    return t, n_s, routes

t1, n_s1, routes1 = single_drone()
print("\n单机基线 (cap 6 kg, 15 m/s): makespan %.1f min, %d 架次" % (t1, n_s1))
for si, (r0, t_rt) in enumerate(routes1):
    print("  sortie %d: %d 载荷, 点序 %s, t=%.1f min" %
          (si + 1, len(r0), [("p%d" % i) for i in r0], t_rt))
print("加速比 (单机/三机) = %.2fx  => 三机协同收益 +%.0f%%" %
      (t1 / mk3, (t1 / mk3 - 1.0) * 100.0))

# --- 契约诊断: 续航语义 ---
# E5 原实现: 门限用 "累计 elapsed + t_rt > EN[m]" (续航当作累计软约束, 且 E5 自身输出
# 已越限: drone0 31.4 > 28 min)。新物理需求 48 单元下该门限把所有后续架次压成单载荷
# 碎片 (36 架次, 每架次固定往返 ~13-15.5 min), 协同反而劣化。变体仅把语义钉死为
# "续航 = 单架次电池, 架次间换电": 门限改为 "t_rt > EN[m]"。同一接口、同一贪心。
def schedule_per_sortie():
    mk_v = np.zeros(3)
    log_v = [[] for _ in range(3)]
    rem_v = list(visits_all)
    while rem_v:
        m = int(np.argmin(mk_v))
        trip = []
        cap_left = CAP[m]
        i0 = 0
        while i0 < len(rem_v):
            i = rem_v[i0]
            if cap_left <= 0:
                break
            cand = trip + [i]
            t_rt, _ = route_time(0, cand, T, SPD[m])
            if t_rt > EN[m] and trip:  # 语义钉死: 每架次续航
                break
            trip.append(i)
            cap_left -= 1
            rem_v.pop(i0)
            i0 = 0
        if not trip:
            trip = [rem_v.pop(0)]
        t_rt, r0 = route_time(0, trip, T, SPD[m])
        mk_v[m] += t_rt
        log_v[m].append((list(r0), t_rt, float(mk_v[m])))
    return mk_v, log_v

mk_v, log_v = schedule_per_sortie()
print("\n=== 契约诊断: 续航语义 (同一接口/贪心, 门限 t_rt<=EN 每架次) ===")
for m in range(3):
    print("drone %d: %d 架次, 累计 %.1f min" % (m, len(log_v[m]), mk_v[m]))
mk_v3 = float(mk_v.max())
print("makespan = %.1f min ; 单机 %.1f min ; 加速比 %.2fx => 三机协同收益 +%.0f%%"
      % (mk_v3, t1, t1 / mk_v3, (t1 / mk_v3 - 1.0) * 100.0))

# --- 评分/分钟: 评分加权交付 = sum_i s_i * dose_i (全部载荷交付完成) ---
delivered = float(np.sum(s * dose))
print("\n评分加权交付 (sum s_i*dose_i) = %.4f ; 总载荷 %d 单元" % (delivered, int(dose.sum())))
print("评分/分钟: E5原语义三机 %.5f ; 单机 %.5f ; 变体(每架次续航)三机 %.5f" %
      (delivered / mk3, delivered / t1, delivered / mk_v3))
