# 无人值守运行总结（第三轮）

> 运行日期：2026-06-08
> 分支：model-redo-autonomous
> 运行范围：阶段 0 梳理 + 阶段 8 迭代优化 + GPT 审查

---

## 1. 完成的阶段

| 阶段 | 状态 | 关键产物 |
|------|------|---------|
| 0. 进度梳理 | ✅ | `reports/current_project_state.md` |
| 8. 模型迭代（3 轮） | ✅ | 15 个实验（EXP-001 到 EXP-015） |
| GPT 审查 | ✅ | Review 002 完成 |
| 创新探索笔记 | ✅ | `reports/innovation_exploration_notes.md` |
| 模型选择报告 | ✅ | `reports/model_selection_preliminary_report.md` |
| 无人值守总结 | ✅ | 本文件 |

## 2. Git 提交记录

| 提交 | 信息 |
|------|------|
| babee23 | docs: 梳理当前项目进度 |
| 26371d3 | feat: 实现增强版baseline训练（XGBoost/LightGBM+扩展特征集） |
| cb6a36e | feat: 迭代2-泄漏分析+LightGBM修复+特征选择实验 |
| 38297a5 | feat: 迭代3-跨数据集泛化+时间稳定性分析 |

## 3. 实验结果汇总

### 3.1 Lake Erie（总 MC 回归）

| 实验 | 描述 | 最佳模型 | R² | Spearman | WF2% |
|------|------|---------|---:|---------:|-----:|
| EXP-001 | baseline 10 特征 | Ridge | 0.063 | 0.687 | 31.6% |
| EXP-002 | 扩展 18 特征 | **RF** | **0.430** | **0.737** | **62.1%** |
| EXP-007 | 去掉蓝藻叶绿素 | Ridge | 0.384 | 0.709 | 33.0% |
| EXP-008 | 仅浮游植物 | XGB | 0.394 | 0.670 | 54.2% |
| EXP-015 | 时间外推 13-19→20-24 | RF | 0.439 | 0.760 | 62.3% |

### 3.2 HABs NLA（总 MC 回归）

| 实验 | 描述 | 最佳模型 | R² | Spearman | WF2% |
|------|------|---------|---:|---------:|-----:|
| EXP-003 | baseline 12 特征 | RF | 0.205 | 0.495 | 35.5% |
| EXP-004 | 扩展 26 特征 | **XGB** | **0.229** | **0.550** | **37.9%** |
| EXP-009 | 精选 15 特征 | RF | 0.178 | 0.505 | 35.5% |
| EXP-010 | N/P surplus | XGB | 0.212 | 0.507 | 37.5% |

### 3.3 EMLS MC-LR

| 实验 | 描述 | 最佳模型 | R² | Spearman | WF2% |
|------|------|---------|---:|---------:|-----:|
| EXP-005 | baseline 10 特征 | Ridge | 0.195 | 0.445 | 11.8% |
| EXP-006 | 扩展 27 特征 | Ridge | 0.110 | 0.336 | 11.8% |
| EXP-011 | Ridge alpha sweep | Ridge(a=10) | 0.165 | 0.394 | 11.8% |

### 3.4 跨数据集与时间稳定性

| 实验 | 描述 | 最佳 R² | 结论 |
|------|------|--------:|------|
| EXP-012 | HABs→Erie | 0.058 | 跨数据集失败 |
| EXP-013 | Erie→HABs | -19M | 灾难性失败 |
| EXP-014 | 合并训练 | 0.212 | 不如单独训练 |
| EXP-015 | 时间外推 | 0.439 | 时间稳定性好 |

## 4. 关键科学发现

1. **浮游植物分类叶绿素是 Erie MC 的最强预测因子**：添加后 R² 从 0.063 提升到 0.430。
2. **蓝藻叶绿素贡献约 0.15-0.26 R²**：去掉后 R² 降至 0.17-0.28。
3. **跨数据集泛化完全失败**：两个数据集的 MC-环境关系不可迁移。
4. **Erie 时间稳定性好**：R² 在 0.35-0.44 之间。
5. **HABs 特征工程改善有限**：R² 从 0.205 到 0.229。
6. **EMLS 树模型严重过拟合**：仅 Ridge 有效，但测试集仅 17 行。

## 5. GPT 审查关键反馈

### 5.1 总体判断

阶段 8 结果有审计价值，但不能支持"重建 MC-LR 模型"的主叙事。建议修改为：
"完成总 MC baseline 建模，MC-LR 可行性审计；当前尚不支持跨域部署。"

### 5.2 必须修改项

1. 修改项目主叙事
2. 建立数据集—目标变量合同
3. 重跑 HABs GroupKFold by DSGN_CYCLE
4. 分离 Erie A1（同步估计）/ A2（提前预测）版本
5. EMLS 零值 sensitivity 分析
6. 复核跨数据集 pipeline（R²=-19M 可能有 bug）

### 5.3 高风险点

1. 把同步估计包装成提前预测
2. 总 MC 与 MC-LR 标签混用
3. EMLS 测试集 17 行不稳定
4. 中国部署无证据链

## 6. 可信结论

1. Erie 总 MC 的 R²=0.43-0.44 在数据集内是可信的（含蓝藻叶绿素）。
2. 时间维度上 Erie 模型是稳定的（R²=0.35-0.44）。
3. 跨数据集泛化失败是可信的发现。
4. MC-LR 建模受样本量、零值、检测方法限制。
5. Decision 003 的任务拆分是正确方向。

## 7. 不可信结论

1. EMLS R²=0.20 — 测试集仅 17 行。
2. HABs R²=0.23 — 随机划分可能高估。
3. Erie R²=0.43 — 可能是同步估计而非预测。
4. 任何跨洲/跨场景的泛化声明。

## 8. 本轮新增文件

| 文件 | 说明 |
|------|------|
| `reports/current_project_state.md` | 项目进度报告 |
| `reports/enhanced_baseline_results.json` | 增强 baseline 结果 |
| `reports/iteration2_results.json` | 迭代 2 结果 |
| `reports/iteration3_results.json` | 迭代 3 结果 |
| `reports/model_selection_preliminary_report.md` | 模型选择报告 |
| `reports/innovation_exploration_notes.md` | 创新探索笔记 |
| `reports/gpt_review_packets/stage8_model_iteration_review_packet.md` | GPT 审查包 |
| `reports/gpt_responses/stage8_model_iteration_response.md` | GPT 审查回复 |
| `run_train_enhanced.py` | 增强训练脚本 |
| `run_iter2.py` | 迭代 2 脚本 |
| `run_iter3.py` | 迭代 3 脚本 |
| `memory/context_summary.md` | 上下文摘要 |

## 9. 需要用户人工检查

1. **是否接受 GPT 建议的叙事修改**：从"重建 MC-LR 模型"改为"总 MC baseline + MC-LR 可行性审计"
2. **蓝藻叶绿素的测量时间**：同步测量 = 泄漏；前置测量 = 合法特征
3. **是否继续投入 MC-LR 小样本建模**：369 行 + 54% 零值 = 非常困难
4. **跨数据集 R²=-19M 是否需要排查 bug**
5. **是否整合 EPA NLA 2017 数据**：已下载但未使用

## 10. 下一条建议 Prompt

```
继续 model-redo 项目。GPT 审查建议：
1. 修改项目主叙事（总 MC baseline + MC-LR 可行性审计）
2. 重跑 HABs GroupKFold by DSGN_CYCLE
3. 分离 Erie A1/A2 版本（同步估计 vs 提前预测）
4. EMLS 零值 sensitivity 分析
5. 排查跨数据集 pipeline bug（R²=-19M）
6. 整合 EPA NLA 2017 数据
请先确认用户是否接受叙事修改，然后按优先级执行。
```
