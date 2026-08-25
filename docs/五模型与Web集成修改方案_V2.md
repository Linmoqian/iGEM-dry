# 五模型 × Web 平台集成修改方案（V2）

> **版本**：V2（2026-08-25，基于全量磁盘盘点）
> **状态**：方案定稿稿
> **与 V1 的关系**：V1（`docs/五模型与Web集成修改方案_V1.md`，落款日期标注 2026-08-27）在 07/05/06 号报告基础上给出了完整的工程化框架（契约、网关、Web 改造、实施顺序），本 V2 在此基础上做了 **2026-08-25 全量磁盘核实**：逐目录核查代码/产物/文档三方一致性（5 个模型 + web + 设计资产，7 路并行调研 + 关键代码实跑验证），修正了 V1 中 4 处与当前磁盘不符的表述，并按设计资产最新演进（README 已到 V5）更新了 Web 改造基准。**V1 的框架结论全部保留，V2 的差异见附录 B。**
>
> **诚实性红线（贯穿全文）**：所有未完成现场标定的数字，在页面上必须带「原型参数」徽章并同时显示区间/超阈概率，**不得显示为确定结论**。这是设计 README 自己的规则，也是 iGEM 评审的底线。

---

## 0. 结论速览（30 秒版）

1. **五模型上下流关系已成立，「契约已定稿、实现未落地」的判断在 08-25 复核后依然成立**，但各模块内部有几处 V1 之后的新进展（详见各节）：
   - 水流模型：B3 水深 / cd_lake / windage 2% / physical_thr_rel / E13 端到端 **均已落地并验证**（比 V1 表假设的更完整）；
   - 路径规划：**V3 模块验证轮（M1–M7）已合入**（commit 218816d），t_service=1.0 / κ=1.15 / E_res=2.0 已为 Instance 默认，多访问完成时刻=第 demand 次已修复；
   - 标定模型：真实 33h 湿实验已接入并完成 8 个 trigger 拟合（trigger5 正响应 z=2.03、trigger2 抑制型 z=−2.59），但 **fuse() 仍为零实现**（全目录 grep 零命中）；
   - 降解模型：**A1–A7 换锚全部未做**，`src/api.py` 五函数未实现——仍是管线最大 P0 依赖；
   - redo_v2：**V1 说"tar.gz 恢复源码"有误**——实为未压缩目录 `model_redo_v2_server_20260810/model_redo_v2/`（含完整 v2 源码快照，35 个 .py），但**最终 I5 冠军代码只存在于 .pyc**、正式 run dirs 全部在服务器，本地仅有 smoke 制品（已验证可端到端推理）。
2. **推荐改造顺序（依赖驱动，不能倒序）**：契约冻结 → 降解 v1.2 换锚（D-1）∥ redo_v2 源码/制品恢复（R-1）→ 水流 C_req↔thr_rel 联标（W-1）∥ 标定 fuse()（C-1）→ 降解 api.py / 代理（D-2/D-3/D-4）→ 路径 v3.0 契约落地（P-1/P-2）→ 管线网关+静态场景包 → Web 四页改造（地图三状态为主）→ 端到端仿真复盘。
3. **Web 侧不做五页五模型**（与设计 README 结论一致）：新增能力全部收敛到「地图监视」页三状态工作台；其余三页轻改。**设计图存在文件命名漂移与若干与模型能力冲突的字段，必须先定版再动手**（详见 §8）。
4. **Web 现状**：无 services 层、无任何 fetch/状态管理/useEffect；地图页是 CSS 手绘示意图（未用 Leaflet）；dnd-kit 装了没用；三个 common 组件（AquaCard/RiskBadge/StatusBadge）零引用；`@theme` 色板 token 形同虚设（全部硬编码）；数据页「AI 预测 7 天 / 置信度 87% / 下一高风险时间」必须移除；三处毒素曲线数据互相矛盾；header 硬编码「在线 9/待机 2/离线 3」与实际 8/3/3 不符。
5. **关键工程决策**：网关采用「A. 静态场景包（默认，演示首选）→ B. 在线推理（联调可选）」双模式；地图用「真实 Leaflet + 离线降级示意图」双模式；所有模型产物（npz/ckpt/csv）被 .gitignore 全局排除——**换机/重克隆后必须重新训练或从其他介质拷贝，方案中已列入风险**。

---

## 1. 项目背景与系统闭环

（背景详见 `docs/Introduction/IGEM项目简介.md`，此处只给五模型定位所需的骨架。）

- **问题**：蓝藻水华 → MC-LR 超标（WHO 红线 1 μg/L）。传统检测慢、贵；传统降解低效。
- **方案**：工程大肠杆菌（START 核糖开关 + LuxI/LuxR 群体感应放大 + sfGFP/TurboRFP 双荧光 + YF1-FixJ 光控自杀）做**检测菌**，漂浮装置组网实时监测；超标预警后**无人机投放降解菌**（mlr 酶基因簇 + Adda 转氨酶），降解至无毒后菌体自杀回收。
- **干实验五模型**承担该闭环中「感知→推演→决策→执行→复核」的数字化部分：

```
|---------------- 物理世界 -----------------|--------- 数字化世界（五模型+Web） ---------|

湿地/水域                       多源环境观测(水质/气候/遥感/历史毒素)
   │                                     │
   ▼                                     ▼
[漂浮检测节点: 荧光信号 y] ──► [① 浓度标定: y→ĉ+CI+P(C≥1)]   ←─ 真值锚点
   │                        │        ▲
   │                        │        │ 空间先验 p_env
   │                        │   [② redo_v2: 环境风险 nowcast]
   │                        │        │
   │                        └──► 风险融合 → 风险斑块（Web 图层）
   │                                     │
   │              [③ 二维浅水流: 流场→漂移→投放点+覆盖面积+漂移时滞]
   │                                     │
   │              [④ 降解动力学: 剂量-时间反演 → C_req/剂量/达标时间/窗口]
   │                                     │
   │              [⑤ 任务级路径规划: 多机分配+访问顺序+滚动重规划]
   │                                     │
   ▼                                     ▼
[无人机投放降解菌] ───────────────► 治理执行 → 节点复测 ──(回环: 标定/redo_v2 再学习)
```

- **统一语义**：全链共用 1 μg/L 阈值、小时/分钟时间单位、JSON+版本+置信度输出契约；三份五模型联动报告（标定 report/07、降解 report/05、路径 report/06）已确认「语义已对齐，缺口在实现与联调」。
- **级联不确定度预算**（按对「达标时间」终局不确定度的贡献排序，降解 report/05 §4.4）：**降解 k（跨文献 3–4 个数量级，最大未知）> C0（标定 LOD 与东湖作业带 0.25–2.85 μg/L 在低端重叠）> 风况（水流 5 成员系综 ±12%）> 到达抖动（分钟级）**。管线契约必须声明「各单位预算」，避免五模块平均用力；湿实验三件套（δ(I) 光死曲线、工程菌 C(t)、mlrA 表达动态）是投入产出比最高的一环。

---

## 2. 现状盘点（2026-08-25 磁盘实测）

### 2.1 各模型现状与缺口清单

| 模型 | 当前版本/状态 | 关键产出（已核实） | 面向管线/Web 的缺口 | 参考文档 |
|---|---|---|---|---|
| **model_redo_v2**（CMADRE） | v2 服务器锁定测试完成（8-10）；**本地无 .py（仅 pyc）**；完整 v2 源码在 `model_redo_v2_server_20260810/model_redo_v2/` 目录（非 tar.gz）；**I5 冠军代码仅存 pyc（8-11 凌晨最终态，与快照有代差）**；正式 run dirs 在服务器，本地仅 13 个 smoke 制品（已验证 E2E 推理） | {q10/median/q90, ood_score/flag, 每专家3列+集成+校准列}；锁定测试：total MC source-OOD log1p MAE **0.3488**；MC-LR core **0.2972**（Spearman 0.5091）；MC-LR static 0.1318（弱） | ①权威制品拉取/重训（I5 冠军）；②东湖网格导出 `export_grid.py`；③`p_env_at()` 未实现；④p_detected/p_exceedance 未输出（risk_thresholds 配置全空）；⑤无 HTTP 服务 | report/MODEL_OBJECTIVE_SPEC.md、FINAL_MODEL_REPORT.md、SERVER_RUN_REPORT.md、迭代记录.md |
| **model_concentration_calibration** | v3.1 完成；真实 33h 数据已接入并完成 trigger 0/1/5/6(+)/2/7(−) 拟合（`real_fit_results.json`） | 11 参数时变 Hill；MAP+Laplace；网格反演 {median/lo5/hi95/p_ge_1}；deploy LUT（trigger5 一套）；正响应 z@1μg/L,6h：t5=2.03/t6=0.26/t0=0.32/t1=0.48；抑制 t2=−2.59；合成 LOD 0.28–1.34 μg/L；**真实数据 3σ LOD：量程外** | ①**fuse() 零实现**（07 §2B 必需接口）；②p_env 是先验常量 ENV=(−1.9,1.2)，非 redo_v2 接口；③输出契约未标准化（无 node_id/t_meas/flags/qc）；④artifacts 仅 trigger5 一套、无 calibration_day/device 参数；⑤evaluate.py 与 synth.py 键名断裂（lobo_cv 读 data['Q'] 而 gen_dataset 返回 'fold'）未修 | report/03 终版、report/07（§2 四项调整、§4 真实数据审计）、src/*.py |
| **model_Two-dimensional_water_flow** | **E14 新基线生产默认已落地**：powB3 水深（42 实测点标定 RMSE 0.49）+ cd_lake + windage 2% + n=0.0238 + Smagorinsky cs=0.29；domain/flow_*/opt_result.npz 均在 | flow SE 0.0680/0.0154（峰值/均值 m/s）、N 0.0806/0.0208、W 0.0434/0.0098；opt_result.npz（792 候选+5 成员系综，thr_kind='demo'）；`physical_thr_rel(C0,t_ok,T,M)` → thr_rel=0.2465（demo 5% 的 4.9 倍）；`scripts/21_pipeline_demo.py` 端到端 | ①覆盖阈值仍是演示 5%→ 与降解 C_req 联标（W-1）；②无服务化/GeoJSON 导出；③坐标换算（米→km→WGS84）工具化未建；④节点坐标仍假设值；⑤文档 MODEL_ARCHITECTURE §6/§7.3/§8.2 仍是 E14 前旧数字；⑥`SweConfigSI` 类默认（const ν=0.5、const Cd）与生产（smag、lake）不一致，裸用会悄悄降级 | MODEL_ARCHITECTURE.md、README、report/实验记录_EXPERIMENTS.md、E11/E13 |
| **model_MC-LR_degradation_kinetics** | v1.1 灰箱原型 + 文献层校准；QA 04 判定「架构可上评审，**数字先换锚**」 | prototype_v1.py（C/L 两态 ODE+环境修正+MC）；fit_literature.py（CTMI/非对称高斯/USGS k）；3 批真实数据（Mendeley k、Lake Erie 0.90 胞内比例/0.278 f_LR、东湖 2009 六点 0.25–2.85 μg/L） | ①**A1–A7 全部未做**（m6 k=0.25 h⁻¹ 是网格伪影、CTMI R²=1.0 是 4 参数拟合 4 点、原型仍是旧对称高斯、k_bg 未分层、C_intra 未默认开启、fig4–6 由 v1.0 函数生成）；②`src/api.py` 五函数（scenario/dose_response/t_safe_quantiles/sink_rate/C_req）未实现；③投放时滞 Heaviside、机会约束、GBDT 代理未做 | report/04 质量审查（A1–A4/B/C）、report/05（§3.2 接口、§5 A5–A7 路线图）、src/prototype_v1.py |
| **model_path_planning** | **V2.7 优化轮 + V3 模块验证轮（M1–M7）已合入**；`env.Instance` 默认 κ=1.15/E_res=2.0（M3）、t_service=1.0（M1）、多访问完成时刻=第 demand 次（M6 修复通过）；东湖 RL-B 推理 0.064 s | env.Instance（13 字段）；flow_tasks.py（v3.0 任务生成器，**真实加载水流 opt_result.npz**）；outA/outB/outC(+C2) ckpt；V3 训练产物（D/E/E2/F）归档于 SWF/…/V3_pathplanning/trainings/；M5：n=50 时 RL+LS 9.1% 优于贪心+LS | ①**P-1 v3.0 契约未真正落地**：flow_tasks.py 中 K_BASE=0.25/F_D0=0.15/PACK_DOSE=1.0/T_LIMIT=360/SEP_M=300/T_DRIFT=60 仍是演示常数，DEG_DIR 死代码；②**P-2 续航计费未做**（T[i,i]=0.13 微小值，E13 契约诊断：同点打包零边际成本导致单机基线偏乐观；修复后预期 1.91× 加速比）；③P-3 S_j 覆盖乘子未实现；④P-4 机会约束/场景采样未做；⑤无 task_plan 服务化输出；⑥train.py 默认 κ=1.0/e-res=0.0 与 Instance 默认 1.15/2.0 不一致（掩码/审计口径分裂）；⑦rollout hover 0.13 vs 评分 hover 1.0 不一致 | report/09（M1–M7）、report/06（失配点 1–6）、report/03（主表）、code/*.py |

### 2.2 Web 现状（web/，Vite+React18+TS+Tailwind v4）

| 项 | 现状 | 与目标差距 |
|---|---|---|
| 技术栈 | Vite 5 + React 18.3 + recharts + leaflet/react-leaflet/leaflet.heat + dnd-kit（**均已安装但后四组零源码引用**）+ lucide-react；纯 SPA | 可沿用；Leaflet 接入无需新增依赖 |
| 路由 | `/`、`/map`、`/data`、`/device` 四页（App.tsx） | 与设计一致（新增能力不引新路由） |
| 数据层 | 全部手工 mock：demoReadings.ts（14 设备 13 字段）、mockPredictions.ts（假 7 天预测）、materials.ts；**demoDeviceHistory/demoSummary 部分函数零引用**；**无 src/services/**；全库 fetch/axios/WS/useEffect/createContext 零命中 | 需从零建服务层（fetch + mock 降级）；设备字段需扩展 DO/浊度/叶绿素/营养盐/校准状态/暗基线等 |
| 地图页 | CSS 手绘湖面示意图 + 硬编码 % 坐标（11 台）；图层按钮/缩放/定位均为死控件；右侧详情面板 420px | 与设计图差距最大，本次主改；Leaflet 已有类型声明（leaflet-heat.d.ts）为将来预留 |
| 数据分析页 | 「AI 预测（未来 7 天）」+「模型置信度 87%」+「下一高风险时间 5月29日」+「预测开始」虚线——**全部硬编码** | 与模型能力（nowcast）直接冲突，必须纠偏 |
| 总览页 | KPI（平均 2.50 硬编码）+系统状态+告警摘要+趋势+最新采样；无交互 | 补「模型链路」+「待治理任务」+最高风险卡跳转 |
| 设备配对页 | 卡片 6 台+配对雷达+「拖拽排序」（**纯文案，dnd-kit 未用**） | 节点详情补校准字段；无人机作执行资源展示 |
| 一致性隐患 | header 硬编码「在线 9/待机 2/离线 3」vs 实际 8/3/3；OverviewTrend/trendData/mockPredictions 三条毒素曲线互相矛盾；risk 色值两套（#059669/#f59e0b/#f97316/#ef1919 vs #22C55E/#F59E0B/#FF7A00/#EF4444） | 统一数据源与色阶（服务层改造顺带收敛） |
| 样式 | `.aqua-panel`、`.glass-button` 等少量自定义 class；`@theme` 的 water-* 色板 token **零引用**，全部硬编码任意值；`min-width: 1180px`；无 public/ 目录（素材走 `new URL('../../materials/...')`） | 地图三状态新增组件沿用现有硬编码色值风格即可，不建议大范围重构 |

### 2.3 设计资产现状（design-assets/page-objectives-redesign-v2/）

- **6 张成图 + README（演进记录到 V5）**：

| 文件 | 内容版本 | 用途 |
|---|---|---|
| `地图监视页-v2-态势总览.png` | 状态 01 态势总览 | 地图页默认监测态基准 |
| `地图监视页-v2-治理规划.png` | 状态 02 治理规划 | 任务规划态基准 |
| `地图监视页-v2-方案推演-执行检查.png` | **即 README 的 V5 内容**（执行前检查四项） | 方案推演态基准（文件名为 v2 前缀，与 README 不一致） |
| `数据分析页-v2.png` | README「当前风险估计」+ 数据页 V4 导航修订（已含单一下拉/导出左移/iGEM Team） | 数据页基准（左下插图仍为水豚+烧瓶，V4 所述显微镜插图未落盘） |
| `总览页重设计.png` | 旧版（V2 仅 3 项轻改，无新图） | 总览页基准 + 左上角「吉祥物操作显微镜」插图来源 |
| `设备配对页重设计.png` | 旧版（V2 不改结构） | 设备页基准 + 绿色显微镜插图来源 |

- **README 声称存在但在磁盘上不存在**：`地图监视页-v2-闭环推演.png`、`数据分析页-v2-当前风险估计.png`（实际名 `数据分析页-v2.png`）、`数据分析页-v3-当前风险估计.png`、`地图监视页-v3-闭环推演.png`、`地图监视页-v4-方案推演.png`、`地图监视页-v5-方案推演-执行检查.png`、`数据分析页-v4-导航与插图修订.png`。
- **结论**：README 是唯一演进记录，但**文件名已两套并存**；Web 改造前必须先定版（推荐：以 6 张实际存在的图为唯一实现基准，README 的演进结论（V4 删闭环链路、V5 换执行前检查、数据页 V4 导航修订）以「已吸收进上述文件」处理，README 需同步修正文件清单——见 §8 第 1 条）。

### 2.4 湿实验分析结论对模型的硬约束（docs/Introduction 各报告）

| 结论（报告出处） | 对模型/接口的含义 |
|---|---|
| 响应以早期窗口为主（RFP 内参报告：峰值 2h，trigger1 Δ=0.2147；0-6h 报告：编号 1/5/4 为 0-6h AUC 前三；tig4567：2h 峰、幅度 0.14–0.21） | 标定模型**有效读取窗 = 2–6 h**（设备页展示「有效反应时间窗」）；路径/任务时间轴以小时计 |
| trigger 优选结论不一（RFP 报告主推 trigger1/0；0-6h 报告主推编号 1；标定 07 逐时间 fold 复算主推 trigger5（正）与 trigger2（抑制），并指出 trigger1 的 24h 强响应主要是 DoubleNorm 的 0h 行位因子） | **统一采用 per-time fold（Q/Q0 同时间 0 μg/L 对照）作训练口径**；DoubleNorm 只作诊断量；报告口径不一致处需在模型 README 记录（数据诚实性） |
| RFP 内参 CV 中位 3.21%（docs 报告）vs loader 实测 3.3–6.6%（trigger 3–8） | 以 loader 实测为准；置信预算按 5–7% 噪声设计 |
| 均为 3 技术重复、无独立生物重复；A 行（0 μg/L）存在孔位异常；缺 OD600 | **最低数据契约**：板位随机化 + OD600 + ≥3 批生物学重复 + 每板空白/哨兵；否则标定结论只能算「方法验证」 |
| 建议 signal/OD600 与 Δ(signal/OD600) 为主指标（tig4567 §6） | 与标定模型口径一致；设备字段需含 OD600 或菌量近似（未来硬件/QF 通道） |
| pmcy/pmlrA/tig0123 数据质量低（方向不利/缺 0h/仅 0.5h） | 仅早期定性证据，不得作定量候选进入标定训练主体 |

---

## 3. 统一数据契约（先冻结，再动手改代码）

> 这是整个改造的第一件事：**冻结 JSON Schema 五件套（schema_version / model_version / units / confidence / provenance）**，五个模型与 Web 只消费标准记录；任何演示数字必须带 provenance:「prototype」或真实来源。

### 3.1 信封（所有管线输出共用）

```json
{
  "schema_version": "1.0",
  "model_version": "cmadre_v2 | calib_v3.1 | swf_v1.2 | degr_v1.3 | pp_v3.0",
  "data_version": "hash or run-id",
  "units": {"concentration": "ug/L", "length": "m", "time": "min"},
  "confidence": {"level": "prototype|calibrated|site-validated", "note": "…"},
  "generated_at": "2026-08-25T09:42:00+08:00",
  "provenance": {"source": "…", "run_dir": "…"}
}
```

### 3.2 五个标准记录（各模型生产者 → 统一消费者）

**① calibration_record（标定 → 流场/降解/路径/Web）**
```json
{"node_id":"aq-006","lat":30.5699,"lng":114.3864,"trigger_id":"trigger5","sign":"+",
 "t_meas":"2026-08-25T09:40:00+08:00","fold":1.31,
 "c":{"median":6.35,"lo5":4.80,"hi95":8.10},"p_ge_1":0.96,
 "flags":["low_snr"],"qc":{"rfp_cv":0.056,"n_reps":3,"biorep":1},
 "env_prior":{"kind":"grid|zonal|lognormal","params":{}}}
```

**② risk_field（redo_v2 → 标定 p_env / 流场热点 / Web 图层）**
```json
{"target_kind":"mc_lr","extent":[[30.52,114.33],[30.62,114.44]],
 "grid":{"nx":200,"ny":200,"cells":["median","q10","q90","p_exceedance","ood_score"]},
 "sources":["node-calibrated 6.12","cmadre-nowcast 6.58"],
 "horizon":"nowcast","model_version":"cmadre_v2","data_version":"…"}
```

**③ flow_result（水流 → 降解/路径/Web）**
```json
{"wind":{"speed_ms":2.5,"dir":"SE"},"scenario":"SE_2p5","members":5,
 "drop_points":[{"id":"D1","x_m":-1531,"y_m":-535,"lat":30.5518,"lng":114.3796,
   "score":0.0533,"a_drop_km2":0.065,"drift_theta_deg":15}],
 "patch_mask":"geojson-url",
 "coverage_thr":{"kind":"c_req","value":0.2465,"note":"C_req联标后替换演示5%"}}
```

**④ degradation_decision（降解 → 水流/路径/Web）**
```json
{"C0_ugL":{"median":2.85,"lo5":1.0,"hi95":6.0},"dose_per_pack_ugL":0.9,
 "scheme":{"packages":12,"D_eff":6.0},"t_safe_h":{"median":5.6,"p90":8.1},
 "window":{"light_survival_h":24,"second_drop_needed":true,"second_drop_after_h":24},
 "infeasible":false,
 "decision_conf":{"level":"prototype","note":"k_bg/工程菌k未锚定，剂量为原型参数"}}
```

**⑤ task_plan（路径 → 执行/Web）**
```json
{"mission_id":"TS-0825-03","assets":[{"id":"A","type":"uav","cap_packs":4,"battery_pct":87}],
 "routes":[{"uav":"A","legs":["depot-north","D1","D2","depot-north"],"packs":[6,6],"eta_min":8.4}],
 "timeline":[{"t":"09:45","event":"publish"},{"t":"09:53","event":"arrive","uav":"A"}],
 "gantt":[{"uav":"A","kind":"flight","start_min":0,"end_min":20}],
 "metrics":{"risk_weighted_eff_time_min":16.6,"coverage_km2":0.9,"unserved":0}}
```

### 3.3 时序与坐标系约定（红线）

- **时刻语义**：`t_meas`（采样时刻，标定时间轴）≤ `t_publish`（任务发布）= t_meas + 决策延迟；`t_arrive`（路径规划）；`t_eff = t_arrive + T_drift + t_safe`（治理生效，全链统一目标）。路径重规划事件与标定测量时刻必须在同一时间轴上；**「预计达标」的起算口径必须在界面显式标注**（设计图 15:30 = 首架到达 09:53 + 5.6h，若从发布起算应标注差异）。
- **坐标**：水流模型为**米**（原点 114.3956E/30.5566N，等距圆柱 MLON=95,847 m/°、MLAT=111,320 m/°）；路径规划用 **km**（LAKE_CENTER 30.5667/114.3833）；Web 用 **WGS84**。必须提供官方换算工具 `pipeline_server/utils/geo.py`，禁止各模块私自从常数推导。
- **不确定度**：上游只传「紧凑分布」（中位数+分位数+概率），不用原始 MCMC 样本横穿 5 个模型；Web 端不做二次积分。

---

## 4. 模型侧修改方案（按模型，含优先级）

> P0 = 阻断项（不先做后面全是错的）；P1 = 联调/服务化必需；P2 = 体验/长期。

### 4.1 model_redo_v2（CMADRE）—— 风险估计上游

| ID | 改动 | 优先级 | 说明与验收 |
|---|---|---|---|
| R-1 | **源码与制品恢复**：把 `model_redo_v2_server_20260810/model_redo_v2/` 的 src/configs/run_train/run_validate/pyproject/tests 并入 `model_redo_v2/`（先 SHA-256 比对确认与服务器一致）；**注意快照是 8-10 的 v2 状态，最终 I5 冠军代码（distributional stacking、xgb_quantile_tail、σ 有界、log-blend）只在本地 .pyc**——需①从服务器再拷正式源码（若仍在 `/home/linux/igem-cmadre`）或②以 pyc 为基准用 decompyle3/pycdc 反编译辅助重实现，或③接受「用 v2 源码 + smoke 制品」作接口级演示、在报告中注明「正式冠军代码未恢复」 | **P0** | 恢复后 `pytest` 通过；`cmadre predict` 在 smoke_full_ensemble 上端到端复跑成功（已验证可行） |
| R-2 | **正式 run dirs 拉取**：`runs/total_mc_source_ood_v2/`、`mc_lr_core_waterbody_ood_v2/`、`mc_lr_static_source_ood_v2/` + I0–I5 迭代 run dirs（`runs/mc_lr_bloom_augmented_v2/`、`mc_lr_bloom_distributional_i2/`、`runs/cv_summaries/mclr_bloom_logblend_i5_cv1/` 等）+ 冠军配置 `mc_lr_bloom_v5_log_blend.json` 等 3 个 config——从服务器拉取后本地归档（.tar 不进 git，见 §10） | **P0** | 本地可直接加载冠军 run 推理；若服务器已清理则凭恢复的最终源码重训（锁定设置：seed 42、默认切分、CQR alpha=0.2） |
| R-3 | **东湖网格风险场导出器** `src/cmadre/export_grid.py`：给定经纬度边界+分辨率（建议 200×200）→ 批量推理 → 输出 GeoJSON（web 图层）+ npz（下游仿真）+ LRU 缓存；对每个网格点用 core_field + 季节/流域先验 + 缺省指示组装特征 | P1 | 输出 risk_field 记录（3.2②）；**明确 nowcast 不外推**；网格推理加缓存 |
| R-4 | **p_env 接口**：`p_env_at(lat, lng, t)` → {median, q10, q90, ood}，供标定 `invert_posterior(c_prior=…)` 替换静态对数正态 | P1 | 未就绪时用分区先验（湖湾/开阔水域/入湖口）兜底，页面标注「分区先验」 |
| R-5 | **输出契约补齐**：p_detected（Hurdle 头已实现接口，进入正式 v2 或标记未启用）、p_exceedance（risk_thresholds 配 `[1.0]` 启用）；信封字段（model_version/data_version/prediction_time/horizon=nowcast） | P1 | 输出与 3.2② 一致；失败时 confidence.level=「prototype」且字段 null，不许静默降级 |
| R-6 | 服务化适配器 `pipeline_server/adapters/cmadre.py`（加载 run dir，批量推理 + 进程内缓存） | P1 | 见 §5 |

**注意**：redo_v2 的能力定位是「统计上诚实的 nowcast 研究基线」（total MC 上简单 RF 仍优于 v2 点预测、MC-LR 上 v2≈Dummy 中位数但排序/区间有增量）。**Web 上任何「未来滑杆/预测 7 天」的表层都不可以挂到它头上**；模型卡必须显示 OOD 徽章与区间宽度语义。

### 4.2 model_concentration_calibration —— 感知层/真值锚点

| ID | 改动 | 优先级 | 说明与验收 |
|---|---|---|---|
| C-1 | **实现 fuse()**（新 `src/fuse.py`）：fuse(posterior_list) 把多节点×重复×时间×触发通道的对数浓度后验相乘再归一化（负响应通道取 |Δ| 作独立证据；同一装置多次读数按有效独立样本数保守加权） | **P0** | 真实数据 z 分数：trigger5 单点 2.03、trigger1/6 仅 0.26–0.48、抑制 trigger2 −2.59——**单点单通道无法 3σ 检出 1 μg/L，融合是必需接口而非增强**。验收：N 节点×3 重复×3 时点 z 提升曲线（√N 趋势）+ 有效独立样本保守估计 |
| C-2 | **p_env 升级**：invert_posterior(..., c_prior=grid_prior) 内部先查 redo_v2 `p_env_at()`（R-4），未命中→分区先验→再退静态对数正态；输出记录含 env_prior.kind | P1 | 消除「平台区后验扑向高浓度」病灶；相邻节点同读数不同后验 |
| C-3 | **输出契约标准化**：build_calibration_record(...) 输出 3.2① 全部字段（node_id/trigger_id/t_meas/fold/ĉ/ci/p_ge_1/flags/qc/model_version）；t_meas 必须为采样时刻；flags 枚举 {low_snr, ambiguous, out_of_range, wide_ci}；qc 含 rfp_cv/n_reps/biorep | P1 | 下游只消费契约字段；路径重规划事件与 t_meas 同轴 |
| C-4 | **抑制通道纳入**（部署组合=阳性通道+阴性对照联合诊断）：trigger2/7/3 为抑制型（Amax −0.268/−0.373/−0.326；trigger2 在 1 μg/L z=−2.59 全表最强） | P1 | 抑制通道异常=体系/基质问题，与阳性通道联合提高特异度；成本为零（不改生物构造） |
| C-5 | **修复 evaluate.py/synth.py 键名断裂**（lobo_cv 读 data['Q'] vs gen_dataset 返回 'fold'，KeyError） | P1 | LOBO 交叉验证可跑通；05 报告 P0-3 遗留 |
| C-6 | **Web/网关适配器** pipeline_server/adapters/calibration.py：加载 deploy artifact（LUT JSON）+ 设备仿射参数（a/b/暗基线）→ 节点读数转 calibration_record；**补全 artifact**：calibration_day（LOD/LOQ 写入）、device 仿射参数；时间维最近节点插值（线性插值列后续项） | P1 | 与 device.py 仿射+暗基线扣除一致；**注意当前 artifact 仅 trigger5 一套、calibration_day=None 的现状** |
| C-7 | 装置协议补充：每周期暗电流基线、RFP 单色标样、荧光珠哨兵；行位随机化+独立生物重复+OD600（湿实验侧联动，07 §4.4 最高优先） | P2 | 板位混杂会污染 fold（现 0h RFP 随浓度行单调 +27.7%），属「湿实验→模型」接口要求 |
| C-8 | 不确定性改进：HMC/NUTS、AR(1)/well 随机效应、Student-t 似然（当前区间覆盖率 54–65%，低于名义 90%） | P2 | 长期 |

### 4.3 model_Two-dimensional_water_flow —— 推演层

| ID | 改动 | 优先级 | 说明与验收 |
|---|---|---|---|
| W-1 | **C_req↔thr_rel 联标**：用降解层 `C_req(C0, env, D_max)` 输出替换 physical_thr_rel 的 v1.1 锚（`_K_T_ANCHOR`/K_REF=0.25 锚到 m6 伪影）；输出「东湖场景群的门限换算表」；覆盖面积随 thr_rel 重新计算（E11 已备好 `18_thr_rel_calibration.py` 3×3×2 网格） | **P0** | 联标前，README/E13 所有覆盖面积数字只能作「演示值」。验收：thr_rel 从 0.05 → 联标值（现 physical 口径 0.2465，随 v1.2 换锚变化），单次覆盖面积给出新区间（演示 0.038–0.080 km² 在 0.2465 下坍缩至 ~0.001–0.01 km²，E4 报告 6–60×） |
| W-2 | **服务化查询器** pipeline_server/adapters/swf.py：加载 data/processed/{domain,flow_*,opt_result}.npz → flow_snapshot(scenario, hour)（u,v,η 稀疏箭头，每 500 m 一支）、drop_candidates()（Top-K+score+member_scores）、bloom_patch_geojson()、coverage_ellipse(point_idx, thr_rel) | P1 | 全部转 WGS84 GeoJSON；**禁止在线求解 SWE**（24h 自旋 168–306 s/场景），服务启动时加载一次（<2 s） |
| W-3 | **漂移-衰减修正接口**：drift_forecast(node_pos, t_meas, wind_scenario, horizon_h) → 菌团轨迹/质心/椭圆 + T_drift（供标定读取窗 2–6h 与路径 eff_lag；`sim_drop(record=True)` 已具备雏形） | P1 | 与「最优点=斑块中心偏上风侧，预补偿自动实现」一致 |
| W-4 | **节点坐标真实化**：检测节点坐标改由标定/设备注册表提供；投放点-检测点联合布点（流场+路径联合优化，07 §7 第 5 项） | P2 | 使「水流最优投放点能否覆盖真实报警斑块」可被验证 |
| W-5 | **数字版本统一**：以 E14 基线为准重签 MODEL_ARCHITECTURE §6（SE 0.0680/0.0154、N 0.0806/0.0208、W 0.0434/0.0098）、§7.3（2h 覆盖 0.065 km²、质心 (−385,1852)）、§8.2（top1 (−1531,−535) 0.0533）、§13（cd_lake 高风 clip 3.6e-3 局限）、IntroductionMD §8、TEACHING_GUIDE 修订说明；README 目录行删「01…06」错误条目；补 fig05 Manning 占位 | P1 | 文档与磁盘数字逐一对应（诚实性红线） |
| W-6 | **默认参数陷阱修复**：SweConfigSI 类默认（const ν=0.5、const Cd=1.3e-3）与生产（smag cs=0.29、cd_mode='lake'）不一致，裸用即静默降级（05/08/10/16 已中招）——类默认改为生产口径，或文档显著标注 | P1 | 裸 SweConfigSI() 复现生产结果 |
| W-7 | 风场景系综升级：E12 建议 P75 成员（SE_p75 0.1069/N_p75 0.1497）换入 04/E13 系综；8 扇区×（p50/p75/p90）场景库 | P2 | 覆盖结果区间更真实 |
| W-8 | 实测流速/水位序列（武丰闸/新沟/东湖水文站）获取——仲裁量级之争的第一优先数据 | P2 | 长期；无此数据前所有流场验证止于「解析+守恒+收敛+量级」 |

### 4.4 model_MC-LR_degradation_kinetics —— 剂量层（**先换锚，再服务化**）

| ID | 改动 | 优先级 | 说明与验收 |
|---|---|---|---|
| D-1 | **v1.2 换锚包（A1–A7）**：①m6 k=0.25 h⁻¹ 是网格伪影（C0/4 恰整除），速率先验重锚为 CQ5 0.01537 / Ho2012 8×10⁻⁴–1.3×10⁻² / Lake Erie 8.8–10 d⁻¹ / USGS 12 株中位 ≈0.057 d⁻¹ / Mendeley 分层（<0.22μm 0.17–0.64、<0.45μm 0.22–≥0.77 d⁻¹，删失用区间似然）；②CTMI R²=1.0 是 4 参数拟合 4 点，函数型式降级为「形状假设」；③prototype_v2.py：CTMI f_T + 非对称高斯 f_pH + E(t) + 事件检测，重生成 fig4–fig6；④USGS 只提取 6/12 株，补全并转「上限型/区间先验」（天然微宇宙 8 天清除率中位 ~50%）；⑤C_intra 默认开启（Lake Erie 胞内中位 0.90，f_intra IQR 0.78–0.95），输出「溶解态达标/胞内释放情景」双场景；⑥f_LR 站点先验（Lake Erie 0.278，东湖待测，不进机理内核）；⑦东湖 2009 C0 场景库（0.25–2.85 μg/L 六点）+ 标定 LOD 约束说明 | **P0** | QA 04 判定「数字先换锚」；**管线联调必须在换锚之后**，否则伪影固化进管道。验收：参数溯源台账（每先验→文献原文行号+采样窗口）；fig4–6 数字与报告口径一致 |
| D-2 | **实现 src/api.py（v1.3 服务化，纯函数+JSON 契约）**：scenario()（标定/redo_v2 双来源合并 → C0~N(μ0,σ0²)+来源旗标+ood 门槛）、dose_response(C0, env, T_limit, alpha) → {D*, dosage_ugL, packages}、t_safe_quantiles(C0, D, env) → {median, p90}、sink_rate() → r、C_req() → 最小有效菌密度 | P1 | 供水流（W-1 联标）、路径（P-1）、Web（剂量卡）。双来源合并规则：**触发用 redo_v2 p_exceedance、剂量计算用标定 ĉ**（标定缺失/ood 超限时以预测为情景、实测为校准；<0.5 μg/L 以实测为主） |
| D-3 | **投放时滞输入**：B0(t)=B0·H(t−T_arrive)（Heaviside 延迟投放），T_arrive 抖动并入机会约束 P(t_safe+T_arrive≤T_limit)≥1−α；与路径 t_eff 互洽 | P1 | 「到达≠生效」的模型侧钉死 |
| D-4 | **GBDT/GP 仿真代理**：5×10⁴ 机理仿真→代理模型→秒级剂量查询（供路径迭代与 Web「改包数立即看达标时间」交互） | P1 | 验收：代理误差相对全 MC ≤5%/≤10% 分位 |
| D-5 | **部署 contract/degradation.schema.json + degradation_decision 生产者**（3.2④）；infeasible 显式输出（白色区域/超时限不可达）与「升级处置建议」 | P1 | 不可行时禁止 Web 用「加包」暗示可解（设计图「用量增加 33%」仅对 A/B/C 可比时成立） |
| D-6 | 参数纳入：真实 Km≈350 μg/L、Hill 1.56–2.53（Yang 2024）、多毒素竞争；δ(I) 光死曲线待湿实验 | P2 | 长期 |

### 4.5 model_path_planning —— 执行层

| ID | 改动 | 优先级 | 说明与验收 |
|---|---|---|---|
| P-1 | **v3.0 契约正式落地**：flow_tasks.py 演示常数全部改为调用 D-2/D-3 真实接口与 W-1 结果（K_BASE=0.25、F_D0=0.15、PACK_DOSE=1.0、T_LIMIT=360、SEP_M=300、T_DRIFT=60、D_MAX=6、C_REQ=1.0 逐个删除；DEG_DIR 死代码复活或删除）；任务改为斑块级两层（斑块级→Top-K 投放点级）；06 契约字段（p_ge_1ugL/patch_id/drop_points.centroid/confidence）补齐 | **P0** | 验收：任务库的 demand/tw_end/eff_lag 与降解+水流输出一一对应（hash 比对） |
| P-2 | **续航语义修正**：T[i,i] 同点重复载荷按「现场操作时间」计费（现 0.13 微小值+1.0 min hover 部分缓解，replan 显式置 0.0 必须改）；E13 契约诊断复跑：修复后预期 3 机 60.9 vs 单机 116.4（**1.91×**；不修则 0.62× 负收益） | **P0** | 同步修改 env.py/replan_demo.py 与 E13 docstring；验收：E13 复跑 1.91× 且能量审计 100% 通过 |
| P-3 | **目标函数 v3.0 补全**：Σ w_j·S_j·t_eff_j（**S_j 覆盖质量乘子未实现**）；软窗=降解 t_safe 分位+迟到惩罚 λ 与「加剂量边际成本」耦合；多访问完成时刻=第 demand 次（已修复 ✓） | P1 | 保留统一评分器回放审计；--use-edge --tanh-prior --mode flow 重训 outC′ |
| P-4 | **机会约束/场景采样**：任务属性带紧凑分布（风况成员×降解分位数），POMO S=32 场景采样，输出 P(t_eff≤T_limit) 与置信等级 | P1 | 不加「再传播一层 MC」（与 06 §4.3 一致） |
| P-5 | **服务化适配器** pipeline_server/adapters/planner.py：载入 outB′/outC′ ckpt（CPU <5 ms）→ plan(mission) → task_plan（3.2⑤）；失败回退贪心+LS（<0.1 s）并标注算法回退 | P1 | 供 Web「治理规划」与「执行时间轴」；ckpt 不入库（.gitignore），需本地产物或训练脚本 |
| P-6 | **口径修复**：train.py `--kappa 1.0 --e-res 0.0` 改为默认 1.15/2.0（与 Instance 一致，当前掩码/审计分裂）；rollout HOVER=0.13 改为 inst.hover_time=1.0（当前训练模拟与训练目标不一致） | P1 | 修复后重训 outB′ 并复核 16 场景 |
| P-7 | 动态重规划事件流：replan_event(t, new_alerts) → 增量任务库+新路线（M6 highprio 已支持；结论场景依赖，展示注明演示） | P2 | 与「复测排程/新警报注入」联动的 Web 演示条目 |
| P-8 | 文档同步：README/IntroductionMD 的 V2.7 数字（15.34/16.27/0.06s）→ 补 t_service=1.0 口径注记；「20/22 篇文献」口径统一；outD 路径指向归档目录 | P1 | 诚实性红线 |

---

## 5. 管线网关 pipeline-server（模型 → Web 的桥）

### 5.1 形态与位置

- 新增仓库根目录 `pipeline-server/`（Python 3.11，FastAPI + uvicorn，pydantic v2 schema 校验），**不做数据库**（演示期 JSON 产物+内存缓存；如需历史落盘用 SQLite）。
- 依赖五模型目录（model_*）在本仓库的相对路径；通过 `adapters/` 单文件封装每个模型（只 import 各模型 src/，不改模型源码语义）：
  - `adapters/cmadre.py`（R-6）、`adapters/calibration.py`（C-6）、`adapters/swf.py`（W-2）、`adapters/degradation.py`（D-5 生产者）、`adapters/planner.py`（P-5）；
  - `utils/geo.py`（**官方坐标换算工具：SWF 米 ↔ PP km ↔ WGS84**，契约红线）、`utils/schema.py`（信封校验，版本不匹配即断点）。
- 命令：`uvicorn pipeline_server.main:app --port 8010`；Web 侧 Vite 代理 `/api → http://127.0.0.1:8010`。
- **环境隔离**：五模型环境各异（conda igem-cyanohab / torch CPU / xgboost），网关需独立 venv 并锁定版本（`pipeline-server/requirements.txt` 与 `model_redo_v2/pyproject.toml` 的依赖范围需协调）。

### 5.2 端点（初版）

| 端点 | 用途 | 主要响应 |
|---|---|---|
| GET /api/v1/health、GET /api/v1/models/status | 五模型可用性/版本/置信等级 | 模型状态卡片（总览页「模型链路」） |
| GET /api/v1/overview | 总览页聚合 | KPI、最新读数、告警、待治理任务、模型链路 |
| GET /api/v1/risk/field?target=mc_lr | 风险面（redo_v2 nowcast + 节点标定融合） | risk_field GeoJSON（地图图层） |
| GET /api/v1/nodes/{id}/calibration | 节点证据卡 | calibration_record |
| GET /api/v1/flow/snapshot?scenario=SE_2p5&h=1 | 水流/风场箭头 | GeoJSON 线集+稀疏向量 |
| GET /api/v1/governance/draft?patch_id=… | 生成治理方案 | 投放点+覆盖椭圆+剂量+窗口+任务库（**核心复合端点**） |
| POST /api/v1/plan/generate | 立即生成路径计划 | task_plan（routes/gantt/timeline） |
| POST /api/v1/plan/{id}/replan | 注入事件重规划 | 增量计划 |
| POST /api/v1/scenario/replay | 演示回放（一个东湖风况日时间线） | 事件流（供 Web 时间轴滑块） |
| GET /api/v1/degradation/decide?C0=…&env=… | 剂量决策卡 | degradation_decision |

### 5.3 双模式（关键工程决策）

| 模式 | 适用 | 做法 |
|---|---|---|
| **A. 静态场景导出（默认，演示/答辩首选）** | Web 无后端、断网演示 | `pipeline-server/scripts/export_demo_scenario.py` 预生成「东湖高风况日」完整 JSON 包（24h 风险面/流场/一次治理方案/任务甘特/复测）→ `web/src/data/pipelineScenario.json` + `web/src/assets/pipeline/`（GeoJSON）。Web 服务层优先读它 |
| **B. 在线推理（联调/真机可选）** | 展开复盘、增量更新 | 同上端点实时计算；模型未就绪字段返回 confidence=「prototype」与 null，**前端必须渲染占位徽章而非报错** |

**建议节奏**：先做 A（独立于模型服务化），保证 iGEM 演示稳定；A 稳住后再接 B。

### 5.4 场景包内容（export_demo_scenario.py 产出字段）

scenario（风/时间基线）、nodes（12 个模拟节点+真实检测参数）、risk_field、risk_patches（2–3 个椭圆斑块，含来源/区间/OOD）、governance_draft（4 投放点+覆盖椭圆+12 包+达标区间）、task_plan（3 机路线+甘特+时间轴）、degradation_curve（中位+90% vs 1 μg/L 线）、dose_decision_surface（低分辨率剂量×时间热图）、exec_check（无人机电量/天气窗 2.6 m/s 适宜/通信 4/4 在线/复测 12:00 已排程）、replay_events（发布→首架到达→投放完成→复测→预计达标→复检关闭）。

---

## 6. Web 平台修改方案

### 6.0 总原则

1. **不改四页路由与主导航**；不新增「模型页」；新增能力进地图页（遵循设计 README）。
2. **新增服务层**：`src/services/pipelineApi.ts`（优先读场景包 → 可选 fetch 网关 → 最终 mock 兜底，三级降级）；`src/types/pipeline.ts`（对准 §3 契约）；`src/utils/`（风险色阶/区间格式化/时间轴工具——**色阶收敛为一套**，现两套并存）；`src/data/mockScenario.ts`（阶段一占位，字段与场景包一致）。
3. **文案规则**（设计 README §关键文案规则，必须全站执行）：风险估计/当前状态估计，不用「未来 7 天预测」；浓度必须带区间；1 μg/L 决策必须带 P(C≥1)；OOD 显示「模型域：域内/域外」；未标定数字带「原型参数」徽章。
4. **设备字段扩展**：demoReadings 增加 do、turbidity、chlorophyll_a、tn、tp、calib_state、dark_baseline、react_window_h、trigger_id、flags（同时服务 redo_v2 特征与标定证据卡）。
5. **数据一致性收敛**：header 统计、总览趋势、数据分析趋势、场景包四者统一从单一数据源（pipelineScenario.json 或服务层）派生；删除 mockPredictions.ts 的「未来段」。

### 6.1 总览页（轻改）

- 「系统状态」卡内新增**「模型链路」**横条：5 个模型节点（风险估计→浓度标定→水流推演→剂量决策→路径执行），每节点显示状态点（就绪/演示/未接）+版本徽章（CMADRE v2 · nowcast、标定 v3.1 · 原型参数…）；点击跳地图对应图层。
- 「告警摘要」新增**「待治理任务」**（≥1 时橙色按钮）→ 跳 `/map?state=governance&mission=TS-…`。
- 最高风险卡（6.35）可点击 → 跳地图定位斑块；卡片显示「P(C≥1) 96%（原型）」小字。
- 趋势概览改为「近 7 天均值（节点融合）」，只到当前时间，不画虚线延长。
- 修复 KPI 硬编码（平均 2.50 → 服务层计算）；header「在线 9/2/3」改为动态。

### 6.2 地图监视页（主改 —— 三状态工作台）

**布局**：外壳沿用 aqua-panel + 顶部页头（胶囊文案统一为「闭环运行中」）；左侧地图区（flex-1）+ 右侧 420px 信息栏；页内状态切换（态势总览/治理规划/方案推演）为顶部胶囊，**同路由 /map，状态存 useSearchParams**。

**状态 A：态势总览**
- 地图：**真实 Leaflet**（react-leaflet + OSM 瓦片，demoLake.bounds `[30.52,114.33]→[30.62,114.44]`，比例尺/缩放/归因）；叠加层与图层胶囊一一对应：MC-LR 风险（节点标定融合，绿黄橙红连续热力，默认开）、环境风险估计（CMADRE v2 nowcast，蓝紫等值面+虚线边缘，默认关——**图层名避开「预测」**）、设备（状态色定位针，默认开）、水流场（青色稀疏流线/箭头附 m/s，默认开）、风场（深蓝稀疏箭头附 m/s，关）、投放覆盖（青绿半透明椭圆，关）、不确定度（区间宽度半透明，关）。
- 风险面渲染：**推荐 GeoJSON 等值面**（要表达区间/OOD 语义），热力（leaflet.heat）作为可选切换，防止「热力图=预测」误解。
- 右侧斑块证据卡：名称（EL-R03）/风险等级/MC-LR 中位数+ **80% 区间**/超限概率 **P(C≥1 μg/L)**（全称）/数据可信度（高≥2 独立源一致 / 中 1 源+区间宽 / 低 OOD 或 flag，规则写进前端 util，与网关 confidence.level 对齐）/证据来源（检测节点标定 6.12 vs 环境风险估计 6.58 两条）/现场条件（水温/pH/流速 0.015 m/s/主流向）/OOD 关注徽章。
- 时间滑杆（当前/+30 min/+2 h/+6 h）：**只允许推演「物理层」**（流场漂移/降解曲线/任务状态），风险面保持 nowcast——滑杆旁固定注明「风险面为当前状态，不随时间滑杆外推」（**设计图该处需修正，见 §8**）。
- 主按钮「生成治理方案」→ 状态 B；次按钮「查看节点证据」。
- **降级模式**：`?mock=1` 或瓦片加载失败时回退现有 CSS 示意图 + 矢量叠加（数据驱动渲染不变，只换底图）。

**状态 B：治理规划**
- 主视图切「投放覆盖 + 无人机路线」：候选投放点 D1–D4（绿色编号圆标）+ 覆盖椭圆（半透明青绿，随 thr_rel(C_req) 变化）+ 无人机路线（A 蓝实线 / B 紫虚线，**以事实上的 2 架为准，见 §8 第 7 条**）+ 风险斑块轮廓保留。
- 右侧「治理任务方案 TS-0825-03」卡：目标斑块/投放点 4 个/**推荐包数（带「原型参数」徽章）**/单点覆盖（带「原型参数」）/**方案有效期（需由网关定义，见 §8 第 2 条）**/治理预期（预计达标 5.6 h+90% 区间 4.2–8.1 h、目标 <1 μg/L、是否需要二次投放）/无人机任务摘要（航线/投放量/首达时间）/总航程/任务完成时间。
- 主操作「确认并下发任务」（写入时间轴）+「重新计算」（调 POST /api/v1/plan/generate，无后端时场景包+重采样）+「返回推演」。
- 底部图例条：推荐投放点/有效覆盖/无人机 A/无人机 B。

**状态 C：方案推演-执行检查（以 V5 内容为基准）**
- 中央 4 块：**候选方案对比**（A 8 包/B 12 包【推荐】/C 16 包：预计达标 7.8/5.6/4.1 h、覆盖率 84/92/95%、取舍文案「补救风险较高/综合平衡最优/用量增加 33%」——**取舍文案必须由剂量-时间面计算得出，不得手写死**；覆盖率口径（对斑块面积 vs 对 1 μg/L 风险区面积）必须与路径模型约定并在图注说明）；**浓度与达标预测**（三候选曲线+1 μg/L 目标线+90% 区间+「预计 5.6 h 达标」标注，**起算口径显式说明**）；**剂量—时间决策**（连续决策面热图+选中点 12 包/5.6h，数据来自 dose_response 代理 D-4，不使用随机彩色渐变）；**执行前检查**（无人机 A 87%/B 92%、天气窗口 09:45–11:30/2.6 m/s 适宜、通信 4/4 在线、复测 12:00 已排程——四项来自 task_plan+设备状态，演示数据标注）。
- 右侧：已选方案摘要（12 包/5.6h/4.2–8.1h/有效期）+ 任务执行时间轴（09:45 发布→09:53 首架到达→10:04 投放完成→12:00 节点复测→15:30 预计达标）+ 无人机分配表 + 「导出方案」（JSON/PNG）。
- 底部（或抽屉）「模型证据与限制」：数据来源/模型域/覆盖边界（「覆盖面积按演示阈值」）/待校准参数（k、包剂量、C_req）——V5 把它从中央区移出，但**「模型证据与限制」内容不可全删**，放进抽屉或详情页。

**新增组件清单**（`src/components/map/`）：LayerChipBar、RiskIsoLayer（等值面）、FlowArrowOverlay、WindArrowOverlay、DropCandidateMarkers、UavRouteLayer、TimeSlider、PatchEvidencePanel、GovernancePanel、PlanCompareCards、ConcTargetChart（Recharts）、DoseTimeSurface（自绘 canvas/SVG）、ExecCheckCards、MissionTimeline、UavGantt（自绘，Recharts 无内置）。

**基础设施**：Vite 代理 /api → 8010（仅模式 B）；TileLayer 归因；`leaflet-heat.d.ts` 已备好。

### 6.3 数据分析页（中等改）

- 顶部筛选行：时间范围+设备筛选+**分析物切换（MC-LR / total MC，仅一个下拉，按 V4 删第二个）**+导出数据（左移到筛选器后）。
- 「AI 预测（未来 7 天）」块 → **「当前风险估计（非未来预报）」**：历史曲线+当前中位数点+80% 区间带+置信点；右侧证据卡：当前状态估计（中位数 2.50/区间 1.60–3.40/超限概率 **P(C≥1) 91%**/模型域 OOD 关注/CMADRE v2 · nowcast 徽章+「建议现场复测」）；删除「预测开始」虚线与未来段。
- 删除：假「模型置信度 87%」、假「下一高风险时间 5月29日」。
- 趋势分析保留三轴 + 阈值线（1.0 警戒/5.0 高风险），数据源统一。
- 「传感器对比」→「节点读数与质量」：新增每行质量状态列（异常/待复测/信号弱/正常），数据来自标定 qc 旗标。
- 左下插图按设计 README V4 换为「吉祥物操作绿色显微镜」（来源：总览页/设备页重设计图），但需生成或裁剪素材——P2，可用现有 `materials/` 素材近似替代。

### 6.4 设备配对页（结构不变，扩展信息）

- 节点详情面板扩展：暗基线（设备自检）、校准状态（已标定/待标定/标定过期）、有效反应时间窗（2–6 h）、trigger 构型与符号（trigger5+ / trigger2−）、OD600（可选）。
- 新增「执行资源」卡区（与传感器卡片分离）：无人机 A/B 电量/就绪/航线预览；不参与蓝牙/WiFi 配对 CRUD。
- 保留现有交互；「拖拽排序」若短期不实现**文案与行为必须一致**（要么接入 dnd-kit，要么删文案）。

### 6.5 公共/全局

- AppHeader 地图态胶囊更新：「闭环运行中」状态徽章常显；风场数据改从场景包/网关取。
- 全局 loading/错误兜底：场景包缺失 → 「演示场景未加载」占位（不白屏）。
- 收敛色阶与两套 risk 色值（统一：正常 #059669 / 关注 #f5c400 / 警戒 #f97316 / 高风险 #ef1919，删除 RiskBadge 内部第二套）。
- web/Technical_route.md、AGENTS.md、CLAUDE.md 路由/数据说明同步更新。
- **构建验证**：npm run build 通过（tsc strict）；新增依赖为零（leaflet/recharts/dnd-kit 已装；如需 gantt 自绘）。

---

## 7. 湿实验侧联动（模型接口要求，非 Web 任务）

| 需求 | 优先级 | 说明 |
|---|---|---|
| 板位随机化 + 独立生物学重复（≥3 批）+ OD600 + 每板空白/哨兵 | P0（湿实验） | 行位混杂（0h RFP 随浓度行 +27.7%）污染 fold；这是标定结论从「方法验证」升级的前提 |
| δ(I) 光死曲线、工程菌降解 C(t)、mlrA 表达动态（12 组曲线达 v1.2 门槛） | P0（湿实验） | 管线的最大不确定度来源；报告 05 §4.4 |
| 10 μg/L 上界点、0.5/1 h 早窗点 | P1 | 补标准曲线动态范围与早期预警窗口 |
| 装置协议：暗电流基线/RFP 单色标样/荧光珠哨兵 | P1 | 设备仿射校准与跨设备迁移 |

---

## 8. 设计图的不合理之处与修正建议（明确指出）

> 以下 13 条是 Web 改造前**必须先定版**的矛盾点。第 1 条是文件管理问题，其余是内容问题。

| # | 设计图/README 内容 | 问题 | 修正建议 |
|---|---|---|---|
| 1 | README 声称的 V3/V4/V5 交付图 7 个文件在磁盘上**全部不存在**；「地图监视页-v2-方案推演-执行检查.png」内容实为 **V5** | 文件名两套命名并存，后续引用哪个版本成谜 | **定版**：以实际存在的 6 张图为唯一实现基准（态势总览/治理规划/方案推演-执行检查〔V5 内容〕/数据分析页-v2〔含 V4 导航修订〕/总览页/设备配对页）；README 文件清单与生成状态表修正为与实际一致；如需保留演进记录，在 README 增「文件-版本对应表」 |
| 2 | 「方案有效期限 15 min」 | 无定义；由风场窗口/光控存活窗口/无人机可用窗口哪个决定不明；且「基于当前风场」与时间滑杆交互冲突 | 明确定义为 min(风场窗口余量, 光控存活窗口余量, 无人机可用窗口)，由网关计算并标注公式；否则删除该字段 |
| 3 | 时间滑杆「+30 min/+2 h/+6 h」 | redo_v2 是 nowcast（明确不做未来预报）；滑杆若把「风险面」外推 6h 即虚假预测；但流场/漂移/降解确实可物理推演 | 滑杆只作用于推演层（水流/覆盖/降解曲线/任务状态），风险面保持「当前状态」，滑杆旁注明；或把滑杆命名为「推演时刻」并默认锁在「当前」 |
| 4 | 「推荐剂量 12 包」「方案 A 8/B 12/C 16 包」 | 无来源且与「单次覆盖 0.05–0.08 km²」不匹配（E13 物理剂量：C0=2.85/24h/25°C/M=1 时 8 点×6 载荷=48 载荷单元，为演示需求 17 的 2.8 倍）；且未带「原型参数」徽章，**违反设计自己的诚实性规则** | 三档方案由 dose_response 在 [D_min, D_max] 区间取 3 档；达标时间/覆盖率/取舍由模型输出+**全部带「原型参数」徽章**；不建议硬编码 12 包 |
| 5 | 「单点覆盖 0.05–0.08 km²」 | 是 5% 演示阈值下的值；C_req 联标后变化（0.2465 时坍缩 6–60×） | 展示「面积随阈值」区间+「原型参数（待 C_req 联标）」徽章 |
| 6 | 「80% 区间 4.80–8.10 μg/L / 超限概率 96%」「数据可信度 中等」 | 标定能力边界是**多通道融合判别**（真实 3σ LOD 量程外、单点 z 0.26–2.03）；6.35 的中值可以给出但必须声明融合通道与来源 | 证据卡加「来源：3 节点 × 3 重复 × 2 通道融合（原型）」；P(C≥1) 用全称 **P(C≥1 μg/L)**；可信度规则前端 util 化并与网关 confidence.level 对齐 |
| 7 | README 写「**三架**无人机」，成图与 V5 均为**两架** A/B | README 自相矛盾 | 以成图为准（2 架），README 修正；场景包与路径模型按 2 架（或 3 机队但界面可配置） |
| 8 | 「预计达标 15:30」起算点 | 推演完成 09:43+5.6h≈15:19；09:45 发布+5.6h≈15:21；仅从首架到达 09:53 起算才自洽（≈15:29） | 界面显式说明起算口径（建议统一从「首架到达」或「投放完成」起算，或时间轴部件标「达标为治理生效时刻」） |
| 9 | 覆盖率 8 包 84% / 12 包 92% / 16 包 95%（+33% 用量仅 +11 个百分点） | 覆盖率口径（对斑块面积 vs 对 1 μg/L 风险区面积）未定义；与治理规划图「椭圆几乎铺满」视觉不一致 | 与路径模型约定口径（建议：有效覆盖面积 ∩ 风险斑块面积 / 斑块面积），图注写明 |
| 10 | 态势总览图层抽屉：☑MC-LR 风险/设备/水流场/风场/total MC/不确定性；README 图层表：MC-LR 风险/预测风险/设备/水流场/风场/投放覆盖/无人机路线 | 抽屉与图层表互相不一致（抽屉有 total MC/不确定性，表有预测风险/投放覆盖） | 统一图层清单：MC-LR 风险/环境风险估计(nowcast)/设备/水流场/风场/投放覆盖/不确定度；「total MC」作为分析物切换而非图层 |
| 11 | 数据页 V4「左下插图换吉祥物操作绿色显微镜」 | 未落盘（`数据分析页-v2.png` 仍是水豚+烧瓶） | 实现时按 V4 执行；素材可从 `web/materials/` 或总览页重设计图裁剪 |
| 12 | 顶部胶囊文案：「闭环运行中」（态势/规划）vs「热力图实时更新」（推演页） | 同页三状态三种文案 | 统一为「闭环运行中」，推演态可加「推演完成 09:43」副标 |
| 13 | 「12 包=每点 3 包」分配明细、设备名笔误「撞水口监测-04」（其余页为「排水口监测-04」）、数据页 2.50 μg/L 与节点 6.35 的关系（口径混用） | 剂量分配明细缺失、跨页设备名不一致、估计值（环境侧 CMADRE）与实测值（节点标定）易误读 | 界面上剂量按「每投放点包数」明细展示；设备名统一（以 demoReadings.ts 为准）；证据卡加 tooltip 解释「当前状态估计=环境侧融合，非全湖平均；节点实测见上图」；两处超限概率保留但统一为 P(C≥1 μg/L) 并注明作用域（斑块级/湖面级） |

---

## 9. 分阶段实施路线与验收

> 依赖链（严格）：R-1/R-2 源码与制品恢复 ∥ D-1 换锚 → W-1 联标 ∥ C-1 fuse → D-2/D-3/D-4 api+代理 → P-1/P-2/P-6 v3.0 → 网关静态导出 → Web 地图三状态 → 其余三页 → 端到端复盘。

### Phase 0：契约冻结 + 数据对齐（2–3 天）
- 产出 §3 的 JSON Schema（5 个标准记录+信封）+ `pipeline-server/docs/contract.md`；五模型 README 各加「管线接口」一节（指向 contract 版本号）；设计资产定版（§8 第 1 条：文件-版本对应表）。
- **验收**：每个模型给出符合 schema 的样例记录（可用现有脚本生成）；confidence 字段全部有值；设计图引用文件名与实际一致。

### Phase 1：模型侧 P0 项（2–3 周）
| 周 | 内容 | 验收 |
|---|---|---|
| W1 | R-1/R-2 源码与制品恢复（服务器拉取或 pyc 反编译辅助重实现 I5）；D-1 v1.2 换锚（A1–A7 全部+参数溯源台账+fig4–6 重生成） | pytest 通过；台账齐全；fig 数字与表一致 |
| W2 | W-1 C_req↔thr_rel 联标（门限换算表+重算覆盖面积区间）；C-1 fuse()+融合 z 提升报告；C-5 修复 evaluate 断裂 | 水流 README「演示值」换为联标值并标注；融合报告 z~√N 曲线+有效样本保守估计 |
| W3 | P-2 续航计费+E13 复跑（≥1.9×）；P-1 v3.0 契约接入 D-2/D-3（双来源 C0 规则落地）；P-6 训练口径修复 | E13 复跑 1.91× 且能量审计 100%；任务库 hash 与上游一致；重训 outB′ |

### Phase 2：服务化 + 静态场景包（1 周）
- D-2/D-3/D-4（api.py+GBDT 代理）、W-2（SWF 适配器+GeoJSON）、C-6（标定适配器+artifact 补全）、R-3/R-4/R-5（网格导出+p_env+契约）、P-5（规划适配器）→ pipeline-server 端点在本地跑通；`export_demo_scenario.py` 产出 pipelineScenario.json + GeoJSON 进 web/。
- **验收**：curl /api/v1/overview 与场景包字段一致；场景包在无后端下可驱动全 Web 演示；每个数字可回链到 provenance。

### Phase 3：Web 改造（2 周）
- 6.2 地图三状态（先场景包后网关）→ 6.1 总览 → 6.3 数据页纠偏 → 6.4 设备页扩展 → 6.5 全局。
- **验收**：npm run build 0 error；四页截图与设计图（定版 6 张）逐项对照通过；「原型参数」徽章在所有未标定数字上出现；「未来 7 天/置信度/下一高风险时间」无残留；地图离线降级可用；数据一致性（header/KPI/曲线单一来源）。

### Phase 4：端到端复盘（1 周）
- e2e_demo 时间线：东湖风况日→风险面→节点报警（含融合决策）→生成方案→下发→执行（模拟）→复测→效果复核（预计达标 vs 复测值；闭环指标：区间覆盖率/命中率）→（远期）标定再学习回环。
- **产出**：演示视频脚本+评审证据包（对照实验：有/无流场推演的点位差异、有/无融合的单点检出差异）——直接支撑 iGEM Engineering/Innovation/Safety 评分点。

---

## 10. 风险、边界与诚实性声明

1. **数据诚实性（必须写进所有展示材料）**：①redo_v2 无东湖毒素标签（训练 99.5% 美/加，东湖输出属「外域估计候选」，且 total MC 上仍不敌简单 RF 基线）；②浓度标定融合基于 33h 湿实验工作簿+合成数据先验，真实数据存在行位混杂/重复非独立，真实 3σ LOD 量程外；③降解模型 v1.2 换锚后仍属「文献先验+情景灵敏度」，工程菌 k 未实测；④水流无东湖实测流速对照，水深为形态学重建（泥层 1.06 m 未入模）。→ 页面与答辩口径必须带「当前能力边界」，不允许「我们已经能精准预测东湖」类表述。
2. **明确不做**：未来预测（1/3/7 天）、total MC↔MC-LR 固定换算（redo_v2 拒绝的边界）、端到端黑箱一体化模型、真实无人机/硬件通信（演示用模拟执行）、用户认证与数据持久化。
3. **工程风险**：
   - **产物不入库**：.gitignore 全局排除 `**/data/`、`*.npz`、`*.csv`、`*.xlsx`、`*.pt/*.ckpt/*.pkl` 等——**换机/重新 clone 后所有模型产物与 ckpt 必须重新生成或手动拷贝**（重训预估：SWF 管线一步 30 min、路径 outB 25 min、redo_v2 数小时 GPU）。方案要求各模型 README 增加「产物来源清单」+ 归档介质说明。
   - **redo_v2 正式 run dirs 在服务器**：若不同步，本地只能 smoke 级输出（接口演示）；I5 冠军代码仅存 pyc，恢复路径不确定（拉取/反编译/重训三选一，需在 Phase 1 内决策）。
   - **tile 合规**：OSM 公开瓦片有使用政策（归属/请求量）；演示机建议离线 mbtiles 包或降级示意图模式。
   - **五模型环境各异**（conda igem-cyanohab / torch CPU / xgboost/catboost），网关独立 venv 并锁定版本；pyc 为 Python 3.12（服务器 3.11），恢复源码后须在 pyproject 范围内验证。
   - **跨模块契约版本漂移**：contract 版本号必须进每个输出信封，不匹配即断点（回归测试）。
   - **文档-代码漂移**：本次盘点确认的多处旧数字（MODEL_ARCHITECTURE §6/§7.3/§8.2、IntroductionMD、TEACHING_GUIDE、train.py 口径、README 目录等）必须在各自模块改造时同步修复，否则后续会话引用会继续放大误差（W-5/P-8/F 系列）。
4. **评审对齐**：闭环价值证明需要对照实验——建议 Phase 1 即准备「无流场推演 vs 有推演」（覆盖斑块 vs 直接投中心）、「单点 vs 融合」（z 2.03 vs 3σ）对比表；创新点申明与公开文献差异（标定 report/07 §5 先例调研）。

---

## 附录 A：关键既有文档索引（本方案依据）

| 主题 | 文档 |
|---|---|
| 闭环接口总览 | model_concentration_calibration/report/07_系统级衔接与集成报告.md（§1 接口表、§2 四项调整、§4 真实数据审计） |
| 降解适配 | model_MC-LR_degradation_kinetics/report/05_五模型管线协同调研与降解模型适配评估.md（§3.2、§5 A1–A7） |
| 路径适配 | model_path_planning/report/06_五模型联动适配性审查与路径规划改进方向.md（§2.1 契约、§3 失配点 1–6） |
| 水流-规划端到端 | model_Two-dimensional_water_flow/report/experiments/E13_pipeline_interface.md（续航语义、physical_thr_rel、dose_i） |
| 水流最新实验 | model_Two-dimensional_water_flow/report/实验记录_EXPERIMENTS.md、E9/E11/E12（cd_lake、thr=0.2465、系综） |
| 标定真实数据审计 | model_concentration_calibration/report/07 §4、src/loader.py、scripts/_real_fit3.py（trigger5 z=2.03） |
| 降解质量审查 | model_MC-LR_degradation_kinetics/report/04_交付物质量审查报告.md（A1–A4、B/C 类） |
| redo_v2 | model_redo_v2/report/MODEL_OBJECTIVE_SPEC.md、FINAL_MODEL_REPORT.md、SERVER_RUN_REPORT.md、迭代记录.md；源码快照 `model_redo_v2_server_20260810/model_redo_v2/` |
| 路径 V3 | model_path_planning/report/09_模块级优化验证报告.md（M1–M7） |
| 设计 | design-assets/page-objectives-redesign-v2/README.md 及 6 张成图 |
| Web 现状 | web/Technical_route.md、web/src/pages/*、web/src/data/* |

## 附录 B：本方案（V2）与 V1 的差异清单

| # | V1 表述 | V2 核实结果 | 处理 |
|---|---|---|---|
| 1 | R-1「从根目录 model_redo_v2_server_20260810.tar.gz 解出源码」 | **tar.gz 不存在**；实际是未压缩目录 `model_redo_v2_server_20260810/model_redo_v2/`（含完整 v2 源码 35 个 .py + pyproject/run_train/run_validate/configs/tests） | 改为「目录恢复（R-1）」，并新增警告：快照为 8-10 的 v2 状态，**最终 I5 冠军代码仅存本地 pyc**；正式 run dirs 需从服务器拉取（R-2） |
| 2 | 各模型缺口表按「V1 时点」描述路径规划（v3.0 未落地） | 路径规划 **V3 模块验证轮已合入**（M1–M7：t_service=1.0、κ=1.15/E_res=2.0 默认、多访问完成时刻修复、constraint-aware LS、highprio 重规划模式）；但 v3.0 契约（P-1）、续航计费（P-2）仍为 P0 未做 | 缺口表更新（P-1/P-2/P-6 补充新发现口径问题：train.py 默认 κ 不一致、rollout hover 0.13 vs 1.0） |
| 3 | 水流模型「覆盖阈值仍是演示 5%…」未提落地状态 | B3 水深/cd_lake/windage 2%/physical_thr_rel/E13 **均已落地**（E14 基线）；新增缺口：文档旧数字（§6/§7.3/§8.2）、SweConfigSI 类默认陷阱、历史流场 npz 字段不兼容 | 更新缺口表（W-5/W-6 新增） |
| 4 | 设计图「V4/V5 为当前推荐（5 张成图）」 | README 演进到 V5，但文件名两套并存（v3/v4/v5 文件全部不存在；V5 内容保存在 v2 前缀文件）；6 张文件为唯一实现基准 | §8 第 1 条定版；Web 基准表更新（6.2 状态 C 以 V5 内容为准） |
| 5 | 附录称「五模型环境各异」但未提 redo_v2 pyc Python 3.12 vs 服务器 3.11 | 已核实（.pyc 均为 3.12.13；快照 pyproject 要求 ≥3.11,<3.14） | §10 风险补充 |
| 6 | Web 现状表 | 补充实测细节：@theme token 零引用、AquaCard/RiskBadge/StatusBadge 零引用、dnd-kit 未用、无 public/、header 9/2/3 vs 8/3/3、三处曲线矛盾 | §2.2、§6.5 补充 |

---

*文档版本 V2（2026-08-25 定稿）· 适用仓库根目录 IGEM-dry · 下一版本触发条件：Phase 1 P0 项全部验收通过后更新为 V3（含实测参数回填）。*
