# E9：湖面 Cd 生产验证 — cd_mode='lake'（cd_lake）vs 常数 1.3e-3

- 日期：2026-08-24
- 脚本：`scripts/tmp_e9_verify.py`（运行日志：`report/experiments/_E9_run.log`）
- 结果流场：`data/processed/flow_tmp_e9_{SE_2.5,N_3.0,W_2.0}_{lake,const}.npz`（临时，未覆盖生产流场 `flow_*_cdlake.npz` 等）

## 动机（文献/问题）

优化方案 A2「风拖曳系数：弃常数 1.3e-3」尚未落地到生产默认值。依据：

- Zhang, Chen & Brett (2024, Water Resources Research 60:e2023WR035914, 东湖同尺度浅湖物理池实验) Fig.4b：**弱风 U10 在 1.6–3.0 m/s 时湖面 Cd 为海洋线性外推的 1.0–3.1 倍**（正相关分支，r²=0.901）；Eq.11 波依赖 Cd 本身在东湖均衡 SMB 波假设下崩溃（见 E1）。
- 工程默认对照：Delft3D Cd=0.0025，MIKE21 用 0.0016–0.0026——现行常数 1.3e-3 **低于两套工程默认下限**；Wu(1980) 更小（@2.5 m/s 仅 0.9625e-3）。
- E1v2（`15_wave_dependent_cd.py`）用「cd_lake 拟合 + 35% 风区长度空间调制」得到流速 +9~+43%，但那是独立实验路径。本轮 E9 验证的是**生产路径**：`SweConfigSI(cd_mode='lake')`（新默认）+ `wind_stress(..., cd_mode=cfg.cd_mode)` 解析 Cd，即纯 Fig.4b 线性拟合（无风区调制），含裁剪 [1.2e-3, 3.6e-3]。

## 方法

- 单元检查：`cd_lake(U)` 与 `wind_stress` 的 lake/constant/wu 三种模式数值。
- 对比运行：三场景 SE_2.5(2.5 m/s, 135°)、N_3.0(3.0 m/s, 0°)、W_2.0(2.0 m/s, 270°)，各用
  `SweConfigSI(dx=50, dt=20, n_manning=0.0238, use_adv=True, use_coriolis=True, nu_mode='smag', cs=0.29, cd_mode='lake')`
  与 `cd_mode='constant'`（c_d_wind=1.3e-3）跑 24 h 自旋（4320 步），风应力 `wind_stress(spd, dir, cd=1.3e-3, cd_mode=cfg.cd_mode)`。
  域：`data/processed/domain.npz`，205×231、dx=50 m、12487 湿格、水深 mean 2.48 / max 3.70 m。
- 输运对比：SE 场景两套流场各做一次 `sim_drop((-1300,-200), T_h=2, thr_rel=0.05, n=2500)`；
  流场 dict 含 wind_mps/wind_dir，粒子按生产路径自动应用 windage w_a=0.02。

## 结果（真实运行输出）

### 1. 单元检查

```
[0.0018279999999999998, 0.002463, 0.003098]          # cd_lake(U) for U=(2.0,2.5,3.0)
(np.float64(-0.01333415564079076), np.float64(0.013334155640790758), 0.002463)   # lake @2.5,135
(np.float64(-0.0070379221814973565), np.float64(0.007037922181497356), 0.0013)   # constant @2.5,135
(np.float64(-0.005210769307454774), np.float64(0.005210769307454773), 0.0009625) # wu @2.5,135
```

公式核对：cd_lake(2.0)=1.32e-3+1.27e-3×0.4=1.828e-3 ✓；cd_lake(2.5)=1.32e-3+1.27e-3×0.9=2.463e-3 ✓；cd_lake(3.0)=1.32e-3+1.27e-3×1.4=3.098e-3 ✓（本风段未触发裁剪）。

### 2. 六次 24h 自旋 + sim_drop（日志原文）

```
== domain: 205x231, dx=50 m, wet=12487, depth mean=2.483 max=3.705 m

### scenario SE_2.5: U=2.5 m/s dir=135 deg
  cd_lake=0.002463   cd_const=0.0013   ratio=1.895
  tau_lake=(-0.01333, 0.01333)  tau_const=(-0.007038, 0.007038)
  24h spin lake  : |u|max=0.0681  |u|mean=0.0152  (295 s)
  24h spin const : |u|max=0.0493  |u|mean=0.0107  (306 s)
  ratio max=1.382  mean=1.415
  speed ratio lake/const: wet-mean=1.461  min=0.00  max=301.72  p10=1.28 p90=1.61
  eta lake: max=0.0028 min=-0.0051 | eta const: max=0.0015 min=-0.0028

### scenario N_3.0: U=3.0 m/s dir=0 deg
  cd_lake=0.003098   cd_const=0.0013   ratio=2.383
  tau_lake=(-0, -0.03416)  tau_const=(-0, -0.01433)
  24h spin lake  : |u|max=0.0807  |u|mean=0.0207  (226 s)
  24h spin const : |u|max=0.0520  |u|mean=0.0131  (282 s)
  ratio max=1.553  mean=1.573
  speed ratio lake/const: wet-mean=1.603  min=0.00  max=29.10  p10=1.42 p90=1.80
  eta lake: max=0.0070 min=-0.0064 | eta const: max=0.0029 min=-0.0027

### scenario W_2.0: U=2.0 m/s dir=270 deg
  cd_lake=0.001828   cd_const=0.0013   ratio=1.406
  tau_lake=(0.008957, 1.645e-18)  tau_const=(0.00637, 1.17e-18)
  24h spin lake  : |u|max=0.0412  |u|mean=0.0095  (168 s)
  24h spin const : |u|max=0.0343  |u|mean=0.0078  (168 s)
  ratio max=1.201  mean=1.219
  speed ratio lake/const: wet-mean=1.225  min=0.00  max=6.23  p10=1.13 p90=1.34
  eta lake: max=0.0023 min=-0.0017 | eta const: max=0.0017 min=-0.0012

### sim_drop SE field: drop=(-1300,-200) T_h=2h thr_rel=0.05 n=2500
  drop in-lake: True  (cell j=95 i=73)
  [lake] area_km2=0.068  centroid=(-1492, -36)  theta=176 deg  peak0=9.8e-05
  [const] area_km2=0.060  centroid=(-1516, -3)  theta=175 deg  peak0=9.8e-05

== E9 summary ==
SE_2.5   U=2.5 cd: lake=0.002463 const=0.0013 | |u|max 0.068 vs 0.049 (x1.38) | |u|mean 0.0152 vs 0.0107 (x1.42)
N_3.0    U=3.0 cd: lake=0.003098 const=0.0013 | |u|max 0.081 vs 0.052 (x1.55) | |u|mean 0.0207 vs 0.0131 (x1.57)
W_2.0    U=2.0 cd: lake=0.001828 const=0.0013 | |u|max 0.041 vs 0.034 (x1.20) | |u|mean 0.0095 vs 0.0078 (x1.22)
done
```

注：speed ratio 的 min=0/max=301 为近岸弱流格点除小量的数值伪影，稳健区间取 p10–p90；三场景湿格速度比均值 1.46/1.60/1.23 与 |u|mean 比值一致。eta 量级约为常数版 2 倍，与应力比 1.4–2.4× 相符（无非物理增长，24 h 稳定）。

## 结论（改动是否有效 + 数字）

**改动有效**。生产路径 `cd_mode='lake'`（纯 cd_lake 拟合，无风区调制）相对常数 Cd=1.3e-3：

- Cd：2.0/2.5/3.0 m/s 分别为 1.828/2.463/3.098e-3（×1.41 / ×1.90 / ×2.38），落在 Zhang 2024「1.0–3.1×」弱风结论带内；Wu(1980)（@2.5 仅 0.9625e-3）低于常数版，明确不可用。
- 流速：三场景 |u|mean +21.9% / +41.5% / +57.3%（0.0078→0.0095 / 0.0107→0.0152 / 0.0131→0.0207 m/s），|u|max +20% / +38% / +55%（W/SE/N）；湿格速度比均值 1.23/1.46/1.60。较 E1v2「+9~+43%」更强（E1v2 的风区调制平均≈1.0×，差异来自 35% 调制系数的拉平效应）。
- 输运（SE 场，2 h 单点投放）：覆盖率 0.068 vs 0.060 km²（**+13%**），漂移方向几乎不变（theta 176° vs 175°，质心位移 ~252 m vs ~292 m）——短时覆盖指标对 Cd 版本敏感性低，但长时（≥6 h）漂移与 MIKE21 量级对比必须标注 Cd 版本（延续 E1 结论）。
- 上游口径影响：生产流水线若沿用常数版数字（如 02 系列），流速将系统性低估 ~20–60%。建议：落地后重跑 02/03/04 优化与 04b 多种子，并在所有含流速/漂移的报告中标注 Cd 版本（A2 落地项）。

附加：单次 24 h 自旋 168–306 s（本机多会话并发负载下），无收敛告警（cg 全程 info=0，日志无 WARN）。
