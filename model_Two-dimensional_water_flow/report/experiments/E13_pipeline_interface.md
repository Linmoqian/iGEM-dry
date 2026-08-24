# E13：管线接口定稿演示 — opt_result → 物理阈值需求生成 → 异构多航次调度（端到端）

脚本：`scripts/21_pipeline_demo.py`（19_interface_mv_vrp.py 升级版）；运行日志：`report/experiments/_E13_run.log`

## 动机

E5（19_interface_mv_vrp.py，报告 §E5）的接口链路"水流模块点+评分 → 需求生成 → 时间矩阵 → 多机调度"已跑通，但结论④明确遗留待办：**需求生成函数用的是风险比例线性模型（1–3 载荷），真实剂量应由 E4 联标的物理阈值 (C0, t_safe, M) 决定**。E4 同时给出物理结论：物理 thr_rel≈0.18–0.49（演示值 5% 的 4–10 倍），单架次覆盖坍缩 6–60×，补偿路径 = "加大单架次剂量（M=5）或多点多架次"。

本轮模块优化（domain B3、swe_si `cd_mode='lake'`、particles windage、deployment `make_tracer` 自动读 wind、`physical_thr_rel()` 接口就位）后，本轮把该遗留接口定稿并做一次端到端演示：需求生成调用 **真实接口** `swflow.deployment.physical_thr_rel(2.85, 24.0, 25.0, 1.0)`（0.25 的物理阈值锚点归一），其余链路全部复用 E5；同时把接口契约（各阶段输入/输出字段）写为脚本 docstring。

## 方法

`21_pipeline_demo.py` 五阶段（与 E5 相同的链路，仅 Stage B 需求生成换为真实物理接口）：

- **Stage A 上游**：读 `data/processed/opt_result.npz`（792 候选 + 5 风场景成员评分 + 斑块掩膜），`score = member_scores.mean(axis=0)` 取 Top-8。
- **Stage B 需求生成（定稿）**：`thr_phys = physical_thr_rel(C0=2.85 µg/L 包络上限, t_ok=24 h, T_water=25 °C, M=1)`（=D_req/M）；`dose_i = max(1, round(2*s_i/s_max * (1 + 2*thr_phys/0.25)))`，其中 0.25 = M=1/24h 的物理阈值锚点；dose_i 个载荷单元 ⇒ 该点等效 M_eff = dose_i×M（E4 的"加大剂量"补偿链路的自动实现）。
- **Stage C**：流场坐标（米，原点 114.3956E/30.5566N）→ 路径规划框架（km，LAKE_CENTER 30.5667/114.3833，等距圆柱投影）。
- **Stage D**：风修正非对称时间矩阵（同路径规划 `wind_time_matrix` 公式：SE 2.5 m/s，v0=15，safety=1.25，hover=0.13 min/航段）。
- **Stage E**：路径规划模块 3 机（cap 4/4/6 kg，en 28/28/34 min，spd 15/15/13 m/s），列表调度（最早完工机优先 + 风险优先序装填 + 每架次 NN+2-opt + 容量/续航约束），慢机时间 = T×15/SPD。（E5 原样复用。）
- **单机基线**：cap 6 kg、15 m/s、同 2-opt 顺序执行；指标：每机架次汇总、makespan、加速比、评分加权交付 Σs_i·dose_i、评分/分钟。
- **契约诊断变体**（同接口同贪心，仅钉死续航语义）：E5 原门限为"累计 elapsed + t_rt > EN[m]"（续航当作累计软约束，且 E5 自身输出已越限 31.4>28 ·min）；变体门限改 "t_rt > EN[m]"（续航=单架次电池、架次间换电）。

接口契约（写入脚本 docstring，字段级）：Stage A in `cands (N,2)/scores (N,)/member_scores (E,N)/patch (Ny,Nx)`；Stage B in `(C0,t_ok,T_w,M,s_i,s_max)` out `thr_phys, dose_i`；Stage C in `pts 米 + 投影原点` out `pts_km`；Stage D in `xy, WIND, v0, safety, hover` out `T (n,n) min 非对称`；Stage E in `CAP/EN/SPD + visits 风险序` out `每机架次表/ makespan / 单机基线 / 加速比 / 评分·分钟`。

## 结果（真实运行输出，python scripts/21_pipeline_demo.py）

```
=== Stage A: 水流模块输出 data/processed/opt_result.npz ===
候选点 792, 风场景成员 5; Top-8 期望保护评分:
  #0 (  -1931,   -335) m  score=0.0533
  #1 (  -1531,   -535) m  score=0.0533
  #2 (  -1131,     65) m  score=0.0526
  #3 (  -1531,   -335) m  score=0.0522
  #4 (   -731,   -135) m  score=0.0519
  #5 (  -1331,   -335) m  score=0.0512
  #6 (  -1531,     65) m  score=0.0512
  #7 (  -1731,   -535) m  score=0.0508

=== Stage B: 需求生成 (deployment.physical_thr_rel 真实接口) ===
thr_phys = physical_thr_rel(C0=2.85, t_ok=24h, T_water=25C, M=1) = 0.2465
剂量因子 (1 + 2*thr_phys/0.25) = 2.972
dose_i = max(1, round(2*s_i/s_max * 2.972)): [6, 6, 6, 6, 6, 6, 6, 6]
总载荷单元 = 48  (E5 风险比例需求为 17)  => 物理阈值剂量放大 x2.8

=== Stage C: 坐标换算 流场(米) -> 路径规划 (km) ===
  #0  pp=( -0.75, -1.45) km  dose=6  (M_eff=6 x M=1)
  #1  pp=( -0.35, -1.65) km  dose=6  (M_eff=6 x M=1)
  #2  pp=(  0.05, -1.05) km  dose=6  (M_eff=6 x M=1)
  #3  pp=( -0.35, -1.45) km  dose=6  (M_eff=6 x M=1)
  #4  pp=(  0.45, -1.25) km  dose=6  (M_eff=6 x M=1)
  #5  pp=( -0.15, -1.45) km  dose=6  (M_eff=6 x M=1)
  #6  pp=( -0.35, -1.05) km  dose=6  (M_eff=6 x M=1)
  #7  pp=( -0.55, -1.65) km  dose=6  (M_eff=6 x M=1)

=== Stage D: 时间矩阵 T (min, 非对称; SE 2.5 m/s) ===
  T[depot北岸 -> tasks]: [7.55 7.67 6.74 7.4  6.95 7.34 6.85 7.74]
  T[tasks -> depot北岸]: [7.55 7.67 6.74 7.4  6.94 7.34 6.85 7.74]

=== Stage E: 机队 3 机 (cap [4, 4, 6] kg, en [28.0, 28.0, 34.0] min, spd [15.0, 15.0, 13.0] m/s) 列表调度+NN+2-opt ===
drone 0 (cap 4 kg, en 28 min, spd 15 m/s): 累计 174.6 min
  sortie 1: 4 载荷, 点序 ['p0', 'p0', 'p0', 'p0'], t=15.1 min (累计 15.1 min)
  sortie 2: 1 载荷, 点序 ['p2'], t=13.5 min (累计 28.6 min)
  sortie 3: 1 载荷, 点序 ['p3'], t=14.8 min (累计 43.4 min)
  sortie 4: 1 载荷, 点序 ['p3'], t=14.8 min (累计 58.2 min)
  sortie 5: 1 载荷, 点序 ['p4'], t=13.9 min (累计 72.0 min)
  sortie 6: 1 载荷, 点序 ['p4'], t=13.9 min (累计 85.9 min)
  sortie 7: 1 载荷, 点序 ['p5'], t=14.7 min (累计 100.6 min)
  sortie 8: 1 载荷, 点序 ['p5'], t=14.7 min (累计 115.3 min)
  sortie 9: 1 载荷, 点序 ['p5'], t=14.7 min (累计 130.0 min)
  sortie 10: 1 载荷, 点序 ['p6'], t=13.7 min (累计 143.7 min)
  sortie 11: 1 载荷, 点序 ['p7'], t=15.5 min (累计 159.1 min)
  sortie 12: 1 载荷, 点序 ['p7'], t=15.5 min (累计 174.6 min)
drone 1 (cap 4 kg, en 28 min, spd 15 m/s): 累计 188.2 min
  sortie 1: 4 载荷, 点序 ['p0', 'p0', 'p1', 'p1'], t=16.0 min (累计 16.0 min)
  sortie 2: 1 载荷, 点序 ['p2'], t=13.5 min (累计 29.4 min)
  sortie 3: 1 载荷, 点序 ['p3'], t=14.8 min (累计 44.2 min)
  sortie 4: 1 载荷, 点序 ['p3'], t=14.8 min (累计 59.0 min)
  sortie 5: 1 载荷, 点序 ['p4'], t=13.9 min (累计 72.9 min)
  sortie 6: 1 载荷, 点序 ['p4'], t=13.9 min (累计 86.8 min)
  sortie 7: 1 载荷, 点序 ['p5'], t=14.7 min (累计 101.5 min)
  sortie 8: 1 载荷, 点序 ['p5'], t=14.7 min (累计 116.2 min)
  sortie 9: 1 载荷, 点序 ['p6'], t=13.7 min (累计 129.9 min)
  sortie 10: 1 载荷, 点序 ['p6'], t=13.7 min (累计 143.6 min)
  sortie 11: 1 载荷, 点序 ['p6'], t=13.7 min (累计 157.3 min)
  sortie 12: 1 载荷, 点序 ['p7'], t=15.5 min (累计 172.8 min)
  sortie 13: 1 载荷, 点序 ['p7'], t=15.5 min (累计 188.2 min)
drone 2 (cap 6 kg, en 34 min, spd 13 m/s): 累计 183.9 min
  sortie 1: 6 载荷, 点序 ['p2', 'p2', 'p1', 'p1', 'p1', 'p1'], t=17.9 min (累计 17.9 min)
  sortie 2: 2 载荷, 点序 ['p2', 'p2'], t=15.5 min (累计 33.5 min)
  sortie 3: 1 载荷, 点序 ['p3'], t=17.1 min (累计 50.6 min)
  sortie 4: 1 载荷, 点序 ['p3'], t=17.1 min (累计 67.6 min)
  sortie 5: 1 载荷, 点序 ['p4'], t=16.0 min (累计 83.6 min)
  sortie 6: 1 载荷, 点序 ['p4'], t=16.0 min (累计 99.7 min)
  sortie 7: 1 载荷, 点序 ['p5'], t=16.9 min (累计 116.6 min)
  sortie 8: 1 载荷, 点序 ['p6'], t=15.8 min (累计 132.4 min)
  sortie 9: 1 载荷, 点序 ['p6'], t=15.8 min (累计 148.2 min)
  sortie 10: 1 载荷, 点序 ['p7'], t=17.9 min (累计 166.1 min)
  sortie 11: 1 载荷, 点序 ['p7'], t=17.9 min (累计 183.9 min)
makespan (3 drones) = 188.2 min   (drone1 瓶颈)

单机基线 (cap 6 kg, 15 m/s): makespan 116.4 min, 8 架次
  sortie 1: 6 载荷, 点序 ['p0','p0','p0','p0','p0','p0'], t=15.1 min
  sortie 2: 6 载荷, 点序 ['p1','p1','p1','p1','p1','p1'], t=15.3 min
  sortie 3: 6 载荷, 点序 ['p2','p2','p2','p2','p2','p2'], t=13.5 min
  sortie 4: 6 载荷, 点序 ['p3','p3','p3','p3','p3','p3'], t=14.8 min
  sortie 5: 6 载荷, 点序 ['p4','p4','p4','p4','p4','p4'], t=13.9 min
  sortie 6: 6 载荷, 点序 ['p5','p5','p5','p5','p5','p5'], t=14.7 min
  sortie 7: 6 载荷, 点序 ['p6','p6','p6','p6','p6','p6'], t=13.7 min
  sortie 8: 6 载荷, 点序 ['p7','p7','p7','p7','p7','p7'], t=15.5 min
加速比 (单机/三机) = 0.62x  => 三机协同收益 +-38%

=== 契约诊断: 续航语义 (同一接口/贪心, 门限 t_rt<=EN 每架次) ===
drone 0: 4 架次, 累计 59.3 min
drone 1: 4 架次, 累计 60.9 min
drone 2: 3 架次, 累计 51.8 min
makespan = 60.9 min ; 单机 116.4 min ; 加速比 1.91x => 三机协同收益 +91%

评分加权交付 (sum s_i*dose_i) = 2.4980 ; 总载荷 48 单元
评分/分钟: E5原语义三机 0.01327 ; 单机 0.02145 ; 变体(每架次续航)三机 0.04101
```

## 结论

**接口定稿：有效。** ① 端到端链路（opt_result → 真实 `physical_thr_rel` → 剂量 → 坐标 → 风修正 T → 机队调度）一次跑通，需求生成无任何硬编码：`thr_phys = 0.2465`（C0=2.85/24h/25°C/M=1 的真实接口返回值），`dose_i = [6]*8`，总载荷 48 单元（E5 的 17 的 2.8 倍）；② 物理含义闭环：每点 M_eff=6 ⇒ thr_eff = 0.2465/6 ≈ 0.041，按 E4 面积-阈值锚点插值单点有效覆盖 ≈0.070 km²，**恢复并略超演示值（0.065 km²@5%）**——"E4 覆盖坍缩 → 加大剂量补偿"链条由接口自动实现，E5 待办 ④ 落地。

**但演示暴露调度器契约歧义 ⇒ 结果反转：** ① 按 E5 原语义（续航=累计软门限）复用，3 机 makespan **188.2 min 劣于单机 116.4 min（0.62x，-38%）**——48 单元下 36 架次中 33 架次被压成单载荷碎片（每架次固定往返 13–15.5 min），三机协同负收益；② 同一接口同一贪心、仅把续航语义钉死为"每架次电池、架次间换电"（门限 t_rt ≤ EN），makespan 降至 **60.9 min vs 单机 116.4 min ⇒ 1.91x（+91%）**，评分/分钟 0.04101 vs 0.02145（+91%）。

**三点落定**：① 契约定稿——Stage E 写入"续航=单架次、架次间换电"语义（E5 原实现的累计门限属歧义，且其自身输出已越限 31.4>28 min；语义修正已写入 21 脚本 docstring 与诊断段，19 未改动）；② 待办——该语义修正应同步到路径规划模块调度器（未在本脚本落地）；③ 建模备注——T[i,i]=0（同点重复载荷不增收航段/悬停费）使"同点打包 6 件"近乎零边际成本，单机基线的 116.4 min 因此偏乐观，后续需在契约中注明（或按多载荷投放的现场操作时间计）。
