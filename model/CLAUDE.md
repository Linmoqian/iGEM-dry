# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

iGEM 蓝藻水华 (CyanoHABs) 预测模型项目。基于美国 EPA NLA 湖泊调查数据，构建 XGBoost + LightGBM 集成模型，预测微囊藻毒素 (MICX) 的检测概率和浓度。

双任务：分类 (MICX_DET 0/1) + 回归 (log10(MICX) μg/L)。

## 环境与命令

```bash
# 环境管理 (conda)
conda env create -f environment.yml
conda activate igem-cyanohab

# 数据清洗 (14 个数据集，线程池并行)
python run_clean.py

# 模型训练
python run_train.py                              # 默认: both tasks, ensemble
python run_train.py --task classification         # 仅分类
python run_train.py --task regression --seed 123  # 仅回归，自定义种子
python run_train.py --tune --n-trials 100         # 启用 Optuna 超参搜索

# 代码检查
ruff check src/ run_*.py
ruff format src/ run_*.py
```

## 架构

两阶段流水线，入口脚本各自独立：

**阶段 1 — 数据清洗**: `run_clean.py` → `src/datasets/*.py` (每数据集一个模块) → `src/clean.py` (共享工具) → `data/cleaned/*.parquet`

**阶段 2 — 模型训练**: `run_train.py` → `src/features.py` → `src/train.py` → `src/evaluate.py` → `src/interpret.py` → `models/*.joblib` + `figures/`

### 核心模块职责

| 模块 | 职责 |
|------|------|
| `src/config.py` | 路径常量、特征分组列名、`DatasetConfig` frozen dataclass |
| `src/clean.py` | 清洗原语: CSV 加载、负值修正、IQR 异常值裁剪、检测限替换、质量报告 |
| `src/features.py` | `build_feature_matrix(df, task)` → 唯一特征工程入口，返回 X, y, feature_names |
| `src/train.py` | XGBoost/LightGBM 训练、集成(概率平均)、5-fold CV、模型 save/load |
| `src/evaluate.py` | 分类/回归指标、阈值优化、混淆矩阵/ROC/PR/残差图 |
| `src/interpret.py` | SHAP TreeExplainer、蜂群图/柱状图/依赖图/瀑布图 |
| `src/logger.py` | Rich console 彩色日志 (绿=成功, 黄=警告, 红=错误) |

### 数据流

```
data/cleaned/v2_habs_training_cleaned.parquet (3,664 行 × 73 列)
  → features.py: 列筛选 (73→45), sin/cos 时间编码, one-hot
  → train.py: 分层 80/20 划分, XGBoost + LightGBM 独立训练
  → evaluate.py: 指标计算 + 诊断图表
  → interpret.py: SHAP 解释
  → models/*.joblib + figures/*
```

## 关键设计决策

- **树模型原生处理 NaN**: 不做缺失值填充，XGBoost/LightGBM 学习最优分裂方向
- **MICX 66% 缺失**: 分类用全量 3,663 行 (MICX_DET)，回归仅用 1,241 行 (MICX 非 null)
- **N/P 预算列精简**: 26 列 → 7 列代表，消除 r>0.7 多重共线性
- **回归目标**: log10(MICX)，原始偏度 15.4 → 对数后 1.09
- **特征分组定义**: `src/config.py` 中模块级常量，非 YAML/JSON 配置

## 注意事项

- matplotlib 中文字体已配置为 Microsoft YaHei，`plt.style.use()` 会在函数内重置字体配置，避免在函数内重复调用
- XGBoost ≥3.0 中 `early_stopping_rounds` 在构造函数而非 `fit()` 中设置
- 所有用户面向的日志、图表标签、报告均使用中文
- 新增数据集时，在 `src/datasets/` 下创建对应模块并实现 `clean()` 函数，在 `config.py` 的 `get_v2_configs()` 中注册
