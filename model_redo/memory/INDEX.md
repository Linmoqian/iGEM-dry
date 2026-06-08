# memory/INDEX.md

## 当前阶段

阶段 0-8 全部完成（含 3 轮迭代）。GPT Review 002 已完成。详见 `reports/autonomous_run_summary.md`。

## 项目目标

重建微囊藻毒素浓度预测模型。

**任务定义（Decision 003）：**
- 任务 A（主）：总 microcystins 浓度回归
- 任务 B：MC-LR 小样本验证
- 任务 C：中国场景迁移

**GPT 建议修改主叙事：**
"完成总 MC baseline 建模，MC-LR 可行性审计；当前尚不支持跨域部署。"

## 最新结果（迭代 3）

| 任务 | 数据集 | 最佳模型 | R² | 可信度 |
|------|--------|---------|---:|--------|
| A | Erie (含BG chla) | RF | 0.43 | 中（泄漏风险） |
| A | Erie (不含BG chla) | Ridge | 0.17-0.38 | 中-高 |
| A | HABs NLA | XGBoost | 0.23 | 中（需GroupKFold） |
| B | EMLS MC-LR | Ridge | 0.20 | 低（17行测试） |
| - | 跨数据集 | - | 失败 | 可能有bug |

## 关键文件

- `CLAUDE.md` — 项目规则
- `memory/old_model_lessons.md` — 旧模型审计
- `memory/decisions.md` — 4 个决策（001-003 + 任务修改）
- `memory/gpt_review_log.md` — 2 次 GPT 审查
- `memory/context_summary.md` — 上下文摘要
- `memory/experiment_log.jsonl` — 实验日志（EXP-001 到 EXP-015）
- `reports/autonomous_run_summary.md` — 无人值守总结
- `reports/model_selection_preliminary_report.md` — 模型选择报告
- `reports/enhanced_baseline_results.json` — 增强 baseline 结果
- `reports/iteration2_results.json` — 迭代 2 结果
- `reports/iteration3_results.json` — 迭代 3 结果
- `reports/gpt_responses/stage8_model_iteration_response.md` — GPT 审查回复

## 运行脚本

- `run_audit.py` — 数据审计
- `run_clean.py` — 清洗流水线
- `run_split.py` — 数据划分
- `run_train.py` — 原 baseline（Dummy/Ridge/RF）
- `run_train_enhanced.py` — 增强 baseline（+XGB/LGBM/扩展特征）
- `run_iter2.py` — 迭代 2（泄漏分析+特征选择）
- `run_iter3.py` — 迭代 3（跨数据集+时间稳定性）

## 待办（用户回来后）

1. ⬜ 确认是否接受 GPT 建议的叙事修改
2. ⬜ 确认蓝藻叶绿素测量时间
3. ⬜ 重跑 HABs GroupKFold by DSGN_CYCLE
4. ⬜ 分离 Erie A1/A2 版本
5. ⬜ EMLS 零值 sensitivity 分析
6. ⬜ 跨数据集 pipeline bug 审计
7. ⬜ 整合 EPA NLA 2017 数据
8. ⬜ 安装 pyarrow
