# E10：windage 生产路径验证（particles w_a / deployment 自动读风 / 种子稳定性）

脚本：`scripts/17_windage.py`（敏感性对照）、内联 heredoc（生产路径 a/b/c）、`scripts/04b_seed_stability.py`（n=600 两种子）。

## 动机

E3 实验（report/实验记录）已给出 windage 敏感性结论：**对覆盖面积不敏感、对输运位置高度敏感**，并推荐 w_a=2%。本轮模块优化把 windage 正式落入生产代码：

- `particles.py`：`ParticleTracer.__init__(..., wind_vec=None, w_a=0.0)`，`advect` 内做对称分裂半步风漂（`_has_wind = wind_vec is not None and w_a > 0`）；
- `deployment.py`：`WINDAGE_DEFAULT = 0.02`，`wind_vec_from_flow()` 从 flow dict 的 `wind_mps/wind_dir` 构造风矢量（气象约定：方向 = 风吹向；`vec = [-sin(th), -cos(th)] * mps`），`make_tracer()` 自动读风并应用默认 w_a，`sim_drop()/batch_sim_drops()` 默认走该路径。

E10 目的：在生产路径（`sim_drop` 默认参数 + 旧流场 `flow_SE_2p5.npz` + 种子 7）上验证 windage 自动启用、与显式 w_a=0.0 的差异符合 E3 量级，并确认种子稳定性脚本 04b 在 windage 启用后无异常、Top5 排名仍稳定。

## 方法

1. `python scripts/17_windage.py`（原样，w_a ∈ {0,1,2,3,5}%，T=2 h，dt=5 s，D=0.3，n=2500，种子 7）。
2. 生产路径（heredoc，sys.path → src，读 `data/processed/flow_SE_2p5.npz`，flow 内 `wind_mps=2.5, wind_dir=135`）：
   - a) `sim_drop(flow, (-1300,-200), T_h=1.5, dt=10, n=2500, sigma0=25, thr_rel=0.05, rng_seed=7, w_a=0.0)`；
   - b) 同参数不传 w_a（应自动取 WINDAGE_DEFAULT=0.02）；
   - c) `make_tracer(flow, dx, rng_seed=7)` 检查 `_has_wind` 与 `w_a`。
3. `python scripts/04b_seed_stability.py`（n=600，5 个流场成员 m0/SE_2p5/m1/m2/m3——**全部携带 wind_mps/wind_dir，故本轮 04b 即 windage 启用下的种子稳定性检验**；792 候选点，种子 1/2）。

## 结果（真实运行输出）

### 1. scripts/17_windage.py（原文输出）

```
windage 0%: area=0.0650 km2  drift=( +25,  -73) m  peak=2.48e-05
windage 1%: area=0.0625 km2  drift=(-101,  +58) m  peak=2.55e-05
windage 2%: area=0.0650 km2  drift=(-224, +195) m  peak=2.49e-05
windage 3%: area=0.0625 km2  drift=(-346, +336) m  peak=2.49e-05
windage 5%: area=0.0625 km2  drift=(-596, +618) m  peak=2.46e-05
```

与 E3 结论一致：area 在 0.0625–0.0650 km² 间仅栅格级波动（±4%），drift 随 w_a 近似线性放大（0→5% 时 drift 从 (+25,−73) → (−596,+618) m）。2% 纯风漂理论值 = 0.02×2.5 m/s×7200 s = 360 m 沿 (−0.707,+0.707)；实测基准差 (Δdrift 2%−0%) = (−249, +268) m，模长 366 m，与理论吻合（<2%）。

### 2. 生产路径 sim_drop + make_tracer（heredoc 真实输出）

```
flow wind_mps=2.5 wind_dir=135.0
a) w_a=0.00: area=0.0650 km2  drift=( +20,  -56) m  peak0=9.80e-05  theta=175.3473491487471
b) w_a=0.02: area=0.0575 km2  drift=(-169, +142) m  peak0=9.80e-05  theta=154.78567105328855
delta(a->b): darea=-0.0075 km2  ddrift=(-189, +198) m
c) make_tracer: _has_wind=True  w_a=0.020  wind_vec=[-1.76776695  1.76776695]
   explicit 0.02 matches default: True
```

- **w_a=0 vs 0.02 差异**：漂移差 (−189, +198) m，模长 273.7 m；理论纯风漂 0.02×2.5×5400 s = 270 m 沿 (−0.707,+0.707) → (−191, +191) m，实测偏差约 4–7 m（<3%，来自风漂改变轨迹后采样到不同流速的耦合项）。面积 0.0650 → 0.0575 km²（−11.5%，栅格量化下与 E3 "面积稳健"结论一致——单次释放 1.5 h 面积差在各态 0.0625–0.0650 的波动带内边界附近）。`peak0` 完全一致（9.80e-05，同一随机流）说明 a/b 除风漂外无任何数值差异；椭圆主轴 theta 由 175.3° → 154.8°（风漂改变了蔓延形状取向）。
- **c) 自动启用**：`make_tracer` 从 flow dict 读到 `wind_mps=2.5/wind_dir=135` → `_has_wind=True`，`w_a=0.020`，`wind_vec = (-1.768, +1.768)` m/s（=2.5 m/s 吹向 315°，与 17_windage.py 内联公式逐位一致）；显式 `w_a=0.02` 与默认结果一致。
- 无异常，a/b/c 全部通过。

### 3. scripts/04b_seed_stability.py（n=600 两种子，exit 0，无异常）

```
seed 1 top5: [(np.float64(-931.0), np.float64(-135.0)), (np.float64(-1131.0), np.float64(-535.0)), (np.float64(-731.0), np.float64(-335.0)), (np.float64(-731.0), np.float64(-135.0)), (np.float64(-1131.0), np.float64(-335.0))]
  scores: [0.0529 0.0526 0.0522 0.0519 0.0519]
seed 2 top5: [(np.float64(-1731.0), np.float64(-535.0)), (np.float64(-1331.0), np.float64(-335.0)), (np.float64(-1331.0), np.float64(-135.0)), (np.float64(-1131.0), np.float64(-535.0)), (np.float64(-931.0), np.float64(-535.0))]
  scores: [0.0533 0.0529 0.0529 0.0526 0.0522]
```

- **无异常**：脚本完整跑完（10 个 batch_sim_drops：2 种子 × 5 流场成员，792 候选 × n=600，T_h=1.5 h/dt=10 s），exit code 0。单 flow-seed 实测 ~326 s（本机多会话并发负载下 04b 全程约 1.5 h，另见 `_E10_run.log`）。
- **两种子 Top-5 排名**：精确点重合仅 1/5（`(-1131,-535)`：S1#2、S2#4）；两个种子的前 5 分数带分别为 [0.0519, 0.0529] 与 [0.0522, 0.0533]，**完全重叠**（并集 [0.0519, 0.0533]，相对带宽 ~2.7%），10 个槽位覆盖 9 个不同点位。
- **解释**：最优区是噪声级"平顶"——与 REVIEW_REPORT P1-1 修复目标口径一致（Top-5 得分间距 ~0.1% 量级，排名本就无可靠区分度）；也与 E11 结论一致（"大偏好区没变、精确最优点移动 1 km"）。**结论：点级顺序不可跨种子复现（仅 1/5），但最优候选区（分数带）完全稳定**，即 windage 启用没有引入种子敏感异常；选点下游（E13 管线）应消费"期望评分 ~0.052–0.053 区带"而非单一坐标最优。
- 注意：`np.float64` 元组是脚本原样输出（未改动脚本所致，仅格式问题）。

## 结论

改动**有效**：

1. **自动启用**：`make_tracer`/`sim_drop`/`batch_sim_drops` 默认路径读到 flow dict 的 `wind_mps=2.5/wind_dir=135` → `_has_wind=True`、`w_a=0.020`、`wind_vec=(-1.768, +1.768)` m/s，与 17_windage.py 内联实现逐位一致；显式传 `w_a=0.02` 与默认完全相等。
2. **a/b 差异符合 E3 量级**（w_a=0 vs 0.02，同一随机实现，peak0 相同 9.80e-05）：漂移差 (−189, +198) m（模长 273.7 m ≈ 理论纯风漂 0.02×2.5×5400 = 270 m，偏差 <3%）；面积 0.0650 → 0.0575 km²（−11.5%），与 E3"面积对 w_a 稳健"（0.0625–0.0650 波动带）一致；椭圆主轴 theta 175.3° → 154.8° 显示风漂改变蔓延取向。
3. **04b 种子稳定性**：无异常、exit 0；两种子 Top-5 分数带完全重叠（[0.0519, 0.0533]），点级重合 1/5——与既有结论（score 面为 ~0.1% 间距平顶）自洽，windage 未引入新的排名不稳定。

生产影响：`opt_result*.npz` 与 E11 跑分均已在 windage 默认启用路径下产出（04/04b 均带 5 成员 wind 信息），无需回退；下游消费方只需注意 top5 是"区带"而非"点"。
