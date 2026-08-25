# 五模型 × Web 平台集成修改方案（V1）

> 目标：把「二维浅水流 / 浓度标定 / MC-LR 降解动力学 / 任务级路径规划 / total MC·MC-LR 风险估计」五个模型，按上下游关系联成一条可演示、可追溯的闭环管线，并以 design-assets/page-objectives-redesign-v2/ 的 V2/V4/V5 设计图为基准改造现有 Web 平台（总览 / 地图监视 / 数据分析 / 设备配对），实现「风险识别 → 水流推演 → 剂量决策 → 路径执行 → 效果复核」的可视化闭环。
>
> 本方案内容包括：①现状盘点与差距；②统一数据契约；③五个模型各自的修改方案（含优先级）；④管线网关（pipeline-server）设计；⑤Web 四页改造方案；⑥设计图不合理之处与修正建议；⑦分阶段实施路线与验收；⑧风险与边界。**所有未完成现场标定的数字，在页面上一律标注「原型参数」并同时显示区间/超阈概率，不得显示为确定结论。**

---

## 0. 结论速览（30 秒版）

1. **五模型上下流关系已成立且「契约已定稿、实现未落地」**：三份五模型联动报告（标定 report/07、降解 report/05、路径 report/06）已经把接口字段、时序语义和级联不确定度方案写清；缺口集中在 ①每模型服务化 API；②统一管线网关；③Web 尚无服务层与模型数据；④少量模型级「数字换锚」待办（降解 v1.2、C_req 联标、标定 fuse、路径 v3.0 契约修复）；⑤redo_v2 本地源码缺失。
2. **推荐改造顺序**（依赖驱动，不能倒序，最重要的「诚实性」红线）：降解模型先换锚（v1.2）→ 水流 C_req↔thr_rel 联标 → 标定 fuse()+p_env 升级 → 路径 v3.0 契约+目标函数 → redo_v2 服务化 → 管线网关（双模式：静态场景导出 + 在线推理）→ Web 四页改造（地图页三状态工作台为主）→ 端到端仿真复盘。
3. **Web 侧不做五页五模型独立页**（与设计 README 结论一致）：新增能力全部收敛到「地图监视」页的三状态工作台；其余三页只做轻量纠偏（数据分析页纠「预测」为「当前风险估计」，总览页补「模型链路/待治理任务」，设备页补「暗基线/校准状态/反应时间窗」）。
4. **地图页现状与设计不符，需要决策**：当前 MapMonitorPage 是 CSS 手绘示意图（未使用 Leaflet），而设计图为真实瓦片地图 + 矢量叠加层。方案给出「真实 Leaflet 模式（默认）+ 示意图降级」的双模式实现，避免演示现场断网/瓦片合规问题。
5. **设计图有 12 处需要修正/明确**（详见 §6），核心是：时间滑杆「+2 h/+6 h」与 redo_v2 nowcast 边界冲突、「推荐剂量 12 包/单次覆盖 0.05–0.08 km²」等数字必须带「原型参数」、80% 区间 4.80–8.10 μg/L 超出当前标定能力边界须标注来源通道。

---

## 1. 现状盘点

### 1.1 系统闭环与五模型定位（谁服务谁）

多源环境观测(水质/气候/遥感/历史毒素)
        ▼
[model_redo_v2] 风险估计(nowcast) ── ① 空间先验 p_env(C|x,t) + 热点候选
        ▼
水质环境数据 ── [浓度标定] 节点荧光→浓度 ĉ + CI + P(C≥1) + 旗标   ← 真值锚点（② 节点报警+估计+测量时刻 t_meas）
        ▼
[二维浅水流] 流场→漂移→投放点+覆盖面积+漂移时滞（③ 投放点位/面积/水动力时限）
        ▼
[MC-LR 降解动力学] 剂量-时间反演 → C_req/t_safe/dosage（④ 剂量与治理时长约束）
        ▼
[任务级路径规划] 多机分配+访问顺序+滚动重规划 → 投放计划（⑤）
        ▼
无人机投放 → 治理执行 → 节点复测 →（回环：标定/redo_v2 再学习）

- **统一语义**：全链共用 1 μg/L 阈值、小时/分钟时间单位、JSON + 版本 + 置信度输出契约；三份联动报告已确认「语义已对齐，缺口在实现与联调」。
- **级联不确定度预算（按对「达标时间」终局不确定度的贡献排序，来自降解报告 05 §4.4）**：降解 k（跨文献 3–4 个数量级，最大未知）> C0（标定 LOD 0.28–1.34 μg/L vs 东湖作业带 0.25–2.85 μg/L，低端重叠）> 风况（水流 5 成员系综 ±12%）> 到达抖动（分钟级）。**管线契约必须声明「各单位预算」，避免五模块平均用力。**

### 1.2 各模型现状与缺口清单

| 模型 | 当前状态 | 关键产出（已核实） | 面向管线/Web 的缺口 | 参考文档 |
|---|---|---|---|---|
| model_redo_v2（CMADRE v2） | 服务器锁定测试完成（v2 候选）；**本地 src/cmadre/*.py 源码缺失**（仅 pyc），完整源码在 model_redo_v2_server_20260810.tar.gz | {median, q10/q90, p_detected, p_exceedance, ood_score, feature_panel, version}；正式 run dirs 在服务器 | ①源码恢复；②东湖网格风险场导出（GeoJSON/栅格）；③作为标定 p_env 的网格先验；④推理服务化/Cache；⑤仅 nowcast，禁止滑杆外推 | report/MODEL_OBJECTIVE_SPEC.md、FINAL_MODEL_REPORT.md、SERVER_RUN_REPORT.md |
| model_concentration_calibration | v3.1 完成（合成数据为主）；已接入 33h 真湿实验工作簿；逐 trigger 拟合完成 | {mean, median, lo5, hi95, p_ge_1, grid, pmf}；deploy LUT（Q→C 查找表）；device 仿射校准 | ①fuse() 未实现（多节点×重复×时间×通道融合——真数据 z 分数表明单点不可靠，融合是必需）；②p_env 仍是静态对数正态 → 换 redo_v2 网格先验（未就绪时分区先验）；③输出契约标准化（含 t_meas/flags/trigger 符号）；④抑制型 trigger（2/3/7）作为独立证据通道 | report/03 终版、report/07 系统级衔接（§2 四项调整）、src/{forward,calibrate,deploy,device}.py |
| model_Two-dimensional_water_flow | 架构定稿；域/流场/粒子/投点优化全跑通（data/processed/*.npz 均在） | domain.npz、flow_*.npz（SE_2p5/N_3p0/W_2p0 + 4 成员系综 m0–m3）、opt_result.npz（792 候选 + member_scores + patch）、physical_thr_rel()、E13 端到端演示（scripts/21_pipeline_demo.py） | ①覆盖阈值仍是演示 5% → 与降解 C_req 联标；②无服务化查询/GeoJSON 出图接口；③节点位置用假设坐标；④与路径规划坐标换算（米→km，等距圆柱）需工具化 | MODEL_ARCHITECTURE.md、README、report/experiments/E13_pipeline_interface.md、scripts/21_pipeline_demo.py |
| model_MC-LR_degradation_kinetics | v1.1 灰箱原型 + 文献校准（fig1–fig7）；QA 04 判定「架构可上评审，数字先换锚」 | prototype_v1.py（C/L 两态 ODE + 环境修正 + MC 不确定带）、fit_literature.py、3 批新增真实数据（Mendeley k、Lake Erie 比例、东湖 2009 六点） | ①v1.2 换锚（A1–A7）：k_bg 分层先验、C_intra 默认开启（Lake Erie 胞内中位 90%）、删除 m6 k=0.25 伪影；②src/api.py 未实现（scenario/dose_response/t_safe_quantiles/sink_rate/C_req）；③C_req↔thr_rel 联标；④GBDT 代理（5×10⁴ 仿真→秒级查询）未做；⑤fig4–fig6 需按 v1.2 重生成 | report/04 质量审查、report/05 五模型协同（§3.2/§5 路线图）、src/prototype_v1.py |
| model_path_planning | V2.7 + V3 模块验证（M1–M7）；东湖场景 RL 推理 0.04 s | env.Instance{risk,demand,tw_end,T[k,i,j],drone_cap,drone_energy,drone_depot,eff_lag}；flow_tasks.py（v3.0 任务生成器，已消费 SWF+降解演示常数）；outA/outB/outC 模型 | ①v3.0 契约正式落地（替换 flow_tasks 中的演示标定常数）；②续航语义修正（每架次电池、架次间换电——E13 显示语义错误会让三机劣于单机 0.62×）；③目标函数 t_eff = t_arrive + T_drift + t_safe（治理生效而非到达）；④多访问完成时刻=第 demand 次；⑤计划/甘特/重规划事件输出服务化 | report/03、report/06（失配点 1–6）、report/09、code/{env,flow_tasks,evaluate,replan_demo}.py |

### 1.3 Web 现状（web/）

| 项 | 现状 | 与目标差距 |
|---|---|---|
| 技术栈 | Vite + React 18 + TS + Tailwind v4 + recharts + leaflet/react-leaflet/leaflet.heat + dnd-kit（依赖已装）；纯 SPA | 可沿用，无需更换框架 |
| 路由 | / 、/map 、/data 、/device 四页（App.tsx） | 与设计一致（新增能力不引新路由） |
| 数据层 | 全部手工 mock：src/data/demoReadings.ts（14 设备，字段仅 toxin/水温/pH/电量/信号）、mockPredictions.ts（假「未来 7 天」）；**无 src/services/** | 需新增服务层（fetch + mock 降级）；设备字段缺 DO/浊度/叶绿素/营养盐等 redo_v2 特征输入 |
| 地图页 | CSS 手绘湖面示意图+定位针（MapMarker 用 %坐标硬编码），未用 Leaflet；无图层/时间滑块/风险斑块 | 与设计图（真实瓦片图+矢量叠加）差距最大，为本次主改 |
| 数据分析页 | 有「AI 预测（未来 7 天）」+ 假「模型置信度 87%」+「下一高风险时间」 | 与模型能力（nowcast）直接冲突，必须纠偏 |
| 总览页 | KPI+系统状态+告警摘要+趋势+最新采样，基本对齐「总览页重设计.png」 | 补「模型链路」状态 + 「待治理任务」入口 + 最高风险卡跳转 |
| 设备配对页 | 设备 CRUD/配对模拟/拖拽排序 | 节点详情补「暗基线/校准状态/有效反应时间窗/trigger 构型」；无人机作为执行资源展示 |

### 1.4 设计资产结论（page-objectives-redesign-v2/README.md + 5 张成图）

- **总览页（重设计）**：轻改——KPI/系统状态/告警摘要/趋势/最新采样；按 README 还应补「模型链路」与「待治理任务」（成图中未体现，需补）。
- **地图监视页三状态（同路由、无新增导航）**：态势总览（图层胶囊 + 风险斑块 + 时间滑杆 + 右侧斑块证据卡 + 「生成治理方案」）→ 治理规划（投放点 1/2/3 编号 + 覆盖椭圆 + 无人机分色路线 + 右侧方案卡 + 「下发任务」）→ 方案推演-执行检查（V4/V5 定稿：候选方案对比 8/12/16 包 + 浓度与达标预测 + 剂量—时间决策面 + 执行前检查四项 + 右侧执行时间轴）。
- **数据分析页（v2/v4）**：删「AI 预测/置信度/下一高风险时间」；改「当前风险估计（非未来预报）」；加分析物切换（MC-LR / total MC）、80% 区间、超限概率 P(C≥1)、OOD 域外标记；参考 V4 修订（导航右上角用户区、导出按钮位置、吉祥物插图来源）。
- **设备配对页**：结构不变 + 节点详情扩展；无人机仅作资源。

### 1.5 湿实验分析结论对模型的硬约束（docs/Introduction 各报告）

| 结论（报告出处） | 对模型/接口的含义 |
|---|---|
| 响应以早期窗口为主（RFP 内参报告：峰值 2h，trigger1 Δ=0.2147；tig4567：2h 峰、幅度 0.14–0.21）；0–6 h 为预测导向主窗（0-6h AUC 报告） | 标定模型的**有效读取窗 = 2–6 h**（C-6 反应时间窗）；路径/任务时间轴以小时计；设备页展示「有效反应时间窗」 |
| trigger 优选结论不一：RFP 内参报告主推 trigger1/0；标定 07 报告逐时间 fold 复算主推 trigger5（正）与 trigger2（抑制），并指出 trigger1 的 24h 强响应主要是**归一化路径差异（DoubleNorm 的 0h 行位因子）** | **统一采用 per-time fold（Q/Q0 同时间 0 μg/L 对照）作训练口径**；DoubleNorm 只作诊断量；报告口径不一致处需在模型 README 记录（数据诚实性） |
| pmcy-GFP：浓度/时间显著但处理组低于对照（方向不利）；pmlrA：显著但缺 0h/OD；tig0123 仅有 0.5h | 仅作早期定性证据；**不得作为定量候选**进入标定训练主体（07 报告星评：★★★） |
| 均为 3 技术重复、无独立生物学重复；部分 A 行（0 μg/L 对照）存在孔位异常；缺 OD600 | **最低数据契约**：板位随机化 + OD600 + ≥3 批生物学重复 + 每板空白/哨兵；否则标定结论只能算「方法验证」（07 报告 §4.4 发现 1–3） |
| 建议 signal/OD600 与 Δ(signal/OD600) 为主指标（tig4567 报告 §6） | 与 C-6 一致；设备字段需含 OD600 或菌量近似（未来硬件/QF 通道） |

---

## 2. 统一数据契约（先冻结，再动手改代码）

> 这是整个改造的第一件事：**冻结 schema（JSON Schema 四件套 schema_version / model_version / units / confidence）**，五个模型与 Web 只消费标准记录；任何演示数字必须带 provenance: 「prototype」或真实来源。

### 2.1 信封（所有管线输出共用）

```json
{
  "schema_version": "1.0",
  "model_version": "cmadre_v2 | calib_v3.1 | swf_v1.2 | degr_v1.2 | pp_v3.0",
  "data_version": "hash or run-id",
  "units": {"concentration": "ug/L", "length": "m", "time": "min"},
  "confidence": {"level": "prototype|calibrated|site-validated", "note": "单点1μg/L检出不可靠，需多通道融合"},
  "generated_at": "2026-08-27T09:42:00+08:00",
  "provenance": {"source": "…", "seed": 0, "run_dir": "…"}
}
```

### 2.2 五个标准记录（各模型生产者 → 统一消费者）

① calibration_record（标定 → 流场/降解/路径/Web）
```json
{"node_id":"aq-006","lat":30.5699,"lng":114.3864,"trigger_id":"trigger6","sign":"+",
 "t_meas":"2026-08-27T09:40:00+08:00","fold":1.31,
 "c":{"median":6.35,"lo5":4.80,"hi95":8.10},"p_ge_1":0.96,
 "flags":["low_snr"],"qc":{"rfp_cv":0.033,"n_reps":3,"biorep":1},
 "env_prior":{"kind":"grid|zonal|lognormal","params":{}}}
```

② risk_field（redo_v2 → 标定 p_env / 流场热点 / Web 图层）
```json
{"target_kind":"mc_lr","extent":[[30.52,114.33],[30.62,114.44]],
 "grid": {"nx":200,"ny":200,"cells":["median","q10","q90","p_exceedance","ood_score"]},
 "sources":["node-calibrated 6.12","cmadre-nowcast 6.58"],
 "horizon":"nowcast","model_version":"cmadre_v2","data_version":"…"}
```

③ flow_result（水流 → 降解/路径/Web）
```json
{"wind":{"speed_ms":2.5,"dir":"SE"},"scenario":"SE_2p5","members":5,
 "drop_points":[{"id":"D1","x_m":-1931,"y_m":-335,"lat":30.565,"lng":114.381,
   "score":0.0533,"a_drop_km2":0.070,"drift_centroid":null,"drift_theta_deg":15}],
 "patch_mask":"geojson-url","coverage_thr":{"kind":"c_req","value":0.05,"note":"C_req联标后替换演示5%"}}
```

④ degradation_decision（降解 → 水流/路径/Web）
```json
{"C0_ugL":{"median":2.85,"lo5":1.0,"hi95":6.0},"dose_per_pack_ugL":0.9,
 "scheme":{"packages":12,"D_eff":6.0},"t_safe_h":{"median":5.6,"p90":8.1},
 "window":{"light_survival_h":24,"second_drop_needed":true,"second_drop_after_h":24},
 "infeasible":false,"decision_conf":{"level":"prototype","note":"k_bg/工程菌k未锚定"}}
```

⑤ task_plan（路径 → 执行/Web）
```json
{"mission_id":"TS-0825-03","assets":[{"id":"A","type":"uav","cap_packs":6,"battery_pct":87}],
 "routes":[{"uav":"A","legs":["depot-north","D1","D3","depot-north"],"packs":[6,6],"eta_min":8.4}],
 "timeline":[{"t":"09:45","event":"publish"},{"t":"09:53","event":"arrive","uav":"A"}],
 "gantt":[{"uav":"A","kind":"flight","start_min":0,"end_min":20}],
 "metrics":{"risk_weighted_eff_time_min":16.6,"coverage_km2":0.9,"unserved":0}}
```

### 2.3 时序与坐标系约定

- **时刻语义**：t_meas（采样时刻，标定时间轴）≤ t_publish（任务发布）= t_meas + 决策延迟；t_arrive（路径规划）；t_eff = t_arrive + T_drift + t_safe（治理生效，全链统一目标）。路径规划重规划事件与标定测量时刻必须在同一时间轴上。
- **坐标**：水流模型输出为米（原点 114.3956E/30.5566N，等距圆柱），路径规划用 km（LAKE_CENTER 30.5667/114.3833），Web 用 WGS84。**必须提供官方换算工具 pipeline_server/utils/geo.py**，禁止各模块私自从常数推导（E13 注释 T[i,i]=0 同点打包零边际成本导致单机基线偏乐观，契约须注明）。
- **不确定度**：上游只传「紧凑分布」（中位数+分位数+概率），不用原始 MCMC 样本横穿 5 个模型；Web 端不再二次积分。

---

## 3. 模型侧修改方案（按模型，含优先级）

> P0 = 阻断项（不先做后面全是错的）；P1 = 联调/服务化必需；P2 = 体验/长期。

### 3.1 model_redo_v2（CMADRE v2）—— 风险估计上游

| ID | 改动 | 优先级 | 说明与验收 |
|---|---|---|---|
| R-1 | **恢复源码**：从根目录 model_redo_v2_server_20260810.tar.gz 解出 src/cmadre/*.py、configs/、run_train.py、run_validate.py、pyproject.toml、tests/，与服务器 /home/linux/igem-cmadre 逐文件比对（SHA-256） | P0 | 现本地只有 pyc（src/cmadre/__pycache__）；README 中「源代码恢复后再读」即指此项。恢复后 pytest 13 项通过 |
| R-2 | 建立**东湖网格风险场导出器** src/cmadre/export_grid.py：给定经纬度边界 + 分辨率（建议 200×200）→ 批量推理 → risk_field 记录（中位数/q10/q90/p_exceedance/ood_score）→ 输出 GeoJSON（web 图层用）+ npz（下游仿真用） | P1 | 复用 CLI 推理；对每个网格点组装 core_field 特征（东湖站点无对应观测则用季节/流域先验 + 缺省指示）；对外明确 nowcast；网格推理做 LRU 缓存 |
| R-3 | **p_env 接口**：暴露 p_env_at(lat, lng, t) → {median, q10, q90, ood}，供标定 invert_posterior(c_prior=…) 替换静态对数正态 | P1 | 标定 report/07 §2A 的「先验升级」落地；未就绪时用分区先验（湖湾/开阔水域/入湖口）兜底，页面标注「分区先验」 |
| R-4 | 服务化推理适配器 pipeline_server/adapters/cmadre.py：加载 run dir（runs/total_mc_source_ood_v2 等，正式 run 在服务器需同步/或本地 smoke run 仅作冒烟） | P1 | 输出 schema 2.2②；失败时返回 confidence.level=「prototype」且字段带 null，不许静默降级为旧模型 |

**注意**：redo_v2 的能力定位是「统计上诚实的 nowcast 研究基线」。**Web 上任何「未来滑杆/预测 3 天」的表层都不可以挂到它头上**（设计图「+2h/+6h」滑杆问题见 §6 第 1 条）。

### 3.2 model_concentration_calibration —— 感知层/真值锚点

| ID | 改动 | 优先级 | 说明与验收 |
|---|---|---|---|
| C-1 | **实现 fuse()**（src/calibrate.py 或新 src/fuse.py）：fuse(posterior_list) 在多节点×重复×时间×触发通道的对数浓度网格上相乘再归一化（triggers 按符号通道；负响应取 |Δ| 作独立证据） | **P0** | 真实数据 z 分数：trigger5 单点 z≈2.0、trigger1/6 仅 0.3–0.5 —— 单点单通道无法 3σ 检出 1 μg/L；融合是「必需接口」而非增强。验收：N 节点×3 重复×3 时点的 z 提升曲线（√N 趋势），并给出**有效独立样本数保守估计**（同一装置多次读数不独立） |
| C-2 | **p_env 升级**：invert_posterior(..., c_prior=grid_prior)；内部先查 redo_v2 p_env_at()（R-3），未命中则分区先验，再退化静态对数正态；输出记录含 env_prior.kind | P1 | 消除「平台区后验扑向高浓度」病灶；相邻节点同读数不同后验 |
| C-3 | **输出契约标准化**：build_calibration_record(...) 输出 2.2①字段（node_id/trigger_id/t_meas/fold/ĉ/ci/p_ge_1/flags/qc/model_version）；t_meas 必须为采样时刻 | P1 | 下游只消费契约字段，不读取底层荧光；路径重规划事件与 t_meas 同轴 |
| C-4 | **抑制通道纳入**：拟合结果 trigger2/3/7 为抑制型（Amax −0.27/−0.33/−0.37，trigger2 在 1 μg/L z=−2.6）——部署组合为「阳性通道 + 阴性对照」联合诊断 | P1 | 抑制通道异常 = 体系/基质问题，与阳性通道联合提高特异度；成本为零（不需要改生物构造） |
| C-5 | **Web/网关适配器** pipeline_server/adapters/calibration.py：加载 deploy artifact（LUT JSON）+ 设备仿射参数（a/b/暗基线）→ 节点读数转 calibration_record；对时间用最近节点插值（连续插值列为后续项） | P1 | 与 device.py 的仿射+暗基线扣除一致；edge（ESP32）端仍用 LUT 解析反演 |
| C-6 | 装置协议补充：每周期暗电流基线、RFP 单色标样、荧光珠哨兵；**行位随机化 + 独立生物重复 + OD600**（湿实验侧联动，报告 07 §4.4 最高优先级修复） | P2 | 板位混杂会污染 fold，属「湿实验→模型」接口要求，写入数据契约 |

### 3.3 model_Two-dimensional_water_flow —— 推演层

| ID | 改动 | 优先级 | 说明与验收 |
|---|---|---|---|
| W-1 | **C_req↔thr_rel 联标**：用降解层 C_req(C0, env, D_max) 输出替换 physical_thr_rel 演示锚点/5% 相对阈值；输出「东湖场景群的门限换算表」（C0×T_limit×环境 → thr_rel），覆盖面积随 thr_rel 重新计算 | **P0** | 联标前，README/E13 所有覆盖面积数字都只能作为「演示值」。验收：同一风况下 thr_rel 从 5% 变为 C_req 标定后的新值，单次覆盖面积给出新区间 |
| W-2 | **服务化查询器** pipeline_server/adapters/swf.py：读取 data/processed/{domain,flow_*,opt_result}.npz → 提供 flow_snapshot(scenario, hour)（u,v,η 稀疏箭头）、drop_candidates()（Top-K + score + member_scores）、bloom_patch_geojson()、coverage_ellipse(point_idx, thr_rel) | P1 | 全部输出转 WGS84 GeoJSON；流场用稀疏箭头（每 500 m 一支）控制体量；**缓存优化后 npz 为服务启动时加载一次（加载 <2 s，不做在线 SWE 求解）** |
| W-3 | **漂移-衰减修正接口**：drift_forecast(node_pos, t_meas, wind_scenario, horizon_h) → 菌团轨迹/质心/椭圆 + 漂移时间尺度 T_drift（供标定最优读取窗 2–6 h 与路径 eff_lag） | P1 | 与 E13/README 的「最优点=斑块中心偏上风侧，预补偿自动实现」一致 |
| W-4 | 节点坐标真实化：检测节点坐标不再用假设值，改由标定/设备注册表提供；**投放点-检测点联合布点**（流场+路径联合优化，报告 07 §7 第 5 项） | P2 | 使「水流最优投放点能覆盖到真实节点报警的斑块」可被验证 |
| W-5 | 文档同步：README/IntroductionMD 中所有「演示值」（5% 阈值、0.038–0.080 km²）加版本标记与 C_req 联标前声明 | P1 | 诚实性红线（iGEM 评审） |

### 3.4 model_MC-LR_degradation_kinetics —— 剂量层（**先换锚，再服务化**）

| ID | 改动 | 优先级 | 说明与验收 |
|---|---|---|---|
| D-1 | **v1.2 换锚包（A1–A7）**：k_bg 分层先验（无生命 ≤0.03 / USGS 0–0.56 / Mendeley <0.22μm 0.17–0.64、<0.45μm 0.22–≥0.77 d⁻¹，删失用区间似然；m6 0.25 h⁻¹ 降为「完成时间刻度参考」）；**C_intra 默认开启**（Lake Erie 胞内中位 90%；输出「溶解态达标」与「胞内释放情景」双场景）；f_LR 站点先验（Lake Erie 0.278、东湖待测，不进机理内核）；东湖 2009 C0 场景库（0.25–2.85 μg/L 六点）；函数型式降级为「形状假设」；fig4–fig6 用 v1.2 参数重生成 | **P0** | QA 04 判定「数字先换锚」；**管线联调必须在换锚之后**，否则伪影固化进管道。验收：参数溯源台账（每个先验 → 文献原文行号+采样窗口），fig4–6 数字与报告口径一致 |
| D-2 | **实现 src/api.py（v1.3 服务化，纯函数 + JSON 契约）**：scenario()（标定/redo_v2 双来源合并 → C0~N(μ0,σ0²)+来源旗标+ood 门槛）、dose_response(C0, env, T_limit, alpha) → {D*, dosage_ugL, cells_L, packages}、t_safe_quantiles(C0, D, env) → {median, p90}、sink_rate(...) → r、C_req(...) → 最小有效菌密度 | P1 | 供水流（P0 联标）、路径（demand/due_min/lag）、Web（剂量卡）。双来源合并规则待拍板：**建议 触发用 redo_v2 p_exceedance、剂量计算用标定 ĉ**（标定缺失/ood 超限时以预测为情景、实测为校准） |
| D-3 | **投放时滞输入**：B0(t)=B0·H(t−T_arrive)（Heaviside 延迟投放），并把 T_arrive 抖动并入机会约束 P(t_safe+T_arrive≤T_limit)≥1−α | P1 | 与路径「t_eff」完全互洽；这是「到达≠生效」的模型侧钉死 |
| D-4 | **GBDT/GP 仿真代理**：5×10⁴ 机理仿真 → 代理模型 → 秒级剂量查询（供路径规划迭代与 Web 交互「改包数立即看达标时间」） | P1 | 参照「物理引导 ML」路径（报告 05 §4.5）；验收：代理误差边界标定（相对全 MC 的 ≤5%/≤10% 分位） |
| D-5 | 部署 contract/degradation.schema.json + degradation_decision 生产者（2.2④）；不可行域（白色区域/「72 小时不可达」）显式输出为 infeasible 与「升级处置建议」 | P1 | 路径/Web 消费；**不可行时禁止 Web 用「加包」暗示可解**（设计图「增加用量 33%」仅对 A/B/C 三者可比时成立） |

### 3.5 model_path_planning —— 执行层

| ID | 改动 | 优先级 | 说明与验收 |
|---|---|---|---|
| P-1 | **v3.0 契约正式落地**：flow_tasks.py 中演示标定常数（K_BASE=0.25、F_D0=0.15、PACK_DOSE=1.0、T_LIMIT=360、SEP_M=300 等）全部改为调用 D-2/D-3 真实接口与水流 W-1 结果；任务=斑块级单元（两层：斑块级 → Top-K 投放点级） | **P0** | 验收：任务库的 demand/tw_end/eff_lag 与降解水流输出对得上一一对应的 hash |
| P-2 | **续航语义修正**：调度器/评分器统一为「续航=单架次电池、架次间换电」（E13 契约诊断：修复后 3 机 makespan 60.9 vs 单机 116.4，1.91×；若不修则 0.62× 负收益）；同点重复载荷（T[i,i]=0）按「多载荷投放现场操作时间」计费 | **P0** | 同步修改 env.py/solvers.py 与 E13 脚本 docstring；验收：E13 复跑给出 1.91× 且能量审计 100% 通过 |
| P-3 | **目标函数 v3.0**：Σ w_j·S_j·t_eff_j（t_eff = t_arrive + T_drift + t_safe）；软窗 = 降解 t_safe 分位 + 迟到惩罚 λ 与「加剂量的边际成本」耦合；多访问任务完成时刻=第 demand 次访问 | P1 | 保留统一评分器回放审计（保证各方法可比）；--use-edge --tanh-prior --mode flow 重训 outC′ |
| P-4 | **机会约束/场景采样**：任务属性带紧凑分布，POMO S=32 场景采样（风况成员×降解分位数），输出 P(t_eff≤T_limit) 与「置信等级」 | P1 | 不加「再传播一层 MC」（与报告 06 §4.3 一致） |
| P-5 | **服务化适配器** pipeline_server/adapters/planner.py：载入 outB′/outC′ ckpt（CPU <5 ms）→ plan(mission) → task_plan（2.2⑤：routes/gantt/timeline/ETA/重规划事件） | P1 | 供 Web「治理规划」与「执行时间轴」；失败回退 贪心+LS（<0.1 s）并标注算法回退 |
| P-6 | 动态重规划事件流：replan_event(t, new_alerts) → 增量任务库 + 新路线（保留 RL 事件重规划 demo 的结论：优势取决于警报风险与到达时机，展示时注明是演示） | P2 | 与「复测排程/新警报注入」联动的 Web 演示条目 |

---

## 4. 管线网关 pipeline-server（模型 → Web 的桥）

### 4.1 形态与位置

- 新增仓库根目录 pipeline-server/（Python 3.11，FastAPI + uvicorn，可选 pydantic v2 schema 校验），**不做数据库**（演示期用 JSON 产物 + 内存缓存；如需历史落盘用 SQLite）。
- 依赖五模型目录在本仓库的相对路径（model_*），通过 adapters/ 单文件封装每个模型（只 import 各模型 src/，不改模型源码语义）。
- 命令：uvicorn pipeline_server.main:app --port 8010；Web 侧 Vite 代理 /api → http://127.0.0.1:8010。

### 4.2 端点（初版）

| 端点 | 用途 | 主要响应 |
|---|---|---|
| GET /api/v1/health、GET /api/v1/models/status | 五模型可用性/版本/置信等级 | 模型状态卡片（总览页「模型链路」） |
| GET /api/v1/overview | 总览页聚合 | KPI、最新读数、告警、**待治理任务**、模型链路 |
| GET /api/v1/risk/field?target=mc_lr&t=… | 风险面（redo_v2 nowcast + 节点标定融合） | risk_field GeoJSON（地图图层） |
| GET /api/v1/nodes/{id}/calibration | 节点证据卡 | calibration_record |
| GET /api/v1/flow/snapshot?scenario=SE_2p5&h=1 | 水流/风场箭头 | GeoJSON 线集 + 稀疏向量 |
| GET /api/v1/governance/draft?patch_id=… | 生成治理方案 | 投放点+覆盖椭圆+剂量+窗口+任务库（**核心复合端点**） |
| POST /api/v1/plan/generate | 立即生成路径计划 | task_plan（routes/gantt/timeline） |
| POST /api/v1/plan/{id}/replan | 注入事件重规划 | 增量计划 |
| POST /api/v1/scenario/replay | 演示回放（一个东湖风况日时间线） | 事件流（供 Web 时间轴滑块） |
| GET /api/v1/degradation/decide?C0=…&env=… | 剂量决策卡 | degradation_decision |

### 4.3 双模式（关键工程决策）

| 模式 | 适用 | 做法 |
|---|---|---|
| **A. 静态场景导出（默认，演示/答辩首选）** | Web 无后端、断网演示 | pipeline-server/scripts/export_demo_scenario.py 预生成「东湖 2026-08-27 高风况日」的完整 JSON 包（含 24 h 风险面/流场/一次治理方案/任务甘特/复测）→ web/src/data/pipelineScenario.json + web/public/assets/pipeline/（GeoJSON/PNG）。Web 服务层优先读它 |
| **B. 在线推理（联调/真机可选）** | 展开复盘、增量更新 | 同上端点实时计算；模型未就绪的字段返回 confidence=「prototype」与 null，**前端必须渲染占位徽章而非报错** |

**建议节奏**：先做 A（1–2 天，独立于模型服务化），保证 iGEM 演示稳定；A 稳住后再接 B。

### 4.4 场景包内容（export_demo_scenario.py 产出字段）

scenario（风/时间基线）、nodes（12 个模拟节点+真实检测参数）、risk_field、risk_patches（2–3 个椭圆斑块，含来源/区间/OOD）、governance_draft（4 投放点+覆盖椭圆+12 包+达标区间）、task_plan（3 机路线+甘特+时间轴）、degradation_curve（中位+90% vs 1 μg/L 线）、dose_decision_surface（低分辨率剂量×时间热图）、exec_check（无人机电量/天气窗 2.6 m/s 适宜/通信 4/4 在线/复测 12:00 已排程）、replay_events（发布→首架到达→投放完成→节点复测→预计达标→复检关闭）。

---

## 5. Web 平台修改方案

### 5.0 总原则

1. **不改四页路由与主导航**（遵循设计 README）；不新增「模型页」；新增能力进地图页。
2. **新增服务层**：src/services/（pipelineApi.ts 优先读场景包→可选 fetch 网关→最终 mock 兜底）；src/types/pipeline.ts（对准 §2 契约）；src/utils/（风险色阶/区间格式化/时间轴工具）；src/data/mockScenario.ts（阶段一占位，字段与场景包一致）。
3. **文案规则**（设计 README §关键文案规则 + 模型诚实性）：「风险估计/当前状态估计」，不用「未来 7 天预测」；浓度必须带区间；1 μg/L 决策必须带 P(C≥1)；OOD 显示「模型域：域内/域外」；未标定数字带「原型参数」徽章。
4. **设备字段扩展**：demoReadings 增加 do、turbidity、chlorophyll_a、tn、tp、calib_state、dark_baseline、react_window_h、trigger_id、qf_flags（同时服务 redo_v2 特征与标定证据卡）。

### 5.1 总览页（轻改，对照「总览页重设计.png」+ README 补充项）

- 系统状态卡内新增**「模型链路」**横条：5 个模型节点（风险估计→浓度标定→水流推演→剂量决策→路径执行），每节点显示 状态点（就绪/演示/未接）+ 版本徽章（如 CMADRE v2 · nowcast、标定 v3.1 · 原型参数）；点击跳到地图对应图层。
- 告警摘要新增**「待治理任务」**（≥1 时橙色按钮）→ 跳 /map?state=governance&mission=TS-…。
- 最高风险卡（6.35 μg/L）改为可点击 → 跳地图并定位斑块；卡片同时显示「P(C≥1) 96%（原型）」小字。
- 趋势概览改为「近 7 天均值（节点融合）」，只到当前时间，不画虚线延长。

### 5.2 地图监视页（主改 —— 三状态工作台）

**布局**：外壳沿用 aqua-panel + 顶部页头；左侧地图区（flex-1）+ 右侧 420px 信息栏；页内状态切换（态势总览 / 治理规划 / 方案推演）为顶部胶囊，同路由 /map，状态存 useSearchParams。

**状态 A：态势总览**
- 地图：真实 Leaflet（react-leaflet + OSM 瓦片，[30.52,114.33]→[30.62,114.44] 边界，比例尺/缩放控件）；叠加层与图层胶囊一一对应：MC-LR风险（节点标定融合，绿黄橙红连续热力，默认开）、预测风险（CMADRE v2 nowcast，蓝紫等值面+虚线边缘，默认关）、设备（状态色定位针，默认开）、水流场（青色稀疏流线/箭头，附 m/s）、风场（深蓝稀疏箭头，关）、投放覆盖（青绿半透明椭圆，关）、不确定性（区间宽度半透明，关）。
- 风险面渲染：优先 GeoJSON 等值面（Leaflet polygon 简化或 leaflet.heat 强度点集二选一，**推荐等值面**因为要表达区间/OOD 语义）；热力与等值面可切换，防止「热力图=预测」的误解。
- 右侧斑块证据卡：名称（EL-R03）/风险等级/MC-LR 中位数+80% 区间/超限概率 P(C≥1)/数据可信度/证据来源（检测节点标定 x.xx vs 环境风险估计 x.xx 两条）/现场条件（水温/流速/主流向）/OOD 关注 徽章。
- 时间滑杆（当前 / +30 min / +2 h / +6 h）：**只允许推演「物理层」**（流场漂移/降解曲线/任务状态），风险面保持 nowcast（加「风险面为当前状态，不随时间滑杆外推」的说明文案）。
- 主按钮「生成治理方案」→ 状态 B；次按钮「查看节点证据」。
- **降级模式**：?mock=1 或瓦片加载失败时回退现有 CSS 示意图 + 矢量叠加（设计图元素仍按数据驱动渲染，只是底图换成品牌插画）。

**状态 B：治理规划**
- 主视图切换为「投放覆盖 + 无人机路线」：候选投放点 D1/D2/D3/D4 编号（绿色圆标）+ 覆盖椭圆（半透明青绿，随 thr_rel(C_req) 变化）+ 无人机路线（分色：A 蓝实线/B 紫虚线，箭头方向）+ 风险斑块轮廓保留。
- 右侧「治理任务方案 TS-XXX-03」卡：目标斑块/投放点 4 个/推荐包数/单点覆盖（带「原型参数」徽章）/治理预期（预计达标 5.6 h、90% 区间 4.2–8.1 h、目标浓度 MC-LR<1 μg/L、**是否需要二次投放**）/无人机任务摘要（航线、投放量、首达时间）/总航程/任务完成 16.6 min。
- 主操作「确认并下发任务」（写入时间轴）+「重新计算」（调 POST /api/v1/plan/generate，没有后端时用场景包+重采样）+「返回推演」。
- 底部图例条：推荐投放点/有效覆盖/无人机 A/无人机 B。

**状态 C：方案推演-执行检查（V4/V5 版式）**
- 中央工作区 4 块：候选方案对比（方案 A 8 包 / B 12 包【推荐】/ C 16 包，展示预计达标时间、覆盖率、主要取舍，如「补投风险较高/综合平衡量最优/用量增加 33%」——**取舍文案必须由剂量-时间面计算得出，不得手写死**）；浓度与达标预测（三条候选曲线 + 1 μg/L 目标线 + 90% 区间 + 「预计 5.6 h 达标」标注）；剂量—时间决策（连续决策面热图 + 当前选中点 12 包/5.6 h——**用 degradation dose-time surface 数据，不使用随机彩色渐变**）；执行前检查（无人机 A/B 电量与就绪状态、天气窗口 09:45–11:30 / 风速 2.6 m/s · 适宜、通信链路 4/4 在线·信号正常、复测排程 12:00·已加入任务——四项来自 task_plan + 执行状态，标注「演示数据」）。
- 右侧已选方案摘要（12 包/5.6 h/4.2–8.1 h/方案有效期（**由窗口定义，见 §6 第 2 条**））+ 任务执行时间轴（09:45 发布任务 → 09:53 首架到达 → 10:04 投放完成 → 12:00 节点复测 → 15:30 预计达标）+ 无人机分配表 + 「导出方案」（JSON/PNG）。
- 底部（或抽屉）「模型证据与限制」：数据来源、模型域、覆盖边界（如「覆盖面积按演示阈值」）、待校准参数（k、包剂量、C_req）。

**新增组件清单**（src/components/map/）：LayerChipBar、RiskEllipseLayer、FlowArrowOverlay、WindArrowOverlay、DropCandidateMarkers、UavRouteLayer、TimeSlider、PatchEvidencePanel、GovernancePanel、PlanCompareCards、ConcTargetChart（Recharts）、DoseTimeSurface（自绘 canvas/SVG 热图）、ExecCheckCards、MissionTimeline、UavGantt（自绘，Recharts 无内置 gantt）。

### 5.3 数据分析页（中等改，参照「数据分析页-v2/v4」）

- 顶部筛选行：时间范围 + 设备筛选 + **分析物切换（MC-LR / total MC）**（保留一个下拉，按 V4 删第二个）+ 导出数据。
- 「AI 预测（未来 7 天）」块 → **「当前风险估计（非未来预报）」**：历史曲线+当前中位数点+80% 区间（浅蓝带）+ 置信点；右侧证据卡：当前状态估计（中位数 2.50 / 区间 1.60–3.40 / **超限概率 91%** / 模型域 OOD 关注 / CMADRE v2 · nowcast 徽章 + 「建议现场复测」）。
- 删除：假「模型置信度 87%」、假「下一高风险时间 5 月 29 日」、虚线未来延长段。
- 趋势分析保留三轴（毒素/水温/pH）并补充 DO/浊度/叶绿素可选；风险阈值线保留（1.0 警戒 / 5.0 高风险）。
- 传感器对比 → 「节点读数与质量」：新增每行 质量状态列（异常/待复测/信号弱），数据来自标定 qc 旗标与设备自检。

### 5.4 设备配对页（结构不变，扩展信息）

- 节点详情面板扩展：暗基线（设备自检）、校准状态（已标定/待标定/标定过期）、有效反应时间窗（2–6 h 最优读取窗）、trigger 构型与符号（trigger6+ / trigger2−）、OD600（可选）。
- 新增「执行资源」卡区（与传感器卡片分离）：无人机 A/B 电量/就绪/航线预览；不参与蓝牙/WiFi 配对 CRUD。
- 拖拽排序等现有交互保留。

### 5.5 公共/全局

- AppHeader 地图态胶囊更新：「闭环运行中」状态徽章常显；风场胶囊数据改从场景包/网关取。
- 新增全局 loading/错误兜底：场景包缺失 → 显示「演示场景未加载」占位（不白屏）。
- web/Technical_route.md、AGENTS.md、CLAUDE.md 路由/数据说明同步更新。
- **构建验证**：npm run build 通过（tsc 严格模式），新增依赖为零（已有 leaflet/recharts/dnd-kit 全部够用；如需 gantt/水印等再评估）。

---

## 6. 设计图的不合理之处与修正建议（明确指出）

| # | 设计图/README 内容 | 问题 | 修正建议 |
|---|---|---|---|
| 1 | 态势总览时间滑杆「+30 min / +2 h / +6 h」 | redo_v2 是 nowcast（明确不做未来预报）；滑杆若把「风险面」外推 6 h 即虚假预测；但流场/漂移/降解确实可以用物理模型推演 | 滑杆**只作用于推演层**（水流/覆盖/降解曲线/任务状态），风险面保持「当前状态」，并在滑杆旁注明；或把滑杆命名为「推演时刻」 |
| 2 | 「方案有效期限 15 min」 | 无定义；是由「风窗口/降解窗口/无人机续航」哪个决定不明 | 明确定义为 min(风场窗口余量, 光控存活窗口余量, 无人机可用窗口)，由网关计算并标注公式；否则删除该字段 |
| 3 | 「推荐剂量 12 包」、「方案 A 8 / B 12 / C 16 包」 | 无来源且与「单次覆盖 0.05–0.08 km²」不匹配（E13 物理剂量：C0=2.85/24h/25°C/M=1 时 8 点×6 载荷 = 48 载荷单元，为演示需求 17 的 2.8 倍） | 三档方案由 dose_response 在 [D_min, D_max] 区间取 3 档（如 8/12/16 或按包载换算），达标时间/覆盖率/取舍由模型输出；**不建议硬编码 12 包** |
| 4 | 「单点覆盖 0.05–0.08 km²」 | 是 5% 演示阈值下的值，C_req 联标后变化（5%→20% 面积缩至 1/6.5） | 展示「面积随阈值」区间 + 徽章「原型参数（待 C_req 联标）」 |
| 5 | 右侧「80% 区间 4.80–8.10 μg/L / 超限概率 96%」 | 标定当前能力边界是**多通道融合判别**（LOD 0.28–1.34 μg/L；单点 trigger1/6 z 仅 0.3–0.5），6.35 μg/L 的中等值可以给出但必须声明融合通道与来源 | 证据卡加「来源：3 节点 × 3 重复 × 2 通道融合（原型）」；可信度等级用「数据可信度：中」并注明依据 |
| 6 | 地图底图 | 设计图为真实瓦片地图，现状是 CSS 示意图（无 Leaflet）；OSM 公共瓦片有使用政策、高德/天地图需 Key | 双模式：默认 OSM 瓦片 + 矢量叠加；离线/演示失败回退品牌示意图。若答辩需要，可离线打包本地瓦片（mbtiles→leaflet） |
| 7 | V2 README 中「闭环推演（下滑分析区）」 | 随后 V4/V5 已把「闭环步骤条/闭环链路」从任务页移除（属实现说明），最终推荐 V4/V5 | 以 地图监视页-v2-方案推演-执行检查.png（V5）为唯一实现基准；「闭环链路」可作为总览页「了解系统」浮层或演示开场动画，不进任务操作区 |
| 8 | 总览页重设计.png | 成图中**未体现** README 所写「系统状态增加模型链路 / 告警摘要增加待治理任务」 | 按 README 补两块（§5.1），注意保持成图版式（不新增卡片密度过度） |
| 9 | 图层「预测风险」与「MC-LR 风险」并存 | 易混淆：一个是 nowcast 风险面（蓝紫），一个是节点标定热力（绿黄橙红）；且「total MC」与「MC-LR」不能合并 | 图层名改为「环境风险估计(nowcast)」；色系严格区分；默认只开 MC-LR 相关图层；文案禁止写「total MC 预测」 |
| 10 | 设备页「无人机」 | 设计 README 说无人机作为执行资源而非传感器卡片 | 移到地图任务栏 + 设备页「执行资源」子区；不进入配对 CRUD |
| 11 | 执行前检查「通信链路 4/4 在线」、复测 12:00「已加入任务」 | 目前无通信/复测调度真实数据 | 由 task_plan + 设备状态表提供；演示值标注「演示数据」，或由网关计算 |
| 12 | 「数据可信度：中等 (i)」图标 | 无图例定义 | 定义 高（≥2 独立源一致）/中（1 源+区间宽）/低（OOD 或 flag），并把判断规则写进前端 util，与网关 confidence.level 对齐 |

---

## 7. 分阶段实施路线与验收（建议 4 个 Phase，共 6–8 周）

> 依赖链（严格）：R-1 源码恢复 ∥ D-1 换锚 → W-1 C_req 联标 ∥ C-1 fuse → D-2/D-3 API → P-1/P-2 v3.0 → 网关 静态导出 → Web 地图三状态 → 其余三页 → 端到端复盘。

### Phase 0：契约冻结 + 数据对齐（2–3 天）
- 产出 §2 的 JSON Schema（5 个标准记录 + 信封）+ pipeline-server/docs/contract.md；五模型 README 各加「管线接口」一节（指向 contract 版本号）。
- 验收：每个模型给出一条符合 schema 的样例记录（可用现有脚本生成）；confidence 字段全部有值。

### Phase 1：模型侧 P0 项（2–3 周）
| 周 | 内容 | 验收 |
|---|---|---|
| W1 | R-1 源码恢复+比对；D-1 v1.2 换锚（A1–A7 全部）+ 新参数表 + fig4–6 重生成 | pytest 通过；参数溯源台账齐全；fig 数字与表一致 |
| W2 | W-1 C_req↔thr_rel 联标（产生门限换算表 + 重算覆盖面积区间）；C-1 fuse() + 融合 z 提升报告 | 水流 README「演示值」换为联标值并标注；融合报告给出 z~√N 曲线与有效样本保守估计 |
| W3 | P-2 续航语义修正 + E13 复跑（≥1.9× 加速比）；P-1 v3.0 契约接入 D-2/D-3（含 double-source C0 规则拍板） | E13 契约诊断复现 1.91×；任务库 hash 与上游一致 |

### Phase 2：服务化 + 静态场景包（1 周）
- D-2/D-4（api.py + GBDT 代理）、W-2（SWF 适配器）、C-5（标定适配器）、R-2/R-3（网格导出 + p_env）、P-5（规划适配器）→ pipeline-server 端点在本地跑通；export_demo_scenario.py 产出 pipelineScenario.json + GeoJSON 进 web/。
- 验收：curl /api/v1/overview 与场景包字段一致；场景包在无后端下可驱动全 Web 演示；每个数字可回链到 provenance。

### Phase 3：Web 改造（2 周）
- 5.2 地图三状态（先场景包后网关）→ 5.1 总览 → 5.3 数据页纠偏 → 5.4 设备页扩展 → 5.5 全局。
- 验收：npm run build 0 error；四页截图与设计图逐项对照通过；「原型参数」徽章在所有未标定数字上出现；removed 的「未来 7 天/置信度/下一高风险时间」无残留；地图离线降级可用。

### Phase 4：端到端复盘（1 周）
- e2e_demo 时间线：东湖风况日 → 风险面 → 节点报警（含融合决策）→ 生成方案 → 下发 → 执行（模拟）→ 复测 → 效果复核（预计达标 vs 复测值，闭环指标：区间覆盖率/命中率）。
- 产出：演示视频脚本 + 评审证据包（对照实验：有/无流场推演的点位差异、有/无融合的单点检出差异）——直接支撑 iGEM Engineering/Innovation/Safety 评分点。

---

## 8. 风险、边界与诚实性声明

1. **数据诚实性（必须写进所有展示材料）**：①redo_v2 无东湖毒素标签（训练 99.5% 美/加），其东湖输出属「外域估计候选」；②浓度标定融合基于 33h 湿实验工作簿 + 合成数据先验，且真实数据存在行位混杂/重复非独立；③降解模型 v1.2 换锚后仍属「文献先验 + 情景灵敏度」，工程菌 k 尚未实测；④水流无东湖实测流速对照，水深为形态学重建。→ 页面与答辩口径必须带「当前能力边界」，不允许「我们已经能精准预测东湖」类表述。
2. **明确不做**：未来预测（1/3/7 天）、total MC→MC-LR 固定换算（redo_v2 拒绝的边界）、端到端黑箱一体化模型、真实无人机/硬件通信（演示用模拟执行）、用户认证与数据持久化。
3. **工程风险**：①redo_v2 正式 run dirs 在服务器，若不同步则本地只能 smoke 级输出（已做降级策略）；②tile 合规（OSM 归因/数量，或离线 mbtiles）；③五模型环境各异（conda igem-cyanohab / torch CPU），网关需独立 venv 并锁定版本；④跨模块契约版本漂移——**contract 版本号必须进每个输出信封**，不匹配即断点（回归测试）。
4. **评审对齐**：闭环价值证明需要对照实验——建议 W1 即准备「无流场推演 vs 有推演」、「单点 vs 融合」的对比表（现成数据：覆盖斑块 vs 直接投中心；z 2.0 vs 3σ）。创新点申明与公开文献差异（标定 report/07 §5 已做全网先例调研）。

---

## 附录 A：关键既有文档索引（本方案依据）

| 主题 | 文档 |
|---|---|
| 闭环接口总览 | model_concentration_calibration/report/07_系统级衔接与集成报告.md（§1 五张接口表、§2 四项调整、§4 真实数据审计） |
| 降解适配 | model_MC-LR_degradation_kinetics/report/05_五模型管线协同调研与降解模型适配评估.md（§3.2 三项接口、§5 阶段路线 A1–A7） |
| 路径适配 | model_path_planning/report/06_五模型联动适配性审查与路径规划改进方向.md（§2.1 契约表、§3 失配点 1–6、§5 v3.0） |
| 水流-规划端到端 | model_Two-dimensional_water_flow/report/experiments/E13_pipeline_interface.md（续航语义、physical_thr_rel、dose_i） |
| 水流模型 | model_Two-dimensional_water_flow/MODEL_ARCHITECTURE.md、README.md（演示值声明） |
| 标定模型 | model_concentration_calibration/report/03_模型架构设计报告_终版.md、src/calibrate.py、src/deploy.py |
| 降解模型 | model_MC-LR_degradation_kinetics/report/04_交付物质量审查报告.md（A1–A4、B/C 类）、report/02（§12.1 环境修正校准） |
| redo_v2 | model_redo_v2/report/MODEL_OBJECTIVE_SPEC.md（§6 输出契约、§8 验收门槛）、SERVER_RUN_REPORT.md（锁定测试/run dirs）、model_redo_v2_server_20260810.tar.gz（源码恢复源） |
| 设计 | design-assets/page-objectives-redesign-v2/README.md（V1→V5 演进）及 5 张成图 |
| Web 现状 | web/Technical_route.md、web/src/pages/*、web/src/data/* |

## 附录 B：本方案与既有报告的差异说明

- 报告 07/05/06 定义的是「模块间科学契约」（字段/语义/不确定度），本方案在其上补充 **工程实现层**（pipeline-server、静态场景包、Web 服务层、三状态地图交互、设计图差异修正）与 **实施顺序/验收**，不重写各模型架构。
- 本方案推荐在 Web 联调前先交付「静态场景包」，是因为：五模型各自推理链重（torch/xgboost/ODE），在线联调风险高、演示不稳定；场景包可在不改模型代码的前提下让 Web 提前 2 周并行开工——这是进度与质量的平衡，若团队坚持秒级在线更新，则需把 Phase 2 提前并接受「模型环境+瓦片+网关」三件耦合风险。

---

*文档版本 V1（2026-08-27 初稿）· 适用仓库根目录 IGEM-dry · 下一版本触发条件：Phase 1 P0 项全部验收通过后更新为 V2（含实测参数回填）。*