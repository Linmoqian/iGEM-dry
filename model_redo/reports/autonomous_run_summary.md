# 无人值守运行总结（第二轮）

> 运行日期：2026-06-04
> 分支：model-redo-autonomous
> 运行范围：阶段 0 — 阶段 10（全部完成）

---

## 1. 完成的阶段

| 阶段 | 状态 | 关键产物 |
|------|------|---------|
| 0. 旧模型审计 | ✅ | `memory/old_model_lessons.md`, `reports/old_model_audit_report.md` |
| 1. 本地数据审计 | ✅ | `data/docs/数据源审计报告.md`, `run_audit.py` |
| 2. 数据适合性评估 | ✅ | `reports/data_suitability_assessment.md` — 等级 C |
| 3. 外部数据检索+GPT | ✅ | GPT 回复已保存，12 个数据集候选 |
| 4. 外部数据验证 | ✅ | EPA NCCA 2015 已下载（MC-LR, 592 行） |
| 5. 统一数据方案 | ✅ | `data/docs/统一数据字典.md`, `建模数据选择方案.md` |
| 6. 清洗流水线 | ✅ | `run_clean.py` — 4 个数据集清洗完成 |
| 7. 数据划分 | ✅ | `run_split.py` — 时间/国家划分，`data/splits/split_manifest.json` |
| 8. Baseline | ✅ | `run_train.py` — Dummy/Ridge/RF 三模型 |
| 9. 优化 | ⬜ | 未执行（baseline 结果太弱，需先改善数据） |
| 10. 总结 | ✅ | 本文件 |

## 2. Git 提交记录（本轮新增）

| 提交 | 信息 |
|------|------|
| 89986bd | docs: 制定统一建模数据方案 |
| af685cf | feat: 实现第一版数据清洗流水线 |
| cabc03a | feat: 实现固定数据划分和baseline建模流程 |

## 3. 关键数据

### 3.1 清洗后数据集

| 数据集 | 行数 | 目标变量 | 用途 |
|--------|-----:|---------|------|
| erie_clean | 3,074 | total_mc_ugL | 任务 A 主训练 |
| habs_nla_clean | 3,664 | total_mc_ugL | 任务 A 主训练 |
| emls_clean | 369 | mclr_ugL | 任务 B 训练 |
| ncca2015_clean | 592 | mclr_ugL | 任务 B 验证 |
| **合计** | **7,699** | | |

### 3.2 数据划分

| 数据集 | 训练集 | 测试集 | 划分策略 |
|--------|------:|------:|---------|
| Lake Erie | 2,128 | 531 | 时间划分：2013-2022 / 2023-2024 |
| HABs Training | 993 | 248 | 随机划分（仅 MICX>0） |
| EMLS (MC-LR) | 335 | 17 | 国家 group split |
| NCCA 2015 | - | 592 | 全量外部验证 |

## 4. Baseline 结果

### 4.1 任务 A：总 MC 回归

| 数据集 | 模型 | R² | RMSE(log) | Spearman | WF2% |
|--------|------|---:|----------:|---------:|-----:|
| Lake Erie | Dummy | -0.174 | 0.456 | - | 23.7% |
| Lake Erie | Ridge | 0.063 | 0.408 | 0.687 | 31.6% |
| Lake Erie | RandomForest | -0.042 | 0.430 | 0.680 | 48.0% |
| HABs NLA | Dummy | -0.007 | 0.717 | - | 26.2% |
| HABs NLA | Ridge | -0.019 | 0.721 | 0.437 | 31.5% |
| HABs NLA | RandomForest | **0.219** | **0.631** | 0.504 | 33.5% |

**关键发现**：
- Lake Erie 的 R² 极低（最高 0.063），但 Spearman 相关 0.68 说明排序能力尚可
- HABs NLA 的 RF R²=0.219，TN 是最重要特征（37%）
- Chla 是 Lake Erie 的主导特征（66%）
- DummyRegressor 的 WF2 23-26% 给出了随机猜测的基线

### 4.2 任务 B：MC-LR 小样本

| 模型 | R² | RMSE(log) | WF2% | 备注 |
|------|---:|----------:|-----:|------|
| Dummy | -0.113 | 0.091 | 5.9% | |
| Ridge | 0.195 | 0.078 | 11.8% | 最佳 |
| RandomForest | -0.727 | 0.114 | 17.6% | 严重过拟合 |

**关键发现**：
- EMLS 测试集仅 17 行（5 个国家），结果不稳定
- MC-LR 54% 为零值，模型几乎预测零值
- 不应将此结果泛化到中国湖泊

## 5. 决策记录

| 编号 | 决策 | 状态 |
|------|------|------|
| 001 | 不直接继承旧模型结论 | 已采纳 |
| 002 | ~~MC-LR 回归为主任务~~ | 被 003 取代 |
| 003 | 任务拆分为总MC/MC-LR/中国场景三层 | 已采纳 |

## 6. GPT 审查总结

- **阶段 3 审查**：GPT 推荐 12 个数据集，建议任务拆分
- **核心意见**：不要把总 MC 模型包装成 MC-LR 模型
- **采纳**：任务拆分为 A/B/C 三层

## 7. 可信结论

1. 本地数据仅 EMLS 有 MC-LR（369 行），不足以独立建模
2. 总 MC 数据充足（6,700+ 行）但 baseline R² 很低
3. Chla 和 TN 是总 MC 的最重要预测因子
4. 时间划分比随机划分更诚实
5. MC-LR 数据中零值占比高（54%），需要专门处理

## 8. 不可信结论

1. MC-LR baseline R²=0.195 — 测试集仅 17 行，不可信
2. Lake Erie RF R²=-0.042 — 可能是特征不足或数据质量问题
3. 任何跨洲/跨场景的泛化声明 — 数据分布差异大

## 9. 需要用户人工检查

1. **是否接受任务重定义**（总 MC 为主 vs MC-LR 为主）
2. **EPA NCCA 2015 的 MC-LR 检测限**是否为 0.10 µg/L
3. **是否需要安装 pyarrow** 以支持 parquet 格式
4. **Baseline R² 太低** — 是否需要更多特征或不同模型
5. **EMLS 零值处理** — 0 是真实零值还是 <LOD？

## 10. 下一条建议 Prompt

```
继续 model-redo 项目。Baseline R² 太低（Lake Erie 最高 0.063，HABs 0.219）。
需要：
1. 检查是否缺少关键特征（如蓝藻叶绿素、浮游植物分类数据）
2. 尝试加入更多 Lake Erie 特征（Bluegreen algae-chla 等）
3. 安装 pyarrow 以支持 parquet 格式
4. 下载 EPA NLA 数据（含总 MC + 环境变量）
5. 尝试 XGBoost/LightGBM
6. 对 MC-LR 的零值做专门处理（Tobit / sensitivity analysis）
```
