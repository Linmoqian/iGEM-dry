
# -*- coding: utf-8 -*-
"""
scenario.py — 东湖应急投放场景构建器
输入: OSM 水多边形 (json), Open-Meteo 风场 (csv), web 检测装置坐标 (14点)
输出: Scenario (depots x/y, alerts x/y/risk/window/demand, wind matrix, cost matrix T)
"""
import json, csv, math, os, random
import numpy as np
from dataclasses import dataclass, field, asdict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")

# 东湖模拟区中心与边界（与 web/src/data/demoReadings.ts 的 demoLake 对齐）
LAKE_CENTER = (30.5667, 114.3833)
BOUNDS = ((30.52, 114.33), (30.62, 114.44))

# 14 个检测装置（坐标取自 web 前端模拟数据; 仅 online/idle 装置产生有效读数）
DEVICES = [
    ("aq-006", 30.5699, 114.3864, 6.35), ("aq-002", 30.5712, 114.3756, 1.36),
    ("aq-003", 30.5598, 114.3703, 0.78), ("aq-001", 30.5667, 114.3833, 0.42),
    ("aq-004", 30.5776, 114.3920, 1.05), ("aq-005", 30.5540, 114.4010, 0.0),
    ("aq-007", 30.5580, 114.3948, 0.55), ("aq-008", 30.5650, 114.3800, 0.60),
    ("aq-009", 30.5615, 114.3650, 0.0),  ("aq-010", 30.5680, 114.3850, 1.10),
    ("aq-011", 30.5535, 114.3820, 0.90), ("aq-012", 30.5740, 114.4000, 4.20),
    ("aq-013", 30.5480, 114.3900, 0.22), ("aq-014", 30.5780, 114.3780, 0.0),
]

# 湖边停机坪（depots，取东湖岸线典型位置：北岸、西南岸、东岸）
DEPOTS = [("北岸停机坪", 30.5990, 114.3920), ("西南岸停机坪", 30.5400, 114.3560),
          ("东岸停机坪", 30.5620, 114.4250)]


def geo_to_m(lat0, lon0, lat, lon):
    """近似等距投影 (公里)"""
    dx = (lon - lon0) * 111.320 * math.cos(math.radians(lat0))
    dy = (lat - lat0) * 110.574
    return dx, dy


def load_osm_water(path=None):
    """解析 OSM water polygons -> list of (name, [(lat,lon),...], kind)"""
    path = path or os.path.join(RAW_DIR, "osm_eastlake_water.json")
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    polys = []
    for e in d.get("elements", []):
        if e.get("type") == "way" and "geometry" in e:
            pts = [(g["lat"], g["lon"]) for g in e["geometry"]]
            name = e.get("tags", {}).get("name", "")
            polys.append((name, pts))
        elif e.get("type") == "relation":
            for m in e.get("members", []):
                if m.get("type") == "way" and "geometry" in m:
                    pts = [(g["lat"], g["lon"]) for g in m["geometry"]]
                    polys.append((e.get("tags", {}).get("name", ""), pts))
    return polys


def load_wind(path=None, date_idx=0):
    """返回 (时间数组, 风矢 (u,v) m/s 简化场, 风速, 风向deg)"""
    path = path or os.path.join(RAW_DIR, "openmeteo_eastlake_2024_bloom.csv")
    times, wspd, wdir = [], [], []
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
        # Open-Meteo CSV 开头有元数据行，跳过直到表头
        start = 0
        for k, ln in enumerate(lines):
            if ln.startswith("time,"):
                start = k
                break
        rd = csv.DictReader(lines[start:])
        for row in rd:
            try:
                k_wspd = [k for k in row if k and k.startswith("wind_speed_10m")][0]
                k_wdir = [k for k in row if k and k.startswith("wind_direction_10m")][0]
                times.append(row["time"])
                wspd.append(float(row[k_wspd]))
                wdir.append(float(row[k_wdir]))
            except Exception:
                continue
    wspd = np.array(wspd) / 3.6
    wdir = np.array(wdir)
    rad = np.deg2rad(wdir)
    u = -wspd * np.sin(rad)   # 气象风向(来风向) -> 风矢量
    v = -wspd * np.cos(rad)
    return times, u, v, wspd, wdir


def wind_time_matrix(xy, drone_speed=15.0, wind=(0.0, 0.0), safety=1.25, hover=0.13):
    """风修正飞行时间矩阵 T[i,j] (min) = dist/地速 + 悬停, 地速 = |v_air + v_wind| 平均近似
    safety: 安全因子(航线系数)"""
    n = xy.shape[0]
    T = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                T[i, j] = 0.0
                continue
            dx, dy = xy[j] - xy[i]
            d = math.hypot(dx, dy)
            if d < 1e-9:
                T[i, j] = hover
                continue
            # 沿航向的地速近似: v_g = sqrt(v_air^2 - v_w_par^2) + v_w_par 的简化形式
            ux, uy = dx / d, dy / d
            v_par = wind[0] * ux + wind[1] * uy          # 顺风分量
            v_c = math.sqrt(max(drone_speed ** 2 - (wind[0] ** 2 + wind[1] ** 2 - v_par ** 2), 4.0)) + v_par
            if v_c < 1.0:
                v_c = 1.0
            T[i, j] = (d * 1000.0 * safety) / max(v_c, 1.0) / 60.0   # 分钟
    return T


@dataclass
class Scenario:
    name: str
    xy: np.ndarray          # (n,2) km 相对坐标, 前 n_depot 个为停机坪
    depot_idx: np.ndarray
    task_idx: np.ndarray
    risk: np.ndarray        # 风险权重 (0-1 归一)
    tw_start: np.ndarray    # 时间窗开始 (分钟, 相对 t0)
    tw_end: np.ndarray
    demand: np.ndarray      # 所需投放包数
    T: np.ndarray           # 飞行时间矩阵 (min), 含风修正, 非对称
    drone_speed: float
    drone_capacity: np.ndarray  # (m,) 每机载荷上限
    drone_energy: np.ndarray    # (m,) 每机续航 (min)
    drone_speed_k: np.ndarray   # (m,) 每机巡航速度 (各向同性比例)
    n_drone: int
    t_service: float = 1.0       # 单点投放作业时间 min [V3 校准默认 1.0: 文献 72-120 s/点]
    meta: dict = field(default_factory=dict)

    def to_dict(self):
        d = asdict(self)
        for k in ("xy", "depot_idx", "task_idx", "risk", "tw_start", "tw_end", "demand", "T",
                  "drone_capacity", "drone_energy", "drone_speed_k"):
            d[k] = np.asarray(d[k]).tolist()
        return d


def build_eastlake(seed=0, n_alerts=None, wind_hour=0, random_device=False, t_service=1.0):
    """构建东湖场景: 用 OSM 水多边形约束生成随机警报点; wind_hour 指定风场小时索引"""
    rng = random.Random(seed)
    polys = load_osm_water()
    name, pts = max(polys, key=lambda p: len(p[1]))    # 取最大水体 = 东湖主水面
    if random_device:
        alerts = DEVICES
    else:
        # 在 demoLake 监测包围盒内均匀采样（与 web 前端的 14 个装置区域一致）
        n = n_alerts or 10
        alerts = []
        for _ in range(n):
            lat = rng.uniform(30.545, 30.585)
            lon = rng.uniform(114.360, 114.405)
            u = rng.random()
            conc = rng.uniform(2.0, 6.0) if u < 0.30 else (rng.uniform(1.0, 2.0) if u < 0.70 else rng.uniform(0.0, 1.0))
            alerts.append((f"alert{_}", lat, lon, conc))
    # 坐标归一化
    lat0, lon0 = LAKE_CENTER
    dep = [geo_to_m(lat0, lon0, la, lo) for _, la, lo in DEPOTS]
    tas = [geo_to_m(lat0, lon0, a[1], a[2]) for a in alerts]
    xy = np.array(dep + tas, dtype=float)             # km（geo_to_m 已按 km/deg 换算）
    n_dep = len(dep); n_task = len(tas); n = n_dep + n_task
    # 风险权重: 浓度 c -> priority = min(c,6)/6 软窗 [0, 20+40*(1-p)] 分钟
    risk = np.zeros(n); tws = np.zeros(n); twe = np.zeros(n)
    for t, (aid, la, lo, conc) in enumerate(alerts):
        p = min(conc / 6.0, 1.0)
        risk[n_dep + t] = max(p, 0.05)
        tws[n_dep + t] = 0.0
        twe[n_dep + t] = 25.0 + 45.0 * (1.0 - p)       # 高优先级 -> 更紧窗口
    demand = np.ones(n); demand[:n_dep] = 0
    # 风场 (从 Open-Meteo 采样)
    times, u, v, wspd, wdir = load_wind()
    idx = min(wind_hour, len(wspd) - 1)
    wind = (float(u[idx]), float(v[idx]))
    T = wind_time_matrix(xy, drone_speed=15.0, wind=wind)
    m = 3
    cap = np.array([4, 4, 6])
    en = np.array([28.0, 28.0, 34.0])
    spd = np.array([15.0, 15.0, 13.0])
    sc = Scenario(
        name=f"eastlake_seed{seed}_w{wind_hour}",
        xy=xy, depot_idx=np.arange(n_dep), task_idx=np.arange(n_dep, n),
        risk=risk, tw_start=tws, tw_end=twe, demand=demand, T=T,
        drone_speed=15.0, drone_capacity=cap, drone_energy=en, drone_speed_k=spd,
        n_drone=m, t_service=t_service, meta={"n_dep": n_dep, "alerts": alerts, "wind": wind,
                         "wind_text": times[idx], "n_task": n_task})
    return sc


if __name__ == "__main__":
    sc = build_eastlake(seed=1, wind_hour=24)
    print("name:", sc.name)
    print("n:", len(sc.xy), " depots:", len(sc.depot_idx), " tasks:", len(sc.task_idx))
    print("risk:", np.round(sc.risk[sc.task_idx], 2))
    print("tw_end:", np.round(sc.tw_end[sc.task_idx], 1))
    print("T[0,:6] (min):", np.round(sc.T[0, :6], 2))
    print("wind:", sc.meta["wind"], "at", sc.meta["wind_text"])
