# E8：B3 生产水深落地复核（domain.py 生产切换 + A/B3 环流与投放复测）

日期：2026-08-24。模块：`model_Two-dimensional_water_flow/`。

## 动机（文献/问题）

E0（`report/实验记录_EXPERIMENTS.md`）基于刘惠 2019（42 实测点）建议采用 **B3 幂指数水深** d = 4.66·(1−exp(−(dist/L)^p))，L=440、p=0.39（锚定实测均值 2.48 m / 最大 4.66 m），作为生产水深（42 点 RMSE 1.02→0.49）。

本轮代码落地后需要复核，防止"建议"与"生产实现"脱节：
1. `src/swflow/domain.py` 生产水深已切到 `mode='powB3'`（`BATHY_B3 = dict(dmax=4.66, L=440.0, p=0.39, mean_target=2.48, ...)`），旧指数式（exp，均值 2.21/最大 4.75，L=381）另存为 `data/processed/domain_exp.npz` 基线；
2. `src/swflow/deployment.py` 的 `make_tracer/sim_drop` 现在自动从 flow dict 读取 wind_mps/wind_dir 并应用 **windage w_a=0.02**（`WINDAGE_DEFAULT = 0.02`）；
3. `src/swflow/swe_si.py` 的 `SweConfigSI` 默认 `cd_mode='lake'`（注意：脚本 14 调用 `wind_stress(*Wind, cd=cfg.c_d_wind)` 时未传 cd_mode，取 `wind_stress` 默认 `'constant'` → 实际仍为常数 Cd=1.3e-3，与 E0-c 配置一致，环比不受 cd_lake 影响）。

问题：迁移后的 domain.npz 是否与 E0 结论一致？A vs B3 的环流差/覆盖差是否复现？新部署层（windage 2%）下的投放测试是否仍支持"覆盖对水深不敏感"？

## 方法

| # | 命令 | 内容 |
|---|---|---|
| 1 | `python scripts/12_validate_bathymetry.py` | 对**生产 domain.npz** 做 42 点验证（表1+0.12==表2 内部校验 42/42） |
| 2 | `python scripts/13_bathy_rbf.py` | 以 **domain_exp.npz 为基线 A**，A/B/B2/B3/C/D 六候选 RMSE + D/B LOOCV；另存 domain_rbf.npz/更新 domain_meta.json/重绘 fig07 |
| 3 | `python scripts/14_bathy_circulation_effect.py` | A vs B3 的 24h SE 2.5 m/s 定常风自旋（n=0.0238、Smagorinsky、dt=20s）+ 同一投放测试（(−1300,−200)，2h，σ0=25m，thr=5%，n=2500，rng_seed=7）；存 flow_SE_2p5_bathyB3.npz/fig08 |
| 4 | 补充检查（独立脚本，未改任何 src/scripts） | ① B3 的逐折 LOOCV（13 脚本未内置打印）；② 精确拟合 (L,p) vs 生产取整值的差异；③ domain_exp/domain.npz 网格一致性 |

## 结果（真实运行输出）

### 1) 脚本 12（生产 domain.npz）
```
=== internal check: Table1 depth + 0.12 == Table2 H ===
mismatches: NONE (42/42 OK)
model domain: area=31.22 km2, L=440.0, mean_target=2.48 max_target=3.70
=== measured vs reconstructed (n=42) ===
measured: mean=3.07  min=1.98  max=3.72
model   : mean=2.78  min=1.81  max=3.69
bias (model-measured) = -0.293 m
RMSE = 0.486 m
MAE  = 0.377 m
R    = 0.757
rel. err (|err|/obs) mean = 12.5%
shallow subset (obs<3.17): bias -0.249 RMSE 0.481 n=21
deep subset   (obs>=3.17): bias -0.338 RMSE 0.492 n=21
```

### 2) 脚本 13（基线 A = domain_exp.npz；约 1–2 分钟完成，图已重生成）
```
used points: 42
A exponential: RMSE=1.015 bias=-0.241 R=0.764
B power-exp fit: Dmax=3.68 L=69.2 p=0.41  RMSE=0.324 bias=-0.000
   field mean=2.87 max=3.56
B2 fixed-Dmax fit: L=247.8 p=0.25  RMSE(42)=0.327  field mean=2.88 max=3.67
B3 fixed-Dmax+mean fit: L=440.0 p=0.39  RMSE(42)=0.489  field mean=2.48 max=3.71
C GLOBathy linear: RMSE=1.780 bias=-1.492  field mean=1.01 max=4.64
D RBF-corrected: RMSE=0.824 bias=-0.216  field mean=2.21 max=4.35
D LOOCV RMSE=0.760 bias=-0.122
B LOOCV RMSE=0.349 bias=+0.001
saved domain_rbf.npz + meta
saved fig07_bathy_validation.png
```
（fig07 时间戳 22:13 已更新 = 本次重生成。）

### 3) 脚本 14（约 16 分钟，图/流场已重生成）
```
A_exp: |u|max=0.0618 mean=0.0158  (depth mean=2.21 max=4.64)
B3_power: |u|max=0.0493 mean=0.0107  (depth mean=2.48 max=3.70)
flow |u| diff: mean=0.0062 max=0.0291 (of base mean 0.0158)
A drop @(-1300,-200) 2h: area=0.0650 km2  centroid=(-1525,-6)  theta=173.3
B3 drop @(-1300,-200) 2h: area=0.0600 km2  centroid=(-1516,-3)  theta=174.7
saved fig08
```
（fig08/flow_SE_2p5_bathyB3.npz 时间戳 22:24 = 本次重生成。）

### 4) 补充检查
```
B3 LOOCV RMSE=0.485 bias=-0.314
B3 exact fit: L=439.9621 p=0.3931
B3 exact-fit RMSE=0.4889 bias=-0.2942  field mean=2.4800 max=3.7103
B3 rounded(440/0.39) RMSE=0.4864 bias=-0.2931  field mean=2.4832 max=3.7047
masks/xs/ys/dx: domain_exp.npz 与 domain.npz 完全一致 (205x231, dx=50)
```
注：脚本 13 本身只内置了 D/B 的 LOOCV；B3 未打印，本记录独立复算＝0.485（E0 记录为 0.478，差异来自逐折 LSQ 起点/收敛的微小差别，两种口径均与样本内 0.489 一致 → 无过拟合证据）。

## 结论（改动是否有效 + 数字）

1. **B3 生产水深有效，与 E0 结论完全一致**：生产 domain.npz 42 点 RMSE=0.486（bias −0.293、MAE 0.377、R 0.757、相对误差 12.5%），相对旧指数基线 A（RMSE 1.015）**降低 52%**；场均值 2.48 m / 场最大 3.70 m（目标最大 4.66 为公式渐近值，湖内不达，口径按 E0："标定目标 4.66/实测场最大≈3.7"）。B3 LOOCV 0.485 ≈ 样本内 0.489，无过拟合。生产取整参数 (440, 0.39) 与精确拟合 (439.96, 0.3931) 的 RMSE 差仅 0.49→0.486 m（取整损失可忽略）。
2. **A vs B3 环流效应复现**：峰值流速 0.0618→0.0493 m/s（**−20%**）、均值 0.0158→0.0107 m/s（**−32%**）、流场差 mean 0.0062 / max 0.0291 m/s——与 E0-c（0.0618/0.0158 vs 0.0495/0.0108；0.0062/0.029）一致，E0-c 数字在代码迁移后仍成立。
3. **投放测试（新部署层 windage=2% 自动生效）**：覆盖面积 A 0.0650 vs B3 0.0600 km²（**−7.7%**），仍支持"单次覆盖对水深不敏感"的结论；质心相对 E0-c 的无风漂移版本（A: (−1267,−257)）向 NW 漂移 ≈360 m（=0.02×2.5 m/s×2h，与 E17 的"~350 m/2h"一致）——这是 **windage 默认化带来的预期变化，非水深效应**，theta≈174° 与风应力方向一致。
4. **方法学注**：脚本 14 虽运行于 `cd_mode='lake'` 默认的代码基线，但 `wind_stress` 未传 cd_mode、取默认 'constant'（Cd=1.3e-3），故 E0-c 环比未被 cd_lake 污染；cd_lake 的流速增益（E1-v2，+9~+43%）是另一独立实验。

**总体：E8 复核通过——B3 生产水深（domain.npz, powB3: 4.66/(440, 0.39)）落地正确，42 点 RMSE 0.486、环流 −20~−32%、覆盖不敏感三项结论均在代码迁移后成立。** 输出产物：`data/processed/domain.npz`（生产）、`domain_exp.npz`（旧基线）、`bathy_validation.npz`、`domain_rbf.npz`、`domain_meta.json`（bathy_mode=powB3）、`flow_SE_2p5_bathyB3.npz`、`figures/fig07`、`figures/fig08`（均已重生成，时间戳 22:13/22:24）。
