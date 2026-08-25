# CMADRE 架构审查扩展轮次（R9–R24）

审查日期：2026-08-11
审查人：Dry Lab 建模组（本会话）
补充材料：`tmp_code/audit_review.py`、`tmp_code/local_diagnostics.py`、`tmp_code/make_figures.py`、
`references/review_data_audit.json`、`references/review_local_experiments.json`、`figures/`

## 0. 为什么需要这份文件

`ARCHITECTURE_ITERATIONS.md` 记录了设计阶段的 **R1–R8**（8 轮架构设计迭代）；
`迭代记录.md` 记录了服务器训练迭代 **I0–I5 及独立种子复核**（7 轮，每轮都有真实训练证据）。
按项目要求“至少进行 20 次全量且仔细的架构审查/改进”，本文件补充 **R9–R24（16 轮）**，
三者合计 **8 + 7 + 16 = 31 轮** 已记录在案。R9–R24 以“只读代码审查 + 本地可复现实验 + 数据审计”为主，
不消耗服务器锁定测试，也不对任何已冻结的 test 重新调参。

每轮结构：**审查对象与证据 → 发现 → 决策/行动**。

---

## R9 数据质量与标签语义全量审计

**审查对象与证据**：四张模型表（total MC dynamic/static、MC-LR dynamic/static）的程序化审计，
`references/review_data_audit.json`；脚本 `tmp_code/audit_review.py`（只读）。

**发现**：

| 表 | 行 | 精确 | 删失 | 删失均有 LOD | 来源 | 水体 | 站点×日重复组/多余行 |
|---|---:|---:|---:|---:|---:|---:|---:|
| total MC dynamic | 20,852 | 9,528 | 11,324 | 100% | 16 | 3,467 | 24 / 24 |
| total MC static | 20,941 | 9,577 | 11,364 | 100% | 17 | 3,500 | 25 / 25 |
| MC-LR dynamic | 2,837 | 2,837 | 0 | — | 3 | 392 | 19 / 19 |
| MC-LR static | 6,409 | 2,992 | 3,417 | 100% | 4 | 473 | **1,025 / 2,565** |

- total MC 精确标签分位：中位 0.19、q90 3.12、q99 21.88、q999 169.2、最大 743.75 µg/L；无 >1000 值。
- MC-LR 精确标签：中位 0.15、q99 492.4、最大 **26,105.59 µg/L**；24 条 >1000 全部来自 Uruguay。
- total MC 99.5% 记录来自美国（20,750/20,852），加拿大 102 条；**没有中国毒素标签记录**。
- 特征覆盖：total MC core_field 全有率为 0.566，bloom 0.481；MC-LR dynamic core 0.319（全有率）。
- 质量标志：total MC 有 11,221 条 `censored_substitution`（半检限替代）和 103 条
  `interval_censored_component_midpoint`；MC-LR 有 24 条 `extreme_review_gt_1000`。

**决策**：① 维持“区间标签优先、中点仅作透明代理”的决定，当前数据确实 53–54% 删失；
② total MC 的“半检限替代”是既有数据层事实，模型层已用区间边界覆盖，无需改数据；
③ 审计确认 total MC 无 >1000 极端值 → 之前分析的“总 MC 尾部极端”主要来自 MC-LR 任务的 Uruguay 数据。

---

## R10 有效样本量与重复/近重复结构

**审查对象与证据**：同表按 `(dataset_id, site_id, sample_date)` 分组计数（见 R9 表）+ 组内标签一致性检查。

**发现**：

- MC-LR static 有 **1,025 个“同站点同日”组、2,565 条多余行**（占行数的 40%），其中 870 组标签完全相同、
  155 组不同（可能为同期重复样或同站多深度/多方法）。
- 这些组几乎全部来自 **Sacramento（1,006 组，2,545 条多余行）**；Uruguay 仅 19 组。
- 含义：static 任务的“有效独立样本”远小于 6,409 行；以行数为分母的任何随机切分指标都会被夸大；
  Sacramento 的 134 条精确测试标签也来自少数站点-日的重复测量，排序指标的信噪比低。

**决策**：① 在统计口径上把“有效站点-日数”作为报告并列指标；② 若把 Sacramento 作为评价来源，
其内部样本不可当成 3,551 个独立观测；③ 列出待办：在数据层增加“同源同站同日聚合”视图（聚合为区间
[L,U] 或日值，按方法分层），作为 P1 数据工程项。未修改任何原始/处理表。

---

## R11 “精确零值”语义疑点

**审查对象与证据**：精确值为 0 的记录计数与来源分布。

**发现**：

- total MC：321 条精确 0，其中 NLA2012 288 条、NOAA Lake Erie 33 条；
- MC-LR dynamic：319 条精确 0（EMLS 195、Uruguay 108、Buffalo Pound 16）；static 326 条。
- NLA2012 源字典区分 `MICL_FLAG`/`MICX_FLAG` 与 `RESULT`（ug/L），并单列 MDL/RL；
  若源数据把“检出但低于 MDL”编码为 0，则这些 0 应视为左删失而非真值 0。
- AFT 训练偏移为 `max(P1(正边界)/10, 1e-8)`；大量“0 精确值”会与“正偏移压缩”形成张力，
  可能同时污染 AFT 尾部与中点代理。

**决策**：① 不删除、不改写；② 在 P0 加入“逐来源 0/ND 语义审计”：核对 EMLS 文档与 NLA2012
FLAG 定义，若确认 0=ND 则把该来源的 0 移入删失区间 `[0, LOD]`（LOD 取来源 MDL/RL）；
③ 当前正式模型不做该改动，避免与已冻结 v2 制品冲突。

---

## R12 简单基线门禁：同切分本地实验

**审查对象与证据**：`tmp_code/local_diagnostics.py` 使用与服务器相同的协议与默认配置
（source_ood 5 折 / waterbody_ood 5 折，seed=42，test_fold=0，validation_fold=1，min_feature_count=3），
在本地复刻切分后训练 Dummy median、来源先验、ElasticNet、RandomForest、删失 MLP 代理。
测试折规模与服务器记录完全一致（total MC 4,298 行 / 1,876 精确；MC-LR 568 精确），
证明切分清单逐字复现。结果见 `references/review_local_experiments.json` 与 `figures/fig05_*.png`。

**发现（total MC source OOD，1,876 条精确测试标签）**：

| 模型 | log1p MAE | Spearman | R² | factor-of-2 | top-1% 尾部 log1p MAE |
|---|---:|---:|---:|---:|---:|
| Dummy median（训练中位数） | 0.3786 | — | -0.028 | 0.365 | 3.85 |
| 来源先验 | 0.3805 | — | -0.028 | 0.347 | 3.85 |
| ElasticNet（log1p） | 0.3717 | 0.152 | -0.010 | 0.297 | 3.52 |
| **RandomForest（300 树）** | **0.2917** | **0.470** | **0.061** | **0.442** | **2.44** |
| 服务器 v2 stacking（文档值） | 0.3488 | 0.319 | -0.011 | 0.381 | 3.61* |

*尾部值为 `迭代记录.md` 记录的事后诊断（19 条 top 1%）。

**发现（MC-LR waterbody OOD，568 条精确测试标签）**：

| 模型 | log1p MAE | Spearman | R² | factor-of-2 | 中位AE (µg/L) |
|---|---:|---:|---:|---:|---:|
| **Dummy median** | **0.2988** | — | -0.007 | **0.577** | 0.0271 |
| RandomForest | 0.3527 | 0.401 | 0.001 | 0.382 | 0.2087 |
| 删失 MLP 代理 | 0.3479 | 0.364 | -0.006 | 0.394 | 0.1486 |
| 服务器 v2 stacking（文档值） | 0.2972 | 0.509 | -0.005 | 0.541 | 0.1029 |

**解读（重要，直接改变项目措辞）**：

1. **total MC 上，同一外部切分里一个未经删失感知调优的 RandomForest（log1p 中点、0.25 删失权重、
   中位数插补、300 树）在 log1p MAE、Spearman、R²、factor-of-2 和尾部五个指标上同时优于 v2 集成。
   这说明 v2 的“组合复杂度”在 total MC 当前测试折上并未换来优于强树基线的点精度**——
   v2 的真正价值目前只体现在概率区间与删失利用上，而不是点精度。
2. **MC-LR 上，v2 集成（0.2972）几乎等于 Dummy median（0.2988）的 log1p MAE**，
   但 factor-of-2（0.541 vs 0.577）与 Spearman（0.509 vs 未定义）显示：模型把价值放在
   “排序与尾部识别”而不是平均对数误差上；单一 log 类指标不足以证明价值。
3. 这佐证了 `LITERATURE_AND_MODEL_REVIEW.md` 的判断：**复杂度必须用非 IID 门禁换取**，
   而且现在的门禁结论是“v2 在点精度上尚未通过，在区间/排序上有条件通过”。

**决策**：① P0 强制要求所有正式运行同折附带 Dummy/来源先验/ElasticNet/RandomForest 基线；
② 把“稳定击败最强简单基线”写进部署门槛；③ 不因本次本地结果就回退 v2（单折、单种子、本地无
原版 TabM 与 GPU 调参），但 **v2 不得宣称“优于强基线”**，只能宣称“提供了删失感知概率输出”。

---

## R13 本地删失 MLP 代理实验：深度模型的域外不稳定性

**审查对象与证据**：与项目 TabM 同损失族（log1p 高斯区间 NLL、σ 有界 [0.03,3.0]、AdamW、
早停）的简化单成员 MLP（256-256-128），但**未加缺失指示掩码、无 member 集成、无来源均衡批次**。
结果见 `references/review_local_experiments.json`。

**发现**：

- **total MC：灾难性外推**。测试集 log1p MAE 0.943（远差于 RF 0.292）、R² ≈ -2.4e17、
  平均区间宽度 ≈ 988,026 µg/L。原因是：位置头 μ 无上界 + 测试折（来源外推）存在训练时未见的
  缺失模式/特征组合，σ 虽被限制但 μ 依然爆炸；单成员无集成就没有“宽区间被平均稀释”的副作用，
  也没有缺失指示让网络区分“真零值”与“缺失”。
- **MC-LR：可用但点精度弱**。log1p MAE 0.348、Spearman 0.364、coverage 0.852、宽度 4.65 µg/L；
  区间覆盖率接近名义 80%（服务器 v2 为 0.79），但点精度低于服务器 v2（0.2972）。
- 对照说明：项目正式 TabM 加了缺失指示、24 成员、来源均衡与宽度惩罚（I1/I2 修复），
  因此不能把本代理的失败直接归咎于“深度删失模型不可行”；但它**定量证明了**：
  缺少缺失掩码/member 集成/μ 饱和的朴素深度删失网络在跨来源外推下不可部署。

**决策**：① 维持 I4 的“tree-only 候选优先”与 I5“log-blend 几何融合”；
② 新增待办：TabM 的 μ 头加饱和上限（或 log1p 输出变换+截断），并在 P1 用重复外层折验证；
③ 把“无界预测头 + 域外缺失模式”列入已知风险清单（与服务器 I5 的 AFT 无界外推测同理）。

---

## R14 AFT 分布假设与分位数转换的一致性审查

**审查对象与证据**：`src/cmadre/models/xgb_aft.py`（`_latent_quantile_multiplier`、
`predict_distribution`、`exceedance_probability`、`distribution_scale` 固定为 1.0）。

**发现**：

1. q10/q50/q90 由“单点预测 × 固定潜变量分位数乘子 − offset”得到：对 normal，乘子为
   `exp(1.0·Φ⁻¹(q))`，即**所有样本共享同一相对宽度**，没有异方差尾巴；对 0 附近的浓度，
   q10 可能为负并被 `np.maximum(...,0)` 截断，形成 0 处质量堆叠。
2. `exceedance_probability` 对 non-normal 分布使用 `expit(standardized)`（即 logistic 生存函数），
   而 `predict_distribution` 对 non-normal **统一用 normal 分位数近似**（代码注释也承认“deliberately
   explicit”）。两者对 extreme-value 分布不一致：若日后把 `aft_loss_distribution` 设为 extreme，
   区间与超限概率将来自不同分布 → 必须修复或禁止该组合。
3. `distribution_scale` 固定为 1.0（default.json），从未做分布（normal/logistic/extreme）×
   scale 的内部折选择；`迭代记录.md` 1.2 已列此待办，但尚未执行。

**决策**：① 当前配置只用 normal，不触发不一致；但把“extreme × 不一致转换”写成 P1 修复项
（统一为同一分布族的严格分位数，或直接限制仅支持 normal/logistic）；
② AFT 分位数宽度固定 ⇒ 主区间信息由 CatBoost/TabM/q90 提供，此点已在 I4 的 tree-only 方案中体现。

---

## R15 特征面板与缺失模式审查

**审查对象与证据**：`src/cmadre/features.py` 预注册面板 + `data.py` 全缺失特征丢弃逻辑 +
`audit_review.py` 覆盖率输出。

**发现**：

- `core_field` 预注册 20 列；total MC 可用 20 列；MC-LR dynamic 实际只有 **14 列**（
  nitrate/nitrite/doc/toc/max_depth/silica 被 `load_dataset` 判定为“全缺失”并丢弃）；
- `static_context` 43 列；MC-LR static 实际参数 35 列（8 个 WorldCover 列全缺失）；
- MC-LR dynamic 的全有率仅 0.319，说明“core 面板”在 MC-LR 上是**半缺失**面板，
  与 total MC 的 0.566 不同——同一个面板名在两个任务上的信息容量并不等价。
- 缺失由树模型天然处理（split 按缺失走默认方向），但 TabM 的 RobustNumericPreprocessor
  显式加了缺失指示（`add_missing_indicators=True`）——这正是 R13 代理实验缺失的部分，
  也是正式 TabM 比代理稳健的重要原因之一。

**决策**：① 面板命名保持（避免在部署时按任务切换白名单），但在报告中为每个任务明确
“实际特征数=可用数”；② 把“面板×任务全有率”纳入模型卡；③ 记录 MC-LR static 的
WorldCover 全缺失事实，禁止把 static 结果解释为“土地利用已被验证”。

---

## R16 特征—标签关联的来源依赖性审查

**审查对象与证据**：审计脚本按来源计算的 Spearman（log1p 标签 vs 特征）。

**发现**：

- 全数据层：total MC 与其相关性最强的是 `sample_depth_m`（-0.52）、`turbidity_ntu`（0.45）、
  `chlorophyll_a_ug_l`（0.44）；MC-LR 的是 `cyanobacteria_cells_ml`（0.60）、`month_sin`（0.43）、
  `water_temp_c_best`（0.33）。
- **按来源分解后关系大变**：NOAA Lake Erie 的 Chla–total MC 相关为 0.67，而 NRSA2013_14 的同对相关仅
  0.15 且 TN 相关 0.21；Uruguay 的蓝藻细胞–MC-LR 相关 0.60，但 Buffalo Pound 则是 pH 0.58 /
  电导率 -0.54。**同一特征在不同来源的方向和强度都不同**。
- `sample_depth_m` 的负相关很可能是“来源/水体类型混杂”（浅水农塘浓度高、深湖调查浓度低），
  不是深度本身的因果效应。

**决策**：① 禁止把全数据相关系数当作“生态规律”写进论文；② 排序类指标必须按来源宏平均与
最差来源报告（已实现）；③ P1 保留“来源×特征交互”显式建模（树模型已隐式处理）与
GroupDRO 对比实验，看是否能在保持平均精度的条件下改善小来源。

---

## R17 Stacking 目标与集成稳定性审查

**审查对象与证据**：`src/cmadre/ensemble.py`（median_nnls 与 distributional 两种目标、
起点集合、SLSQP）、`迭代记录.md` I2/I3/I4/I5 的五折结果与权重。

**发现**：

- v2 的 `median_nnls` 在 MC-LR static 上给出边界解 `(0,1,0)`；I2 的 distributional 目标在
  MC-LR 上给出 `(0.35 AFT, 0.41 tail-quantile, 0.23 TabM)`，但普通 XGBoost quantile 单模型
  在历史 test 上却优于 ensemble（0.2423 vs 0.2615）——**OOF 目标选择与单测试折结论冲突**。
  这说明集成权重方差大、依赖折配置，不能用单 test 事后仲裁。
- distributional 目标的宽度惩罚为 `(max(q90−q10,0)−4.0)²` 的**平方惩罚**，对大宽度异常值敏感，
  主要由 TabM/AFT 的爆点驱动；I5 的 log-blend（加权几何均值，`stacking_blend_transform=log1p`）
  在保持主指标的前提下把区间宽度由 47 → 38.9，并把最坏折原尺度 MAE 从 64 → 62.3。
- 五折复算（I3）证明 I2 的点收益与尾部收益跨折一致（MC-LR 五折 log1p MAE 0.3321→0.2680），
  而 total MC 的 bloom 面板收益有限且来源间方差仍主导。

**决策**：① 冻结 I5 `mc_lr_bloom_v5_log_blend.json` 为 MC-LR 综合候选、`mc_lr_bloom_v4_tree_only.json`
为近中位备选；② P1 完成“删失感知 stacking”（直接最小化 OOF 区间似然/interval score 而非中点 NNLS），
并给出权重 bootstrap 置信区间；③ 禁止用 locked test 重新选权重。

---

## R18 CQR 校准的覆盖假设审查

**审查对象与证据**：`src/cmadre/calibration.py`、`MODEL_ARCHITECTURE_AND_RESULTS_ANALYSIS.md` §7.4/§8。

**发现**：

- CQR 只在 **validation 的精确标签**上拟合，得一个**全局标量 adjustment**；删失样本不参与
  coverage 计算；`scope="exact_observations_only"` 已写入制品。
- MC-LR static 的 coverage=1.000 建立在 134 条精确样本 + 平均 1.9 µg/L 的宽区间之上；
  total MC coverage 0.832、MC-LR core 0.7905（各接近 80% 名义值），但交换性假设在
  跨国家/跨年代时并不成立。
- 代码已支持 `conformal_transform=log1p`（迭代记录 §10.1 消融：与 identity 无实质差异，
  因为多数折 adjustment=0，说明区间宽度来自基模型/stacking 而非 CQR）。

**决策**：① 不夸大 coverage 的意义；② P1 实现 Mondrian（按 source/season 分组）与
truncated density-ratio weighted conformal；③ 在每轮报告同时列出“精确标签 coverage、平均宽度、
分来源覆盖率、高风险子集覆盖率”。

---

## R19 OOD 检测器审查

**审查对象与证据**：`src/cmadre/ood.py`、正式结果中的 OOD 比例。

**发现**：

- 检测器 = 训练折内中位数填补 + 稳健裁剪 + 标准化 + 缺失指示扩展 → Ledoit-Wolf 收缩协方差
  平方马氏距离 → 训练分布 99 分位阈值。
- 正式结果 total MC 外部测试 99.3% 被判 OOD、MC-LR static 100% OOD——**单高斯椭球把
  来源特有缺失模式也当作“远”**；而 `迭代记录.md` 又发现 MC-LR 极端值多数**未被**特征 OOD 检出，
  说明主要问题是 `P(Y|X)` 的概念偏移而非边缘特征距离，OOD 高比例与“预测错误”没有直接对应。
- 全项目 **425,530 条中国协变量**（`china_covariates.csv`）与太湖多模态表尚未进入任何正式训练
  —— 而设计文档第 6 轮明确计划用它训练域分类器/密度比，这是实现与设计之间最大的空白之一。

**决策**：① OOD 分数只用于“提醒/拒绝/建议采样”，不用于证明预测正确性；
② P1 实现：训练域 vs 中国域二分类器、特征级归因（SHAP/置换）、近邻距离、截断密度比；
③ 把中国协变量接入 OOD/校准流程，作为“无标签中国数据唯一无争议用途”。

---

## R20 评估指标与验收协议审查

**审查对象与证据**：`src/cmadre/metrics.py`、`MODEL_OBJECTIVE_SPEC.md` 验收标准、
`迭代记录.md` I3 新增尾部指标。

**发现**：

- 已有：log1p MAE、原尺度 MAE/R²/MedianAE、Spearman、factor-of-2、区间距离 MAE、
  精确 coverage、观测区间 compatibility、来源宏平均/最差来源、OOD 比例，I3 起增加
  q90/q95/q99 尾部 MAE、低估率（`run_outer_cv.py` 正式指标）。
- **尚未有**：区间评分（Winkler/interval score）、CRPS、校准误差（ECE）、风险阈值指标
  （Brier、PR-AUC、阈值召回、决策曲线）；`risk_thresholds_ug_l` 在全部配置中为空。
- `log1p MAE` 与 `R²` 同时出现是刻意的：前者稳健、后者对尾部敏感，二者一起读才能
  暴露“普通样本尚可、尾部失败”的结构（§12.1 已论证）。

**决策**：① P0 完成风险阈值版本化配置（饮用水 1.0 µg/L、娱乐接触、工程菌触发场景分别配置）并
补 Brier/ECE/PR-AUC/决策曲线；② 指标命名注明“仅精确标签”或“全部区间”，防止混用。

---

## R21 时间序列能力边界审查

**审查对象与证据**：`configs/total_mc_temporal.json`、`splits.temporal_folds`、数据画像
（站点单次观测比例、LSWT 同日 1,219 条）。

**发现**：

- `temporal_ood` 协议与配置均已实现；但正式三项运行没有 temporal 任务，`迭代记录.md` 也未提交
  temporal 结果，原因是：绝大多数站点只有一次观测，无法在来源内构造严格滞后序列；
  同日 LSWT 仅 1,219 条（占 5.8%），无法覆盖“前 3/7/14/30 天”滞后特征矩阵。
- 因此当前模型是 **nowcast（当前状态估计）**：标签与水质大多同日记录，代码中没有滞后窗口、
  递归状态或时间编码器。这是诚实且正确的边界。

**决策**：① 不把 nowcast 描述成“预测未来”；② 未来预报列为 P2，要求先获得严格早于预测时刻的
气象/水文/LSWT/遥感与历史毒素序列，并用 rolling-origin 评估 1/3/7 天预报。

---

## R22 测量方法与分析物等价性审查

**审查对象与证据**：`迭代记录.md` §6（Uruguay `mcy` 为 ADDA-ELISA 估算值）、
`MODEL_DATA_SPEC.md`、`CURRENT_DATA_ASSESSMENT.md`、I3 §8.3 的分析物敏感性实验。

**发现**：

- Uruguay 约占总 MC-LR dynamic 的 84%，其 `mcy` 由 Microcystins-ADDA ELISA 估计，
  与 LC-MS/MS 单异构体定量不是同一测量模型；静态表中 Sacramento 占 66%，WQP 的
  `Microcystin` 聚合查询也不等于 MC-LR 专属测定。
- 排除 Uruguay 后严格 congener-specific 视图仅约 444 行：五折 `log1p MAE=0.1425±0.0900`、
  原尺度 MAE 0.267 µg/L、Spearman 0.169、R² -0.057——误差尺度大幅缩小但排序仍弱。
- 该结果证明：**当前 MC-LR 的“大误差”有一大部分是测量学/分析物定义造成的域效应，
  不是模型能力；同时严格 LC-MS/MS MC-LR 标签量不足，无法支撑高精度排序模型。**

**决策**：① 把 Uruguay 单列为 `mc_lr_equivalent_adda_elisa` 辅助任务（若领域专家确认），
与 congener-specific 数据使用独立头或独立校准器；② 新数据优先级：分析方法明确的
LC-MS/MS MC-LR + 同步藻华生物量与营养盐；③ 禁止把 ADDA-ELISA 当量直接称为 MC-LR。

---

## R23 中国域数据的正确使用审查

**审查对象与证据**：`china_covariates.csv`（425,530 行，无毒素标签）、
`taihu_*_multimodal_covariates.csv`、`CURRENT_DATA_ASSESSMENT.md` §4、NESDC 东湖数据下载记录。

**发现**：

- 设计文档把“中国域分类器 / 截断密度比 / 无监督预训练 / 插补器”列为第 6 轮计划，
  **但没有任何代码引用这些表**（grep 确认 `src/` 无 china/taihu/domain 引用），
  这是“设计—实现”差距最大的一处；正式 OOD 只用了有标签来源内的协变量。
- 可争议用途（按收益与风险排序）：① 域分类器与密度比（校准/OOD）；② 缺失模式插补器；
  ③ 掩码重建预训练；④ 东湖候选输入覆盖度绘图指导主动采样。
- 禁止用途保持不变：伪标签、Chla/TSI 代替毒素、最近邻伪标注、仅协变量对齐即宣称中国准确。

**决策**：P1 实现 ①②（无需任何毒素标签），③ 作为消融；④ 配合东湖监测计划。本文件不新增代码。

---

## R24 部署链路与风险决策审查

**审查对象与证据**：`src/cmadre/inference.py`、`configs/*.json` 的 `risk_thresholds_ug_l`、
`model_concentration_calibration/` 与 `model_MC-LR_degradation_kinetics/` 的存在性、
`docs/Introduction/IGEM项目简介.md`（WHO 1 µg/L、工程菌 67 倍感应、Lux 放大、mlr 降解）。

**发现**：

- 推断链路是完整且防错的：必须提供与训练完全一致的特征列（`missing_columns` 直接报错）、
  输出基模型/集成/校准/`ood_score/ood_flag` 全列；制品可脱离重训回载。
- **但部署决策契约未闭合**：`risk_thresholds_ug_l` 全部为空 → 没有任何正式配置产生
  `p_exceedance` 与阈值召回/误报指标；OOD 只标 flag，没有“拒绝预测”的动作路径。
- 项目闭环需要三层模型联合：① 本模型：环境→毒素浓度分布（nowcast）；
  ② `model_concentration_calibration`：GFP/RFP 比值→MC-LR 浓度（传感器标定，4PL/非线性校准）；
  ③ `model_MC-LR_degradation_kinetics`：mlrA 降解率模型。当前只有①与②的独立存在，
  ②→① 的概率融合（把传感器浓度观测作为似然更新环境先验）未实现。
- 工程菌传感器阈值 1 µg/L 与 WHO 红线一致；但菌体批次漂移、荧光比例的非线性（0–10 µg/L 梯度）、
  6h 后荧光回落等湿实验特征（见项目简介 §6.4）也应进入 ② 的模型卡。

**决策**：① P0 定义场景化风险阈值配置并产出阈值指标；② P1 增加“OOD/低置信度 → 拒绝并建议采样”的
部署动作；③ 把 ②（传感器标定）与①的概率融合列为 P1 工程项（复现 `model_concentration_calibration`
的结果接口，再叠加 ③ 的降解动力学做“预警后残余风险”演示）。

---

## 附：31 轮审查总索引

| 轮次 | 类型 | 一句话结论 |
|---|---|---|
| R1–R8 | 设计迭代（ARCHITECTURE_ITERATIONS.md） | 从强基线→Hurdle→区间删失→多任务→挑战模型→域稳健→校准→CMADRE 定稿 |
| I0 | 训练迭代（迭代记录.md §2） | bloom 面板显著改善 MC-LR 但 TabM 尺度爆炸 |
| I1 | 训练迭代 §3 | 有界 sigma 消除数值爆炸；单独修复不够 |
| I2 | 训练迭代 §4 | distributional stacking + tail expert：主指标、最差来源、factor-of-2、q99 全面改善 |
| I3 | 训练迭代 §5/§8 | 完整非 IID 五折：I2 收益跨折一致；static 折方差过大归为低置信后备 |
| I4 | 训练迭代 §9 | tree-only 淘汰 stable-TabM；深度专家当前无可复现增量 |
| I5 + 种子 | 训练迭代 §10/§11 | log-blend 几何融合为 MC-LR 综合冠军；两个种子主指标一致 |
| R9 | 数据审计 | 53–54% 删失且全部有 LOD；total MC 无 >1000 极端值 |
| R10 | 数据审计 | MC-LR static 40% 行为“同站点同日”重复/近重复，有效样本量远小于行数 |
| R11 | 数据审计 | 321/319 条精确 0 疑似 ND 编码，需逐来源审计 |
| R12 | 基线门禁 | 同切分本地 RF 全面优于 v2 集成（total MC）；MC-LR 上 v2≈Dummy 但排序/区间有增量 |
| R13 | 深度模型审查 | 无掩码/无集成/无 μ 饱和的删失 MLP 跨来源外推灾难性失败 |
| R14 | 代码审查 | AFT 极端分布下“分位数近似 normal / 超限概率 logistic”不一致；scale 未调 |
| R15 | 代码审查 | 面板名一致但实际可用特征数任务不同（MC-LR core 实际 14 列） |
| R16 | 数据审查 | 特征—标签相关来源依赖强（Erie Chla 0.67 vs NRSA 0.15），禁止全数据解释 |
| R17 | 集成审查 | OOF 目标与单测试折结论冲突；log-blend 为主；删失感知 stacking 待做 |
| R18 | 校准审查 | CQR 仅精确标签+全局标量；coverage 1.0 由宽区间与少样本造成 |
| R19 | OOD 审查 | 99.3%/100% OOD 主要反映来源缺失模式；中国 42.5 万协变量零引用 |
| R20 | 评估审查 | 缺风险阈值指标/Brier/ECE/CRPS/interval score；风险阈值为空 |
| R21 | 任务边界 | 数据缺严格滞后序列，当前是 nowcast，预报任务归 P2 |
| R22 | 测量学审查 | Uruguay ADDA-ELISA 当量≠LC-MS/MS MC-LR；严格视图仅 444 行、排序仍弱 |
| R23 | 中国域审查 | 设计—实现最大差距：域分类器/密度比/预训练全未实现 |
| R24 | 部署审查 | 推断链路完整，但阈值、OOD 拒绝、传感器—环境概率融合未闭合 |
