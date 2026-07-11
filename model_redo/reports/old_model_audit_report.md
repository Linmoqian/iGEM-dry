# 旧模型审计报告

> 阶段 0 — 旧模型审计  
> 生成日期：2026-06-04  
> 审计范围：`model/` 目录全部代码、配置、数据清洗逻辑、特征工程、模型训练、评估指标  
> 审计方式：逐文件只读审查，不执行代码，不修改旧项目

---

## 一、审计目标

1. 摸清旧项目的完整数据管线
2. 识别旧项目的可复用经验与潜在风险
3. 为 `model_redo/` 的数据审计和模型设计提供基础

## 二、旧项目架构概览

```
model/
├── run_clean.py          # 数据清洗入口：并行调度 11 个清洗器
├── run_train.py          # 训练入口：加载数据 → 特征 → 训练 → 评估 → SHAP
├── environment.yml       # Python 3.11, XGBoost≥2.0, LightGBM≥4.0, SHAP≥0.44
├── src/
│   ├── config.py         # 路径、特征分组、目标列、数据集注册表
│   ├── clean.py          # 通用清洗工具函数（18 个）
│   ├── features.py       # 特征构建（按数据集分派）
│   ├── train.py          # XGBoost/LightGBM 训练、集成、交叉验证
│   ├── evaluate.py       # 指标计算 + 可视化
│   ├── interpret.py      # SHAP 解释
│   ├── logger.py         # Rich 日志
│   └── datasets/         # 11 个数据集专属清洗器
├── data/cleaned/         # 14 个 parquet + 对应 JSON 报告
├── figures/              # 评估图 + SHAP 图
├── reports/              # 评估报告
└── 模型报告.md           # 中文综合报告
```

## 三、数据源审计

### 3.1 原始数据来源

| # | 数据集名 | 来源 | 地理范围 | 时间跨度 | 清洗后行数 | 目标列 | 是否含 MC-LR |
|---|---------|------|---------|---------|----------|--------|------------|
| 1 | habs_training | EPA NLA 2007/2012/2017 | 美国全国 | 2007-2017 | 3,664 | MICX_DET / MICX | 否，总 MC |
| 2 | lake_erie | Lake Erie 全湖采样 | 伊利湖 | 2013-2025 | 3,074 | Total Microcystins | 否，总 MC |
| 3 | sf_estuary | SF Estuary 监测 | 旧金山河口 | 2014-2019 | 438 | ucd.ppia.MC.total.ugL | 否，PPIA 总 MC |
| 4 | emls_europe | EMLS | 欧洲 27 国 | 2015 夏 | 369 | 微囊藻毒素各变体 | 含 MC-LR 变体列 |
| 5 | gull_lake | KBS LTER | 密歇根 | 1998-2014 | 13 | microcystin_ug_l | 不确定 |
| 6 | cleo | CLEO 公民科学 | 康涅狄格 | 2015-2018 | 189 | toxin_level (1-4) | 否，半定量等级 |
| 7 | v2_esp_sensor | ESP 传感器 | 伊利湖 | 2024.7-9 | 140 | MC ug L-1 | 否，总 MC |
| 8 | v2_sb_weekly | SB 周监测 | 萨吉诺湾 | 2024.5-10 | 87 | Particulate/Dissolved MC | 不确定亚型 |
| 9 | v2_habs_prediction | EPA NLA 2017 | 全美 | 2017 | 124,529 | 无 MC 目标 | N/A |
| 10 | v2_erie_summary | Erie 汇总 | 伊利湖 | 2008-2017 | 1,488 | Microcystin 列 | 否，总 MC |
| 11-14 | v2_mc_*/v2_mix_* | EPA Virtual Beach | 明尼苏达 | 2016-2017 | 各 50 | MC/MIX 综合 | 含 MC 数据 |

### 3.2 数据源关键发现

**F-1**：全部已注册训练的数据集（#1-3）的 MC 数据均为"总微囊藻毒素"，**不含 MC-LR 亚型专属测量**。

**F-2**：emls_europe 含 MC 变体列（包括 MC-LR），但未被注册训练。369 行、MC-LR 缺失率 ~5%。

**F-3**：检测方法不统一——NLA 用 ELISA，Lake Erie 混合方法，SF Estuary 用 PPIA，CLEO 用半定量试纸。

**F-4**：跨数据集的营养盐单位不统一（μmol/L vs mg/L），代码中未做单位转换。

**F-5**：habs_training 的 MICX 缺失率 66%（仅 1,241/3,664 行有浓度值），严重影响回归任务。

## 四、清洗逻辑审计

### 4.1 清洗策略总表

| 策略 | 实现函数 | 适用场景 | 备注 |
|------|---------|---------|------|
| 检测限半值替换 | `replace_detection_limits(strategy="half")` | `<0.15` 等 | 统计学惯例 |
| 检测限→NaN | `replace_detection_limits(strategy="nan")` | `bdl`/`nd`/`<LLOD` | 与半值策略不一致 |
| 哨兵值→NaN | `replace_sentinel_values()` | `-1000` | habs_prediction 专用 |
| 负值→NaN | `fix_negative_values()` | field.NTU | 合理 |
| IQR 标记 | `clip_outliers_iqr()` | 极端值 | 只标记不删除 |
| 质控行移除 | `remove_quality_control_rows()` | FieldCont | SF Estuary 专用 |
| 拼写修正 | `fix_country_names()` | FR→France |  |
| 高缺失列删除 | `drop_high_missing_columns()` | ≥55% 缺失 | 硬编码阈值 |
| 多行表头合并 | `parse_multirow_header_csv()` | Erie 汇总 | 7 行表头 |

### 4.2 清洗逻辑关键问题

**F-6**：检测限处理策略不一致——Lake Erie 的 Total MCs 用半值替换（0.075），ESP 传感器的 MC 用 NaN 替换。同一项目中对同一类型标记采用不同策略，引入了系统性偏差。

**F-7**：无显式字段映射表。各数据集直接使用原始列名，不同数据集的同义字段名称不同（如 NTL vs TN，TURB vs Turbidity）。

**F-8**：无单位换算逻辑。habs_training 的营养盐为 mg/L，Lake Erie 为 μmol/L，跨数据集比较需要转换单位但代码中缺失。

**F-9**：无缺失机制分析。代码对所有 NaN 一视同仁交由树模型处理，未区分 MCAR、MAR 和 MNAR（MC 未检出是 MNAR 的典型情况）。

**F-10**：无去重逻辑。habs_training 同一湖泊在不同调查年份重复出现，代码通过 DSGN_CYCLE 分层但未讨论样本独立性。

## 五、目标变量审计

### 5.1 分类目标

| 数据集 | 定义 | 阈值 | 正类比例 |
|--------|------|------|---------|
| habs_training | MICX_DET | 已有 0/1 标签 | 34% |
| lake_erie | Total MCs > 0.15 μg/L | 0.15 | ~70% |
| sf_estuary | PPIA MC > 0 | 0 | ~60% |

**F-11**：分类阈值不统一。habs_training 用 EPA 的检测标准，lake_erie 用 0.15 μg/L（EPA 饮用水标准的一部分），sf_estuary 用 >0。这使得跨数据集的分类任务含义不同。

### 5.2 回归目标

| 数据集 | 定义 | 有效样本 | 浓度范围 |
|--------|------|---------|---------|
| habs_training | log10(MICX), 仅 MICX>0 | 1,241 | 0.1-225 μg/L |
| lake_erie | log10(Total MCs), 仅 >0 | 2,626 | 检测限-数百 μg/L |
| sf_estuary | log10(PPIA MC), 仅 >0 | 154 | 检测限-~20 μg/L |

**F-12**：回归任务丢弃了所有未检出样本。对 habs_training 来说，66% 的数据被丢弃。这意味着模型只能在"已确认有毒"的样本上训练，无法处理"毒素是否会出现"的问题。

**F-13**：log10 变换后偏度从 15.4 降至 1.09，变换合理。但零值和未检出值的处理需要改进。

## 六、特征工程审计

### 6.1 habs_training 特征（45 个）

| 特征组 | 特征数 | 代表变量 |
|--------|--------|---------|
| 水质 | 12 | TEMPERATURE, PH, CHLA_RESULT, NTL, PTL, DO_SURF, TURB |
| 气候 | 4 | EVAP_INFL, D_EXCESS, precip/temp_mean_month |
| 土地利用 | 3 | agr_ws, dev_ws, fst_ws |
| 地形 | 7 | lakemorpho_fetch, BFIWs, SlopeWs, ElevWs |
| N 预算 | 4 | N_Surplus, N_Total_Inputs, N_Fert_Farm, N_livestock_Waste |
| P 预算 | 3 | P_Surplus, P_f_fertilizer, P_human_waste_kg |
| 聚合输入 | 4 | n/p_farm_inputs, n/p_dev_inputs |
| 位置 | 2 | LAT_DD83, LON_DD83 |
| 衍生 | 3 | MONTH_sin, MONTH_cos, P_Legacy_P_outlier |
| One-hot | 3 | AG_ECO3_xxx |

### 6.2 Lake Erie 特征（23 个）

水深、透明度、水温、总叶绿素、蓝藻/绿藻/硅藻/隐藻叶绿素、硝酸盐、铵盐、亚硝酸盐、DRP、硅酸盐、TP、TKN、TN、TN:TP、黄物质、经纬度、月份编码。

### 6.3 SF Estuary 特征（25 个）

水温、DO、电导率、盐度、浊度、pH、NH4、NO3、Cl、DOC、TOC、DON、SRP、TP、SiO2、VSS、TDS、TSS、Chla、Pheo、qPCR total MIC、经纬度、月份编码。

### 6.4 信息泄漏风险

**F-14（高风险）**：Lake Erie 的"蓝藻叶绿素"SHAP 值 0.872，远超其他特征。如果该特征与 MC 是同一次采样事件中同步测量的，在实际部署场景（预测未来的 MC）中该特征不可用。这构成**条件信息泄漏**。

**F-15（高风险）**：SF Estuary 的"qPCR total MIC"是蓝藻毒素基因的定量 PCR 检测结果，与目标变量（MC 毒素浓度）几乎是同一信息的不同测量方式。如果测量时间与 MC 相同，属于典型的信息泄漏。

**F-16（低风险）**：habs_training 的 CHLA_RESULT（叶绿素 a）与 MC 在同一采样事件中测量，但叶绿素 a 测量通常先于 MC 分析，且在实际部署中可实时获取，泄漏风险较低。

## 七、模型方法审计

### 7.1 训练配置

- XGBoost：500 棵树，max_depth=5，lr=0.05，early_stopping=50
- LightGBM：500 棵树，max_depth=5，num_leaves=31，lr=0.05
- 集成方式：简单概率/预测值平均
- 数据划分：80/20 随机划分，按 DSGN_CYCLE × 目标联合分层
- 交叉验证：5-fold stratified CV

### 7.2 关键问题

**F-17**：无 baseline 对照。没有均值预测、逻辑回归、线性回归等简单模型作为比较基准。

**F-18**：集成策略过于简单。简单平均不一定优于单模型。在 sf_estuary 上，Ensemble 的分类 AUC（0.811）反而低于 LightGBM 单模型（0.973 全量 / 0.906 测试 XGBoost）。

**F-19**：`--tune`（Optuna 超参搜索）参数已预留但主流程未使用。超参为手工设置。

**F-20**：所有验证都是随机划分，无时间外推和站点外推。对时间序列数据和空间数据来说，随机划分会高估模型泛化能力。

**F-21**：小数据集（<500 行）自动切换保守参数是合理设计。但 sf_estuary 的保守参数仍不足以防止 LightGBM 过拟合。

## 八、评估指标审计

### 8.1 指标体系

- 分类：ROC-AUC、PR-AUC、Accuracy、Balanced Accuracy、F1、MCC、Precision、Recall ✓
- 回归：RMSE(log)、RMSE(orig)、MAE(orig)、R2、Pearson r、Spearman rho、Within-Factor-of-2 ✓

### 8.2 关键问题

**F-22**：`find_optimal_threshold()` 函数存在但未被主流程调用。混淆矩阵始终使用 0.5 固定阈值。

**F-23**：SHAP 解释只对 `models[0]`（XGBoost）做，不代表集成模型整体。且分类和回归的 SHAP 文件在同一目录下同名，后运行的会覆盖先运行的。

**F-24**：无预测不确定性量化。回归只输出点估计，无置信区间或预测区间。

## 九、可复用经验总结

| 编号 | 经验 | 来源 | 新版可用度 |
|------|------|------|----------|
| E-1 | 通用清洗工具函数（检测限、哨兵值、IQR 标记） | clean.py | 高，直接复用逻辑 |
| E-2 | 特征分组体系（水质/气候/土地利用/地形/营养盐） | config.py | 高，可扩展 |
| E-3 | MONTH_sin/cos 时间周期编码 | features.py | 高，所有数据集有效 |
| E-4 | log10 变换处理 MC 浓度偏度 | features.py | 高，标准做法 |
| E-5 | 树模型原生处理 NaN | train.py | 中，需配合缺失率分析 |
| E-6 | 数据集注册表设计 | config.py | 高，便于扩展 |
| E-7 | SHAP 全流程解释 | interpret.py | 高，标准实践 |
| E-8 | 数据质量报告自动生成 | clean.py | 高 |
| E-9 | 小样本保守参数策略 | train.py | 中，仍需改进 |
| E-10 | 叶绿素/NTL/pH/水温是 MC 通用预测因子 | SHAP 结果 | 高，但需验证泄漏 |

## 十、不应直接继承的结论

| 编号 | 问题 | 风险等级 |
|------|------|---------|
| R-1 | 旧模型预测"总 MC"而非 MC-LR | 高 |
| R-2 | 回归任务丢弃 66% 未检出样本 | 高 |
| R-3 | 蓝藻叶绿素/qPCR 特征可能存在信息泄漏 | 高 |
| R-4 | 随机划分验证高估泛化能力 | 高 |
| R-5 | 无 baseline，无法评估模型增量价值 | 中 |
| R-6 | 跨数据集检测方法和单位不统一 | 中 |
| R-7 | 集成策略简单平均可能弱于单模型 | 低 |
| R-8 | 分类阈值固定 0.5 而非优化 | 低 |

## 十一、对新版项目的建议

### 11.1 数据层面

1. **寻找含 MC-LR 亚型数据的数据源**，或明确将目标定义为"总 MC"
2. **不要丢弃未检出样本**，将 <LOD 视为左截尾数据
3. **统一检测方法和单位**，或在模型中引入检测方法作为特征
4. **分析缺失机制**，区分 MCAR（随机缺失）和 MNAR（未检出）

### 11.2 验证层面

5. **建立 baseline**：均值预测、线性回归、简单决策树
6. **做时间外推验证**：按年份切分 train/val/test
7. **做站点外推验证**：按湖泊/站点 group split
8. **用 locked_test 做最终验收**，不用于模型选择

### 11.3 特征层面

9. **严格检查信息泄漏**：明确每个特征的测量时间是否先于 MC
10. **构建生态学有意义的交互特征**：TN:TP 比、温度×营养盐
11. **考虑特征可用性**：部署时能实时获取哪些特征

### 11.4 模型层面

12. **主任务是回归**，分类只是辅助
13. **先用简单 baseline，再用复杂模型**
14. **尝试加权集成或 stacking 替代简单平均**
15. **输出预测区间**而非仅点估计

---

## 附录：审计中发现的所有文件清单

### 核心代码（8 个 .py）
- `src/config.py` — 228 行
- `src/clean.py` — 242 行
- `src/features.py` — 348 行
- `src/train.py` — 310 行
- `src/evaluate.py` — 572 行
- `src/interpret.py` — 328 行
- `src/logger.py` — 31 行
- `src/datasets/__init__.py` — 空

### 数据集清洗器（11 个 .py）
- `src/datasets/sf_estuary.py` — 39 行
- `src/datasets/emls_europe.py` — 28 行
- `src/datasets/gull_lake.py` — 22 行
- `src/datasets/cleo.py` — 26 行
- `src/datasets/v2_lake_erie.py` — 57 行
- `src/datasets/v2_esp_sensor.py` — 36 行
- `src/datasets/v2_sb_weekly.py` — 43 行
- `src/datasets/v2_habs_prediction.py` — 36 行
- `src/datasets/v2_habs_training.py` — 30 行
- `src/datasets/v2_erie_summary.py` — 49 行
- `src/datasets/v2_toxin_models.py` — 34 行

### 入口脚本（2 个 .py）
- `run_clean.py` — 98 行
- `run_train.py` — 227 行

### 配置和文档
- `environment.yml` — Python 3.11 conda 环境
- `README.md` — 空
- `TODO.md` — 全部打勾
- `模型报告.md` — 488 行中文综合报告
- `reports/dataset_evaluation_report.md` — 三数据集评估报告
- `data/docs/数据清洗报告.md` — 详细清洗日志
- `data/docs/数学建模报告.md` — 建模技术报告
