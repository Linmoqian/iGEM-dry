# E12：场景库分位成员验证 — SE p75 / N p75 两成员的 24h 自旋与投放对照（生产默认：powB3 水深 + cd_mode='lake'）

运行脚本：临时 `e12_scenario_members.py`（主运行，含自旋+保存+4 次投放）、`e12_anchors.py` / `e12_anchorC.py`（分解锚点）；完整运行日志：`report/experiments/_E12_run.log`。产物：`data/processed/flow_SE_p75.npz`、`data/processed/flow_N_p75.npz`（各 0.5 MB）。

## 动机

E6 用本模块自家 Open-Meteo 数据（2023–2024 共 17,544 h）重建风统计后提议"8 扇区 ×（p50/p75/p90）"场景库，其中 **SE p75 = 3.33 m/s（131°）、N p75 = 5.17 m/s（4°）** 均为高频扇区（SE 17.2%、N 25.1%）的代表性中强风成员；而现有三场景 SE_2.5/N_3.0/W_2.0 只落在各自扇区 48/42/62 分位（≈中位风）。

本轮模块优化刚"落地六项"（commit 089ee1a）：生产水深 → B3 幂指数（`domain.npz`，`domain_exp.npz` 为旧基线）、`SweConfigSI` 默认 `cd_mode='lake'`（cd_lake(U) = Zhang, Chen & Brett 2024 WRR Fig.4b 拟合，clip 到实测带 [1.2e-3, 3.6e-3]）、particles 默认 windage 2%、`make_tracer` 自动读取流场风信息。**问题**：① 新成员从未在生产配置下运行过；② cd_lake 拟合段仅 1.6–3.0 m/s（r²=0.901），而**两个 p75 成员（3.33 / 5.17 m/s）都在拟合段之外/边缘**：cd_lake 在 U≈3.40 m/s 处就贴上 3.6e-3 上限（此后恒定），SE p75=3.517e-3（贴顶未截）、N p75 无 clip 时公式给 5.85e-3 → 被截为 3.6e-3，高风端行为必须实测；③ 旧场景文件（flow_SE_2p5 / flow_N_3p0）是旧基线产物（exp 水深 + 常数 Cd 1.3e-3 + 36h 自旋，E7 归因 n=0.022），且**无 Cd/n 元数据**，两代对照的差异来源必须分解清楚。

## 方法

- **域**：`data/processed/domain.npz`（bathy_mode=powB3，湿格 12,487，dx=50 m，水深 mean 2.483 / max 3.705；旧基线 `domain_exp.npz` mean 2.210 / max 4.639）。
- **求解器**：`SweConfigSI(dx=50, dt=20.0, n_manning=0.0238, nu=0.5, use_adv=True, use_coriolis=True, nu_mode='smag', cs=0.29)`（cd_mode 走类默认 `'lake'`）；风应力 `wind_stress(spd, dir, cd_mode='lake')`；自旋 **24 h = 4320 步**，每 2 h 记录一次 |u|max/mean（trace）。
- **成员**：SE_p75 = (3.33 m/s, 131°)、N_p75 = (5.17 m/s, 4°)；保存字段含 `u/v/eta/uc/vc/mask/depth/xs/ys/dx/trace/wind_mps/wind_dir/cd_used/cd_mode/n_manning/label`。
- **投放对照**：`sim_drop((−1300, −200), T_h=2, dt=5, n=2500, thr_rel=0.05, rng_seed=7)`；`make_tracer` 默认 **w_a=0.02 windage**（新旧流场均带 wind 字段 → 同一投放协议，风漂移 2% 双方一致施加）；旧对照直接读 `data/processed/flow_SE_2p5.npz`、`flow_N_3p0.npz`。
- **分解锚点**（同日补跑，逐一隔离 4 个因素；均为 2.5 m/s / 135° 的 24h 自旋）：
  - **A** = powB3 + lakeCd（风 2.5→3.33 纯风效应基准）
  - **B** = exp + lakeCd（exp 域上的纯 Cd 效应；注：锚点脚本中 B 的打印标签误写 "constCd"，其 Cd 输出 0.002463 = cd_lake(2.5) 证实实际为 lake，本报告按真实配置记录）
  - **C** = exp + constCd 1.3e-3（旧配置的 24h 版本，隔离自旋时长/糙率残差）
  - 既有中间产物 `flow_SE_2p5_bathyB3.npz` = powB3 + constCd + 24h（14 脚本）。

## 结果（真实运行输出，全文见 `_E12_run.log`）

**① 两个新成员自旋 + 保存**（24h = 4320 步）：
```
SE_p75 wind=3.33 m/s from 131 deg: |u|max=0.1069 mean=0.0245 vol_drift=0.00e+00 Cd=0.003517 mode=lake   [305.4 s]
saved flow_SE_p75.npz
N_p75  wind=5.17 m/s from  4 deg: |u|max=0.1497 mean=0.0385 vol_drift=0.00e+00 Cd=0.003600 mode=lake   [293.6 s]
saved flow_N_p75.npz
```
收敛性（trace，t=2h→24h）：SE_p75 |u|max 0.1004→0.1069（10 h 后稳定在 0.1062–0.1072），mean 0.0116→0.0245（14→24 h 仅 +2.5%）；N_p75 max 0.1447→0.1497（10 h 后 0.1492→0.1497，+0.3%），mean 0.03836→0.03850（14→24 h +0.4%）。**24 h 自旋已收敛**（后 10 h 变化 ≤2.5%），体积漂移 0。

**② 与旧场景对照的投放**（同一 drop (−1300,−200)，thr 全部一致：peak0=9.8e-5，thr=4.9e-6）：
```
new_SE_p75  area=0.0675 km2  centroid=(-1534,-29)  eig=65/76 m  theta=156.1 deg
old_SE_2p5  area=0.0650 km2  centroid=(-1525, -5)  eig=68/73 m  theta=146.5 deg
new_N_p75   area=0.0625 km2  centroid=(-1258,-481) eig=66/75 m  theta=145.2 deg
old_N_3p0   area=0.0600 km2  centroid=(-1296,-421) eig=66/77 m  theta=161.5 deg
```

**③ 流场统计与分解（锚点，24h @2.5 m/s 135°）**：
```
A powB3+lakeCd                    |u|max=0.0681 mean=0.01517  Cd=0.002463
B exp+lakeCd                      |u|max=0.0833 mean=0.02208  Cd=0.002463
C exp+constCd1.3e-3               |u|max=0.0618 mean=0.01577  Cd=0.0013
A vs bathyB3 (Cd-only, powB3):    max=1.382 mean=1.415  (√τ 预测 1.376)
A vs new SE_p75 (wind-only):      max=1.570 mean=1.613  (√τ 预测 1.592)
C vs old SE_2p5 36h (残差):       max=0.933 mean=0.921
bathyB3 vs C (bathy-only):        max=0.798 mean=0.680
new SE_p75 vs old SE_2p5 (总):    max=1.615 mean=1.430
new N_p75  vs old N_3p0  (总):    max=2.086 mean=1.861
```
B vs C（Cd-only, exp 域）：max=0.0833/0.0618=**1.348**，mean=0.0221/0.0158=**1.400**（√τ 预测 1.376）。

**④ 强流区占比与最大流速位置**：
```
flow_SE_p75  max @(-2581,-1335)=0.1069   |u|>0.02: 60.2%  |u|>0.05: 3.7%
flow_N_p75   max @(  269, -285)=0.1497   |u|>0.02: 79.6%  |u|>0.05: 26.9%
flow_SE_2p5  max @( 3669,-1035)=0.0662   |u|>0.02: 34.0%  |u|>0.05: 0.3%
flow_N_3p0   max @(  269, -285)=0.0718   |u|>0.02: 46.0%  |u|>0.05: 1.5%
```

## 结论

**改动有效，两个 p75 成员在生产默认下可用；流场量级可预测、覆盖面积仅小幅变化。**

1. **可运行性**：SE_p75 / N_p75 均以生产默认（powB3 + cd_lake + n=0.0238 + Smag 0.29）24 h 收敛（max 10 h 后稳定，mean 末 10 h ≤2.5%），vol_drift=0；文件带完整元数据（cd_used/cd_mode/n_manning/wind_*），可直接进 03/04/19 管线。
2. **新成员 vs 旧场景**：SE_p75 |u|max=**0.1069**/mean=**0.0245** m/s（旧 0.0662/0.0171 → **+61.5%/+43.0%**）；N_p75 **0.1497**/0.0385（旧 0.0718/0.0207 → **+108.6%/+86.0%**）；|u|>0.05 m/s 的强流区占比 SE 0.3%→3.7%、N 1.5%→26.9%。**覆盖面积**：SE 0.0650→**0.0675 km²（+3.8%）**、N 0.0600→**0.0625 km²（+4.2%）**（≈有效半径 +2%）；质心位移 ≤71 m，椭圆主轴角偏移 10–16°。
3. **差异可完全分解**（SE，max 逐项乘：0.798×1.382×1.570×0.933 = **1.615**，与实测总比值完全一致；mean 组合同样精确）：水深 B3 −20%（max）/ −32%（mean）；Cd 1.3e-3→cd_lake(3.33)=3.517e-3 **+38%**；风 2.5→3.33 m/s **+57%**；旧文件残差（n=0.022 vs 0.0238 + 36h vs 24h）−7%。各效应近似独立、可用 √(Cd·U²) 线性叠加预测。
4. **关键发现：两个 p75 成员都落在 cd_lake 拟合段（1.6–3.0 m/s）之外，且 Cd 封顶**。cd_lake 单调上升到 **U≈3.40 m/s 即贴上 3.6e-3 上限**（此后对所有更高风速恒为 3.6e-3）：SE p75 (3.33 m/s) = 3.517e-3（恰在封顶前），N p75 (5.17 m/s) 无 clip 给 5.85e-3 → 被截为 **3.6e-3**（应力仅为未截断的 62%）。√τ 链×bathy×残差 = 2.135 vs 实测 2.086（−2.3%）；若忽略 clip 直接外推，N_p75 应力再 +63%（属超参数化区）。**必须文档化**：p75/p90 场景成员的强度（尤其 N 扇区）由 clip 上限 3.6e-3 决定，与常数 Cd 场景的差异被压缩到 ≤2.77×。
5. **对下游的含义**：相对阈值（thr_rel=0.05 演示值）协议下覆盖面积对流场强度不敏感（+4%），与 E1（Cd 不影响覆盖）/E3（面积不敏感、位置敏感）一致——**链路在物理阈值口径下不能因此松动**（E4：物理 thr_rel≈0.18–0.49，覆盖按 E4 曲线坍缩；p75 更强混合对绝对剂量阈值的净效应需按 E4 联标表重估，本实验相对阈值不变）。位置/轨迹、强流区形态与下游混合显著改变，**04 优化与 E13 管线的风场景系综应换入新成员并重跑**。
6. **口径提醒**：三旧场景文件为旧基线（exp + 常数 Cd + n=0.022，36h）且无 Cd/n 元数据；新文件全量元数据，引用数字时按"flow_SE_p75@powB3+lakeCd/24h"标注版本。
