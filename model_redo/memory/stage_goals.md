# stage_goals.md

本文件记录 Claude Code 分阶段 `/goal` 模板。

不要一次性设置"完成整个模型重建"的巨大目标。必须分阶段推进。

---

## Goal 0：旧模型审计

```text
/goal 审计旧项目 `model/`，不得修改旧项目。总结旧模型的数据来源、清洗逻辑、目标变量、模型方法、评估指标、可复用经验和潜在问题。输出以下文件：

1. `model_redo/memory/old_model_lessons.md`
2. `model_redo/reports/old_model_audit_report.md`
3. 更新 `model_redo/memory/INDEX.md`
4. 更新 `model_redo/memory/decisions.md`

完成后，必须生成一份发给 GPT 的 review packet，并使用固定 GPT 审查模板请求查收。

本阶段禁止事项：

1. 不得训练模型。
2. 不得修改旧项目 `model/`。
3. 不得删除或移动任何原始数据。
4. 不得直接复制旧项目代码到 `model_redo/`。
5. 不得下结论说旧模型结果可以直接继承。

完成标准：

1. 已明确旧模型是分类、回归还是混合任务。
2. 已明确旧模型使用了哪些数据源。
3. 已指出旧模型中可复用和不可复用的部分。
4. 已指出数据泄漏、指标不匹配、任务定义不清等潜在风险。
5. 已向 GPT 提交审查，并记录 GPT 反馈。
```

---

## Goal 1：原始数据审计

```text
/goal 审计 `model_redo/data/raw/` 中所有原始数据文件，识别包含 MC-LR 浓度的数据源、字段含义、单位、缺失率、异常值、时间字段和空间字段。生成以下文件：

1. `data/docs/数据源审计报告.md`
2. `data/docs/数据字典.md`
3. `data/docs/变量单位说明.md`
4. 更新 `memory/INDEX.md`
5. 更新 `memory/decisions.md`

完成后，必须生成发给 GPT 的 review packet，并记录 GPT 审查意见。

本阶段禁止事项：

1. 不得训练模型。
2. 不得删除、覆盖或移动 `data/raw/` 中任何文件。
3. 不得擅自丢弃数据源。
4. 不得直接认定旧模型的数据处理方式可继承。

完成标准：

1. 已列出所有原始数据文件。
2. 已识别哪些数据包含 MC-LR 浓度字段。
3. 已识别目标变量单位与潜在单位混乱问题。
4. 已识别时间字段、空间字段和主要环境变量。
5. 已指出不能用于建模或需要进一步确认的数据源。
```

---

## Goal 2：数据清洗

```text
/goal 基于数据审计报告完成第一版数据清洗流水线，生成清洗配置、清洗脚本和清洗后数据。输出以下文件：

1. `src/clean.py`
2. `src/schema.py`
3. `configs/cleaning.yaml`
4. `data/cleaned/main_cleaned.parquet`
5. `data/docs/数据清洗报告.md`
6. 更新 `memory/INDEX.md`
7. 更新 `memory/decisions.md`

完成后，必须向 GPT 提交清洗逻辑 review packet。

本阶段禁止事项：

1. 不得删除原始数据。
2. 不得在没有说明理由的情况下删除样本。
3. 不得在清洗中引入目标泄漏。
4. 不得把未来信息加入当前样本特征。

完成标准：

1. 已说明字段映射规则。
2. 已说明单位转换规则。
3. 已说明缺失值处理规则。
4. 已说明异常值处理规则。
5. 已说明重复样本处理规则。
6. 已输出清洗后数据和清洗报告。
```

---

## Goal 3：数据划分

```text
/goal 在完成数据清洗后，设计并固定数据划分方案。至少包含 random split、time-based split 和 site-based split 的可行性判断。输出：

1. `src/split.py`
2. `configs/split.yaml`
3. `data/splits/` 下的划分文件
4. `tests/test_split.py`
5. `tests/test_no_leakage.py`
6. 更新 `memory/INDEX.md`
7. 更新 `memory/decisions.md`

完成后，必须向 GPT 提交数据划分 review packet。

本阶段禁止事项：

1. 不得使用 locked_test 做模型选择。
2. 不得让同一站点、同一时间段的高度相关样本泄漏到训练和测试中而不说明。
3. 不得只使用随机划分就宣称模型有泛化能力。

完成标准：

1. 已固定训练集、验证集、测试集。
2. 已说明每种划分回答的科学问题。
3. 已说明 locked_test 使用规则。
4. 已加入防泄漏检查。
```

---

## Goal 4：baseline 建模

```text
/goal 在固定数据划分的基础上完成第一版 MC-LR 浓度回归 baseline。至少包含 DummyRegressor、Ridge 或 ElasticNet、RandomForest、XGBoost、LightGBM。输出：

1. `src/train.py`
2. `src/evaluate.py`
3. `configs/baseline.yaml`
4. `runs/` 下的实验结果
5. `reports/baseline_report.md`
6. 更新 `memory/experiment_log.jsonl`
7. 更新 `memory/INDEX.md`

完成后，必须向 GPT 提交 baseline review packet。

本阶段禁止事项：

1. 不得使用 locked_test 做模型选择。
2. 不得只报告最优模型，不报告失败模型。
3. 不得只使用分类指标评价回归模型。
4. 不得跳过 DummyRegressor baseline。

完成标准：

1. 已至少完成 5 类 baseline。
2. 已报告 MAE、RMSE、R²、log-MAE 或 log-RMSE。
3. 已比较不同数据划分下的表现。
4. 已记录每个实验配置和随机种子。
```

---

## Goal 5：模型优化

```text
/goal 基于 baseline_report.md 进行最多 5 轮有假设的模型优化。每轮必须先写明优化假设，再运行实验，最后记录指标变化。优化方向优先考虑目标变量变换、特征工程、样本加权、分组建模和模型集成。输出：

1. `reports/model_selection_report.md`
2. `memory/experiment_log.jsonl` 新增实验记录
3. `memory/decisions.md` 新增关键决策
4. 更新 `memory/INDEX.md`

完成后，必须向 GPT 提交模型选择 review packet。

本阶段禁止事项：

1. 不得根据 locked_test 调参。
2. 不得无限制搜索模型。
3. 不得无假设地随机试模型。
4. 不得只追求指标而忽略解释性和泛化能力。

完成标准：

1. 每轮实验都有明确假设。
2. 每轮实验都有指标变化记录。
3. 已说明最终候选模型的选择理由。
4. 已说明未采纳方案及理由。
```

---

## Goal 6：最终验收

```text
/goal 使用锁定测试集对最终候选模型进行一次最终评估，生成最终报告和模型卡。输出：

1. `reports/final_evaluation_report.md`
2. `reports/model_card.md`
3. `reports/reproducibility_report.md`
4. `figures/` 下的最终图表
5. 更新 `memory/INDEX.md`
6. 更新 `memory/decisions.md`

完成后，必须向 GPT 提交最终验收 review packet。

本阶段禁止事项：

1. 不得根据 locked_test 结果继续调参。
2. 不得删除失败结果。
3. 不得夸大模型适用范围。
4. 不得隐瞒模型局限性。

完成标准：

1. 已报告最终测试指标。
2. 已说明模型适用范围和不适用范围。
3. 已说明主要风险和局限性。
4. 已提供复现命令。
5. 已完成 GPT 最终审查记录。
```
