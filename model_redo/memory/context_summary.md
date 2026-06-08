---
name: context-summary
description: 项目上下文摘要 — 当前阶段、已确认事实、风险和下一步
metadata:
  type: project
---

# 上下文摘要

> 更新日期：2026-06-08
> 更新触发：完成 2 个阶段 + 与 GPT 交流 2 次 + 产生超过 5 个 commit

## 1. 当前阶段

阶段 8（模型迭代）已完成 3 轮迭代。GPT 审查已完成（Review 002）。

## 2. 已确认事实

1. 本地数据仅 EMLS 有 MC-LR（369 行），不足以独立建模。
2. 总 MC 数据充足（Erie 3,074 + HABs 3,664 = 6,738 行）。
3. 任务已拆分为三层（Decision 003）：A=总 MC，B=MC-LR，C=中国场景。
4. Erie 扩展特征后 R² 从 0.063 提升到 0.43-0.44（RF），蓝藻叶绿素是关键特征。
5. 去掉蓝藻叶绿素后 R² 降至 0.17（泄漏风险量化）。
6. HABs XGBoost R²=0.23，特征工程改善有限。
7. EMLS Ridge R²=0.20，测试集仅 17 行，结果不可信。
8. 跨数据集泛化失败：HABs→Erie R²=0.06，Erie→HABs R²=-19M。
9. Erie 时间稳定性好：不同时间划分 R² 在 0.35-0.44。
10. Python 3.12.5，XGBoost 3.1.3，LightGBM 4.6.0 均可用。

## 3. 未确认假设

1. 蓝藻叶绿素是否与 MC 同步测量（泄漏 vs 合法预测特征）。
2. HABs R²=0.23 是否因随机划分而高估。
3. EMLS 零值是否为 <LOD。
4. 跨数据集 R²=-19M 是否为工程 bug。
5. 总 MC 模型对 MC-LR 预测的实际价值。

## 4. 当前数据状态

- 清洗后数据：erie_clean.pkl (3,074), habs_nla_clean.pkl (3,664), emls_clean.pkl (369), ncca2015_clean.pkl (592)
- 外部数据：EPA NCCA 2015 (已下载), EPA NLA 2017 (已下载，未整合)
- 划分：split_manifest.json 已生成

## 5. 当前建模状态

- 最佳 Erie 模型：RF R²=0.43（含蓝藻叶绿素）/ 0.17（不含）
- 最佳 HABs 模型：XGBoost R²=0.23
- 最佳 EMLS 模型：Ridge R²=0.20（不可信）
- LightGBM 有特殊字符 bug 未完全修复

## 6. 当前最可信指标

- Erie RF R²=0.43-0.44（含泄漏风险标记）
- Erie 时间外推 R²=0.35-0.44
- HABs XGBoost R²=0.23

## 7. 当前不可信指标

- EMLS R²=0.20（17 行测试集）
- 跨数据集任何 R²（可能有工程 bug）
- HABs 随机划分 R²（未做 GroupKFold）

## 8. 主要风险

1. 把同步估计包装成提前预测（GPT 最高风险）
2. 总 MC 与 MC-LR 标签混用
3. EMLS 零值处理不当
4. 跨数据集 pipeline 可能有 bug
5. 中国部署无证据链

## 9. 最近 GPT 反馈摘要

Review 002（2026-06-08）：
- 不支持"重建 MC-LR 模型"的主叙事
- 建议修改为"总 MC baseline + MC-LR 可行性审计"
- 必须重跑 HABs GroupKFold
- 必须分离 Erie A1/A2 版本
- EMLS 必须做零值 sensitivity 分析
- 跨数据集失败先查 bug

## 10. 下一步建议

1. 做数据与任务审计表
2. 重跑验证矩阵（GroupKFold、时间划分）
3. Erie A1/A2 版本分离
4. EMLS 零值 sensitivity 分析
5. 跨数据集 pipeline 审计
6. 更新项目主叙事

## 11. 用户回来后必须检查的问题

1. 是否接受 GPT 建议的项目叙事修改？
2. 蓝藻叶绿素的测量时间确认？
3. 是否继续投入更多时间做 MC-LR 小样本建模？
4. 是否接受"总 MC 为主任务"的结论？
