# model_redo 正式运行前置准备文件说明

本文档用于在正式启动 Claude Code / chrome-devtools-mcp / GPT 协作建模流程之前，提前准备 `model_redo` 工程中的基础文件、目录结构、记忆文件、GPT 审查模板、阶段目标与安全边界。

本项目目标不是简单复刻旧项目 `model/`，而是：

> 总结旧项目 `model/` 的经验，在 `model_redo/` 中重新构建一个更清晰、更可复现、更适合长期迭代的 MC-LR（微囊藻毒素-LR）浓度预测模型工程。

---

## 1. 总体原则

正式运行模型前，应先完成以下准备：

1. 建立新版工程目录结构。
2. 写好 `CLAUDE.md`，明确 Claude 的行为边界。
3. 建立 `memory/` 目录，作为长期可追溯记忆。
4. 准备 GPT 审查模板。
5. 准备上下文压缩与重新理解模板。
6. 准备阶段性 `/goal`，不要一开始设置巨大总目标。
7. 明确旧项目 `model/` 只读，不直接继承结论。
8. 明确主任务为 MC-LR 浓度回归预测，分类任务只是辅助风险分析。
9. 明确所有实验必须可复现、可追踪、可复盘。
10. 明确 GPT 只是外部审查者，不是最终裁判。

---

## 2. 推荐文件结构树

建议将 `model_redo` 扩展为如下结构：

```text
model_redo/
├─ CLAUDE.md
├─ README.md
├─ TODO.md
├─ environment.yml
├─ pyproject.toml
├─ .gitignore
│
├─ memory/
│  ├─ INDEX.md
│  ├─ old_model_lessons.md
│  ├─ decisions.md
│  ├─ experiment_log.jsonl
│  ├─ gpt_review_log.md
│  ├─ errors_and_lessons.md
│  ├─ gpt_review_template.md
│  ├─ context_refresh_template.md
│  └─ stage_goals.md
│
├─ data/
│  ├─ raw/
│  │  └─ README.md
│  ├─ docs/
│  │  ├─ 数据源审计报告.md
│  │  ├─ 数据字典.md
│  │  ├─ 变量单位说明.md
│  │  └─ 数据清洗报告.md
│  ├─ interim/
│  │  └─ README.md
│  ├─ cleaned/
│  │  └─ README.md
│  └─ splits/
│     └─ README.md
│
├─ src/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ audit.py
│  ├─ clean.py
│  ├─ schema.py
│  ├─ features.py
│  ├─ split.py
│  ├─ train.py
│  ├─ evaluate.py
│  ├─ interpret.py
│  └─ report.py
│
├─ configs/
│  ├─ data_audit.yaml
│  ├─ cleaning.yaml
│  ├─ split.yaml
│  ├─ baseline.yaml
│  └─ model_search.yaml
│
├─ runs/
│  └─ README.md
│
├─ figures/
│  └─ README.md
│
├─ reports/
│  ├─ old_model_audit_report.md
│  ├─ baseline_report.md
│  ├─ model_selection_report.md
│  ├─ final_evaluation_report.md
│  └─ model_card.md
│
└─ tests/
   ├─ test_cleaning.py
   ├─ test_features.py
   ├─ test_split.py
   └─ test_no_leakage.py
```

---

## 3. 正式启动前必须准备的文件清单

| 文件 | 是否必须 | 作用 |
|---|---:|---|
| `CLAUDE.md` | 必须 | 给 Claude 的总规则、边界和工作流 |
| `README.md` | 必须 | 给人类阅读的项目说明 |
| `TODO.md` | 推荐 | 阶段任务清单 |
| `.gitignore` | 必须 | 防止原始数据、实验结果、模型文件误提交 |
| `environment.yml` | 推荐 | 记录 Python 环境 |
| `pyproject.toml` | 可选 | 规范包结构、格式化与测试工具 |
| `memory/INDEX.md` | 必须 | 当前项目短记忆，不超过 200 行 |
| `memory/old_model_lessons.md` | 必须 | 旧模型审计和经验总结 |
| `memory/decisions.md` | 必须 | 关键决策记录 |
| `memory/experiment_log.jsonl` | 必须 | 实验日志，结构化记录 |
| `memory/gpt_review_log.md` | 必须 | GPT 审查记录 |
| `memory/errors_and_lessons.md` | 推荐 | 错误、踩坑和修复记录 |
| `memory/gpt_review_template.md` | 必须 | 固定 GPT 审查模板 |
| `memory/context_refresh_template.md` | 必须 | 上下文压缩与重新理解模板 |
| `memory/stage_goals.md` | 必须 | 分阶段 `/goal` 模板 |
| `data/docs/数据源审计报告.md` | 必须 | 数据源盘点与质量审计 |
| `data/docs/数据字典.md` | 必须 | 字段含义、类型、单位 |
| `data/docs/变量单位说明.md` | 必须 | 单位统一和换算规则 |
| `data/docs/数据清洗报告.md` | 必须 | 清洗规则与结果说明 |
| `configs/*.yaml` | 推荐 | 审计、清洗、划分、建模配置 |
| `tests/*.py` | 推荐 | 防止清洗错误、特征错误、数据泄漏 |

---

## 4. `CLAUDE.md` 初始内容

建议直接将以下内容写入 `model_redo/CLAUDE.md`。

```markdown
# CLAUDE.md

本项目是 `model_redo`，目标是重建 MC-LR（微囊藻毒素-LR）浓度预测模型。

## 1. 项目定位

- `model_redo/` 是新版建模工程。
- 旧项目 `model/` 只能作为只读经验库和审计对象。
- 不得修改旧项目 `model/` 中的任何文件。
- 不得直接继承旧模型结论，必须重新审计数据、重新定义任务、重新建立实验流程。

## 2. 最高优先级规则

1. 不得删除、覆盖或移动 `data/raw/` 中的任何原始数据。
2. 不得在完成数据源审计前开始训练模型。
3. 主任务是 MC-LR 浓度回归预测；分类任务只能作为辅助风险分析。
4. 所有实验必须记录配置、数据版本、特征版本、模型、随机种子、指标和结论。
5. `locked_test` 只能用于最终验收，不得用于模型选择或调参。
6. GPT 的反馈是审查意见，不是事实结论；最终结论必须由数据、代码、指标和可复现实验支持。
7. 每完成一个阶段，必须生成阶段报告，并向 GPT 提交 review packet 请求审查。
8. 每次重大修改后，必须更新 `memory/INDEX.md`。
9. 长日志写入文件，不要塞进对话上下文。
10. 如发现目标变量、单位、数据泄漏、样本划分存在问题，必须优先暂停建模并报告。

## 3. 建模任务定义

主任务：

- 输入水质、环境、时间、空间等特征。
- 输出 MC-LR 浓度数值。
- 优先考虑回归任务。

辅助任务：

- 基于 MC-LR 阈值进行风险分类。
- 分类任务不能替代浓度预测任务。

## 4. 推荐流程

必须按以下顺序推进：

1. 审计旧项目 `model/`。
2. 总结旧模型经验，写入 `memory/old_model_lessons.md`。
3. 审计 `model_redo/data/raw/`。
4. 生成数据源审计报告、数据字典、变量单位说明。
5. 编写数据清洗流程。
6. 固定数据划分。
7. 建立 baseline。
8. 进行有假设的模型优化。
9. 做解释性分析。
10. 进行最终 locked_test 验收。
11. 生成最终报告和模型卡。

## 5. GPT 交流规则

每次向 GPT 请求审查时，必须加入以下提醒：

> 你保持怀疑态度。你不一定都是对的，我也不一定是对的，但我们都力求最优。

每次提交给 GPT 的内容必须是压缩后的 review packet，不得直接粘贴完整代码、完整日志、完整论文或完整数据。

GPT 审查意见必须记录到：

- `memory/gpt_review_log.md`
- `memory/decisions.md`

对 GPT 的建议必须分类：

- 接受
- 部分接受
- 暂不接受
- 需要进一步验证
- 发现 GPT 可能错误

## 6. 上下文节省规则

1. `memory/INDEX.md` 不超过 200 行。
2. 对话中只保留当前目标、当前阶段、关键结论和下一步。
3. 长文献、长日志、完整实验结果必须保存到文件。
4. 每多轮 GPT 交流后，主动压缩上下文，并让 GPT 重新基于 `memory/INDEX.md`、`old_model_lessons.md`、`experiment_log.jsonl` 理解项目。
5. 不确定时，先读取记忆文件，不要凭印象继续。

## 7. 阶段完成标准

每个阶段完成时必须至少包含：

- 产物文件
- 核心结论
- 已知问题
- 风险点
- 下一步建议
- GPT 审查记录
- 是否允许进入下一阶段

## 8. 禁止事项

- 禁止未审计数据就训练。
- 禁止为了提高指标而频繁查看 locked_test。
- 禁止只报告最优结果而不记录失败实验。
- 禁止用 GPT 的判断替代实验结果。
- 禁止生成无法复现的实验。
- 禁止把分类指标当作浓度回归模型的主要评价。
```

---

## 5. `README.md` 初始内容

建议写入 `model_redo/README.md`。

```markdown
# model_redo

本项目用于重建 MC-LR（微囊藻毒素-LR）浓度预测模型。

## 项目目标

本项目目标是从旧项目 `model/` 中总结经验，在 `model_redo/` 中重新建立一个更加清晰、可复现、可审计的 MC-LR 浓度预测模型工程。

## 任务定义

主任务：MC-LR 浓度回归预测。

辅助任务：基于 MC-LR 浓度阈值的风险分类。

## 旧项目关系

旧项目 `model/` 仅作为只读经验库，不直接继承旧模型结论。新版项目必须重新完成：

1. 数据源审计；
2. 数据清洗；
3. 任务定义；
4. 数据划分；
5. baseline 建模；
6. 模型优化；
7. 最终评估；
8. 模型解释与报告。

## 推荐运行流程

```bash
python run_audit.py
python run_clean.py
python run_train.py
python run_eval.py
python run_interpret.py
```

注意：上述脚本可能在项目初期尚未创建，需由 Claude 按阶段生成。

## 重要规则

- 不得删除或覆盖 `data/raw/` 中的原始数据。
- 不得在数据审计前训练模型。
- 不得用 locked_test 做模型选择。
- 所有实验必须记录到 `memory/experiment_log.jsonl`。
- 每个阶段结束后必须向 GPT 提交 review packet 审查。
```

---

## 6. `.gitignore` 初始内容

建议写入 `model_redo/.gitignore`。

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.so
.venv/
venv/
env/
.ipynb_checkpoints/

# OS / IDE
.DS_Store
Thumbs.db
.vscode/
.idea/

# Raw data and large generated files
data/raw/
data/interim/
data/cleaned/*.parquet
data/cleaned/*.feather
data/cleaned/*.pkl
data/cleaned/*.pickle

# Model outputs
runs/
figures/
*.joblib
*.pkl
*.pickle
*.onnx
*.pt
*.pth
*.ckpt
*.bin

# Logs
*.log
logs/

# Secrets
.env
*.key
*.pem

# Temporary files
*.tmp
*.bak
```

说明：

- 如果希望版本管理某些清洗后的小型样例数据，可以后续手动调整。
- 原始数据默认不提交。
- 实验结果默认不提交，最终报告可单独提交。

---

## 7. `TODO.md` 初始内容

建议写入 `model_redo/TODO.md`。

```markdown
# TODO

## 阶段 0：旧模型审计

- [ ] 读取旧项目 `model/` 的目录结构
- [ ] 审计旧模型目标变量
- [ ] 判断旧模型是分类、回归还是混合任务
- [ ] 审计旧模型数据源
- [ ] 审计旧模型清洗逻辑
- [ ] 审计旧模型特征工程
- [ ] 审计旧模型评估指标
- [ ] 总结可复用经验
- [ ] 总结不可继承问题
- [ ] 生成 `memory/old_model_lessons.md`
- [ ] 生成 `reports/old_model_audit_report.md`
- [ ] 向 GPT 提交审查

## 阶段 1：原始数据审计

- [ ] 扫描 `data/raw/`
- [ ] 识别所有数据文件
- [ ] 识别 MC-LR 目标变量
- [ ] 识别时间字段
- [ ] 识别空间字段
- [ ] 识别水质与环境变量
- [ ] 统计缺失率
- [ ] 统计异常值
- [ ] 生成数据源审计报告
- [ ] 生成数据字典
- [ ] 生成变量单位说明
- [ ] 向 GPT 提交审查

## 阶段 2：数据清洗

- [ ] 编写清洗配置
- [ ] 编写字段映射规则
- [ ] 统一单位
- [ ] 处理缺失值
- [ ] 处理异常值
- [ ] 处理重复样本
- [ ] 生成清洗后数据
- [ ] 生成数据清洗报告
- [ ] 向 GPT 提交审查

## 阶段 3：数据划分

- [ ] 设计 random split
- [ ] 设计 time-based split
- [ ] 设计 site-based split
- [ ] 固定 locked_test
- [ ] 编写防泄漏测试
- [ ] 向 GPT 提交审查

## 阶段 4：baseline 建模

- [ ] DummyRegressor
- [ ] Ridge / ElasticNet
- [ ] RandomForest
- [ ] XGBoost
- [ ] LightGBM
- [ ] 生成 baseline report
- [ ] 向 GPT 提交审查

## 阶段 5：模型优化

- [ ] 每轮先写优化假设
- [ ] 每轮记录实验配置
- [ ] 每轮记录指标变化
- [ ] 每轮记录是否采纳 GPT 建议
- [ ] 最多 5 轮后生成模型选择报告

## 阶段 6：最终验收

- [ ] 使用 locked_test 做一次最终评估
- [ ] 不再根据 locked_test 调参
- [ ] 生成最终评估报告
- [ ] 生成模型卡
- [ ] 生成复现实验说明
```

---

## 8. `memory/INDEX.md` 初始内容

建议写入 `model_redo/memory/INDEX.md`。

```markdown
# memory/INDEX.md

## 当前阶段

阶段 0：旧模型审计前准备。

## 项目目标

重建 MC-LR（微囊藻毒素-LR）浓度预测模型。

主任务：MC-LR 浓度回归预测。  
辅助任务：基于阈值的风险分类。

## 当前关键结论

- `model_redo/` 是新版建模工程。
- 旧项目 `model/` 只能作为只读经验库和审计对象。
- 不直接继承旧模型结论。
- 当前尚未开始数据审计、清洗或训练。
- 正式建模前必须先完成旧模型审计和原始数据审计。

## 当前禁止事项

- 不得修改旧项目 `model/`。
- 不得删除、覆盖或移动 `data/raw/` 中的任何原始数据。
- 不得在完成数据源审计前训练模型。
- 不得使用 locked_test 做模型选择。
- 不得把 GPT 的意见当作最终事实。

## 当前待办

1. 完成 `CLAUDE.md`。
2. 完成 `memory/` 初始文件。
3. 完成阶段 0 `/goal`。
4. 启动旧模型审计。
5. 生成 `memory/old_model_lessons.md`。
6. 生成 `reports/old_model_audit_report.md`。
7. 向 GPT 提交阶段 0 审查。

## 下一次 GPT 审查点

旧模型审计完成后，请 GPT 审查：

- `memory/old_model_lessons.md`
- `reports/old_model_audit_report.md`
- 阶段 0 review packet

## 重要文件

- `CLAUDE.md`
- `memory/old_model_lessons.md`
- `memory/decisions.md`
- `memory/gpt_review_log.md`
- `memory/experiment_log.jsonl`
- `data/docs/数据源审计报告.md`
- `data/docs/数据清洗报告.md`
```

---

## 9. `memory/decisions.md` 初始内容

建议写入 `model_redo/memory/decisions.md`。

```markdown
# decisions.md

本文件用于记录项目中的关键决策，包括数据、模型、指标、实验流程、GPT 建议采纳情况等。

---

## Decision 001

日期：待填写  
阶段：项目启动  
问题：是否直接复用旧项目 `model/` 的代码和结论？

### 选项

1. 直接复制旧代码和旧结论。
2. 完全放弃旧项目。
3. 审计旧项目后，选择性继承经验，不直接继承结论。

### 决定

选择 3：审计旧项目后，选择性继承经验，不直接继承结论。

### 理由

旧项目可能包含有价值的数据清洗经验、特征工程经验、模型训练经验和解释性分析经验；但旧模型可能存在任务定义偏分类、指标与 MC-LR 浓度回归不完全匹配、数据源混合、数据泄漏风险或结论不可直接迁移等问题。

### GPT 意见

待审查。

### 最终采纳情况

待定。

### 后续验证方式

完成 `memory/old_model_lessons.md` 和 `reports/old_model_audit_report.md` 后，再判断旧项目中哪些部分可复用。

---

## Decision 002

日期：待填写  
阶段：项目启动  
问题：新版项目的主任务是什么？

### 决定

新版项目主任务是 MC-LR 浓度回归预测。风险分类只能作为辅助任务。

### 理由

项目目标是预测 MC-LR 浓度，而不是仅判断是否超标。分类任务会损失浓度信息，不能替代回归预测。

### GPT 意见

待审查。

### 后续验证方式

在数据审计阶段确认原始数据中是否存在可用于回归预测的 MC-LR 浓度字段、单位和检测下限信息。
```

---

## 10. `memory/gpt_review_log.md` 初始内容

建议写入 `model_redo/memory/gpt_review_log.md`。

```markdown
# gpt_review_log.md

本文件用于记录 Claude 向 GPT 提交阶段性成果后的审查意见、采纳情况和后续动作。

---

## Review 001

日期：待填写  
阶段：阶段 0：旧模型审计  
状态：待提交

### 提交给 GPT 的 review packet

待填写。

### GPT 主要反馈

待填写。

### Claude 判断

待填写。

### 采纳项

待填写。

### 未采纳项

待填写。

### 需要进一步验证项

待填写。

### 下一步

待填写。
```

---

## 11. `memory/experiment_log.jsonl` 初始内容

建议创建空文件，也可以先写入一条元信息记录。

```jsonl
{"type":"project_init","stage":"preparation","message":"experiment_log initialized; no experiment has been run yet","timestamp":"待填写"}
```

后续每次实验建议使用如下格式：

```jsonl
{"type":"experiment","experiment_id":"EXP-0001","stage":"baseline","data_version":"main_cleaned_v1","split":"time_split_v1","model":"LightGBM","target":"log1p_mc_lr","seed":42,"metrics":{"val_rmse":null,"val_mae":null,"val_r2":null},"hypothesis":"待填写","result_summary":"待填写","gpt_review_id":"待填写","decision":"待填写"}
```

---

## 12. `memory/old_model_lessons.md` 初始内容

建议写入 `model_redo/memory/old_model_lessons.md`。

```markdown
# old_model_lessons.md

本文件用于记录旧项目 `model/` 的审计结果和可复用经验。

注意：旧项目只能作为经验库和审计对象，不得直接继承结论。

---

## 1. 旧项目基本信息

待填写：

- 旧项目路径：`model/`
- 旧项目主要脚本：
- 旧项目主要数据源：
- 旧项目主要模型：
- 旧项目主要评估指标：

## 2. 旧项目任务定义审计

待填写：

- 旧模型预测目标是什么？
- 是分类、回归还是混合任务？
- 是否真正预测 MC-LR 浓度？
- 是否存在将浓度预测简化成分类的问题？

## 3. 旧项目数据源审计

待填写：

- 使用了哪些数据源？
- 哪些数据源包含 MC-LR 浓度？
- 哪些数据源只是环境变量或藻华相关变量？
- 数据源之间单位是否一致？
- 数据源之间时间、空间尺度是否一致？

## 4. 旧项目清洗逻辑审计

待填写：

- 字段映射规则：
- 单位换算规则：
- 缺失值处理：
- 异常值处理：
- 重复样本处理：
- 检测下限处理：

## 5. 旧项目特征工程经验

待填写：

- 可复用特征：
- 不确定特征：
- 可能导致泄漏的特征：
- 与 MC-LR 机理相关的特征：

## 6. 旧项目模型经验

待填写：

- LightGBM 表现：
- XGBoost 表现：
- Ensemble 表现：
- 是否有 baseline 对照：
- 是否存在过拟合：

## 7. 旧项目评估指标问题

待填写：

- 是否使用了分类指标？
- 是否使用了回归指标？
- 是否有验证集和测试集区分？
- 是否存在指标与任务不匹配？

## 8. 可复用经验

待填写。

## 9. 不应直接继承的问题

待填写。

## 10. 新版项目需要避免的风险

待填写。
```

---

## 13. `memory/errors_and_lessons.md` 初始内容

```markdown
# errors_and_lessons.md

本文件用于记录项目中的错误、异常、失败实验、踩坑和修复方式。

---

## Error 001

日期：待填写  
阶段：待填写  
问题描述：待填写  
影响范围：待填写  
原因分析：待填写  
修复方式：待填写  
是否需要 GPT 审查：是 / 否  
后续预防措施：待填写
```

---

## 14. `memory/gpt_review_template.md` 初始内容

这是 Claude 每次向 GPT 请求审查时应使用的固定模板。

```markdown
你保持怀疑态度。你不一定都是对的，我也不一定是对的，但我们都力求最优。

你现在是本项目的外部审查者，而不是最终裁判。请你审查以下阶段性成果，重点寻找错误、遗漏、数据泄漏、指标不匹配、任务定义不清、实验不可复现、结论过度推断等问题。

## 项目背景

本项目位于 `model_redo/`，目标是重建 MC-LR（微囊藻毒素-LR）浓度预测模型。

主任务：

- MC-LR 浓度回归预测。

辅助任务：

- 基于阈值的风险分类。

旧项目 `model/` 仅作为经验库和审计对象，不直接继承结论。

## 当前阶段

【填写当前阶段，例如：旧模型审计 / 数据源审计 / 数据清洗 / baseline / 模型优化 / 最终验收】

## 本阶段目标

【填写本阶段目标】

## 本阶段产物

【列出文件路径，例如：

- memory/old_model_lessons.md
- reports/old_model_audit_report.md
- data/docs/数据源审计报告.md
】

## 核心结论摘要

【用 5-10 条列出 Claude 当前认为成立的结论】

## 当前疑点

【列出尚不确定的问题】

## 希望你重点审查

1. 任务定义是否有偏差？
2. 数据处理是否有泄漏风险？
3. 指标是否匹配 MC-LR 浓度预测目标？
4. 是否存在过度依赖旧模型的问题？
5. 是否有更合理的下一步实验？
6. 当前结论是否证据不足？
7. 是否应该暂停进入下一阶段？

## 请按以下格式回复

### 1. 总体判断

是否允许进入下一阶段：允许 / 暂不允许 / 需要补充后允许

### 2. 主要问题

列出最重要的问题，不要泛泛而谈。

### 3. 高风险点

重点指出可能导致模型无效或结论不可信的问题。

### 4. 建议修改

区分“必须修改”和“可选优化”。

### 5. 我可能错在哪里

请主动指出你自己的判断可能不可靠的地方。

### 6. 下一步建议

给出可执行的下一步。
```

---

## 15. `memory/context_refresh_template.md` 初始内容

这是多轮 GPT 交流后，用于压缩上下文、重新理解项目的模板。

```markdown
你保持怀疑态度。你不一定都是对的，我也不一定是对的，但我们都力求最优。

现在请你压缩并重建项目理解。不要依赖旧对话印象，请只基于下面的项目记忆文件重新理解项目：

1. `memory/INDEX.md`
2. `memory/old_model_lessons.md`
3. `memory/decisions.md`
4. `memory/experiment_log.jsonl`
5. `memory/gpt_review_log.md`
6. 当前阶段报告

请输出：

1. 你对项目目标的重新理解；
2. 当前阶段；
3. 已确认事实；
4. 未确认假设；
5. 主要风险；
6. 下一步最应该审查什么；
7. 你认为此前对话中可能被上下文污染的地方；
8. 是否建议继续当前路线，还是暂停修正。
```

---

## 16. `memory/stage_goals.md` 初始内容

建议将所有阶段性 `/goal` 写入此文件，正式运行时逐个使用。

```markdown
# stage_goals.md

本文件记录 Claude Code 分阶段 `/goal` 模板。

不要一次性设置“完成整个模型重建”的巨大目标。必须分阶段推进。

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
```

---

## 17. `data/docs/数据源审计报告.md` 初始内容

```markdown
# 数据源审计报告

本报告用于记录 `data/raw/` 中所有原始数据文件的来源、结构、字段、质量和建模可用性。

## 1. 审计目标

- 识别所有原始数据文件。
- 判断哪些数据包含 MC-LR 浓度字段。
- 判断哪些数据可用于主任务：MC-LR 浓度回归预测。
- 判断哪些数据只能用于辅助分析或外部验证。
- 识别单位、时间、空间、缺失值、异常值和检测下限问题。

## 2. 原始数据文件清单

| 编号 | 文件/目录 | 格式 | 来源 | 是否包含 MC-LR | 备注 |
|---|---|---|---|---|---|
| 1 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 |

## 3. 字段审计

| 数据源 | 字段名 | 推测含义 | 数据类型 | 单位 | 缺失率 | 是否用于建模 | 备注 |
|---|---|---|---|---|---:|---|---|
| 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 |

## 4. 目标变量审计

| 数据源 | MC-LR 字段名 | 单位 | 是否数值型 | 是否有检测下限 | 是否可用于回归 | 备注 |
|---|---|---|---|---|---|---|
| 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 |

## 5. 时间字段审计

待填写。

## 6. 空间字段审计

待填写。

## 7. 缺失值与异常值审计

待填写。

## 8. 数据源可用性判断

| 数据源 | 可用性 | 用途 | 风险 |
|---|---|---|---|
| 待填写 | 主训练 / 外部验证 / 辅助 / 暂不使用 | 待填写 | 待填写 |

## 9. 初步结论

待填写。

## 10. 需要 GPT 审查的问题

待填写。
```

---

## 18. `data/docs/数据字典.md` 初始内容

```markdown
# 数据字典

本文件记录清洗后主数据表中的字段定义。

| 字段名 | 中文含义 | 数据类型 | 单位 | 来源字段 | 是否特征 | 是否目标变量 | 备注 |
|---|---|---|---|---|---|---|---|
| sample_id | 样本编号 | string | 无 | 生成 | 否 | 否 | 唯一标识 |
| date | 采样日期 | datetime | 无 | 待填写 | 是 | 否 | 时间特征基础 |
| site_id | 采样点编号 | string | 无 | 待填写 | 是 | 否 | 空间特征基础 |
| mc_lr | MC-LR 浓度 | float | 待确认 | 待填写 | 否 | 是 | 主目标变量 |
```

---

## 19. `data/docs/变量单位说明.md` 初始内容

```markdown
# 变量单位说明

本文件用于记录所有关键变量的单位、换算规则和不确定性。

## 1. 目标变量

| 变量 | 标准单位 | 原始单位 | 换算规则 | 备注 |
|---|---|---|---|---|
| MC-LR 浓度 | 待确认 | 待确认 | 待确认 | 主目标变量 |

## 2. 环境变量

| 变量 | 标准单位 | 原始单位 | 换算规则 | 备注 |
|---|---|---|---|---|
| 水温 | ℃ | 待确认 | 待确认 | 可能重要 |
| pH | 无量纲 | 待确认 | 无 | 可能重要 |
| 溶解氧 | mg/L | 待确认 | 待确认 | 可能重要 |
| 总氮 | mg/L | 待确认 | 待确认 | 可能重要 |
| 总磷 | mg/L | 待确认 | 待确认 | 可能重要 |
| 叶绿素 a | μg/L | 待确认 | 待确认 | 可能重要 |

## 3. 单位风险

待填写：

- 是否存在 μg/L 与 mg/L 混用？
- 是否存在 ng/L 与 μg/L 混用？
- 是否存在中文单位或表头不一致？
- 是否存在小于检出限的记录？
```

---

## 20. `data/docs/数据清洗报告.md` 初始内容

```markdown
# 数据清洗报告

本报告用于记录从 `data/raw/` 到 `data/cleaned/` 的清洗过程。

## 1. 清洗目标

- 统一字段名。
- 统一单位。
- 处理缺失值。
- 处理异常值。
- 处理重复样本。
- 明确目标变量 MC-LR 的处理方式。
- 输出可复现的清洗后数据。

## 2. 输入数据

| 数据源 | 路径 | 是否使用 | 原因 |
|---|---|---|---|
| 待填写 | 待填写 | 待填写 | 待填写 |

## 3. 字段映射规则

| 原始字段 | 标准字段 | 说明 |
|---|---|---|
| 待填写 | 待填写 | 待填写 |

## 4. 单位转换规则

| 字段 | 原始单位 | 标准单位 | 转换公式 |
|---|---|---|---|
| 待填写 | 待填写 | 待填写 | 待填写 |

## 5. 缺失值处理

待填写。

## 6. 异常值处理

待填写。

## 7. 重复样本处理

待填写。

## 8. 目标变量处理

待填写：

- 是否使用原始 MC-LR？
- 是否使用 `log1p(MC-LR)`？
- 是否存在低于检出限记录？
- 如何处理 0 值和极端高值？

## 9. 输出数据

| 输出文件 | 样本数 | 字段数 | 备注 |
|---|---:|---:|---|
| `data/cleaned/main_cleaned.parquet` | 待填写 | 待填写 | 待填写 |

## 10. 删除或排除的数据

| 数据 | 原因 | 数量 |
|---|---|---:|
| 待填写 | 待填写 | 待填写 |

## 11. 已知问题

待填写。

## 12. GPT 审查问题

待填写。
```

---

## 21. `configs/data_audit.yaml` 初始内容

```yaml
project:
  name: model_redo
  task: mc_lr_concentration_prediction

paths:
  raw_dir: data/raw
  docs_dir: data/docs
  audit_report: data/docs/数据源审计报告.md
  data_dictionary: data/docs/数据字典.md
  unit_report: data/docs/变量单位说明.md

audit:
  infer_encoding: true
  infer_delimiter: true
  scan_excel_sheets: true
  profile_missing_values: true
  profile_numeric_ranges: true
  detect_datetime_columns: true
  detect_spatial_columns: true
  detect_target_candidates: true

target_keywords:
  - MC-LR
  - MCLR
  - microcystin
  - microcystin-LR
  - 微囊藻毒素
  - 微囊藻毒素-LR
```

---

## 22. `configs/cleaning.yaml` 初始内容

```yaml
project:
  name: model_redo

paths:
  raw_dir: data/raw
  interim_dir: data/interim
  cleaned_dir: data/cleaned
  cleaning_report: data/docs/数据清洗报告.md

cleaning:
  preserve_raw: true
  output_format: parquet
  standardize_column_names: true
  standardize_units: true
  remove_duplicate_samples: true
  handle_missing_values: true
  handle_outliers: true

target:
  name: mc_lr
  standard_unit: unknown
  transform_candidates:
    - raw
    - log1p
  below_detection_limit_policy: to_be_decided

warnings:
  require_report_before_training: true
  forbid_locked_test_access: true
```

---

## 23. `configs/split.yaml` 初始内容

```yaml
split:
  random_seed: 42
  strategies:
    - name: random_split
      enabled: true
      train_ratio: 0.7
      val_ratio: 0.15
      test_ratio: 0.15

    - name: time_split
      enabled: true
      time_column: date
      train_ratio: 0.7
      val_ratio: 0.15
      test_ratio: 0.15

    - name: site_split
      enabled: true
      site_column: site_id
      train_ratio: 0.7
      val_ratio: 0.15
      test_ratio: 0.15

locked_test:
  enabled: true
  use_only_for_final_evaluation: true
```

---

## 24. `configs/baseline.yaml` 初始内容

```yaml
baseline:
  target: mc_lr
  target_transform: log1p
  metrics:
    - mae
    - rmse
    - r2
    - spearman
    - log_mae
    - log_rmse

models:
  - name: dummy_regressor
    enabled: true

  - name: ridge
    enabled: true

  - name: elasticnet
    enabled: true

  - name: random_forest
    enabled: true

  - name: xgboost
    enabled: true

  - name: lightgbm
    enabled: true

rules:
  forbid_locked_test_for_model_selection: true
  require_experiment_log: true
  require_seed: true
  require_config_snapshot: true
```

---

## 25. `environment.yml` 初始内容

```yaml
name: model_redo
channels:
  - conda-forge
  - defaults

dependencies:
  - python=3.11
  - pip
  - numpy
  - pandas
  - scipy
  - scikit-learn
  - matplotlib
  - pyarrow
  - openpyxl
  - pyyaml
  - joblib
  - pytest
  - pip:
      - xgboost
      - lightgbm
      - shap
```

说明：

- 如果 LightGBM 或 XGBoost 在 Windows 安装失败，可后续改用 pip 或 conda-forge 单独安装。
- 深度学习依赖不要一开始安装，除非数据审计证明时间序列结构足够支持。

---

## 26. `pyproject.toml` 初始内容

```toml
[project]
name = "model-redo"
version = "0.1.0"
description = "MC-LR concentration prediction model reconstruction project"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.ruff]
line-length = 100
```

---

## 27. 目录占位 README 文件

### `data/raw/README.md`

```markdown
# data/raw

本目录用于存放原始数据。

重要规则：

- 不得删除、覆盖或移动本目录中的原始数据。
- 所有清洗和转换结果必须输出到 `data/interim/` 或 `data/cleaned/`。
- 原始数据默认不纳入 Git 管理。
```

### `data/interim/README.md`

```markdown
# data/interim

本目录用于存放中间处理数据。

例如：

- 初步字段标准化后的数据；
- 单位统一后的数据；
- 合并前的单数据源清洗结果。
```

### `data/cleaned/README.md`

```markdown
# data/cleaned

本目录用于存放清洗后的建模数据。

主要输出：

- `main_cleaned.parquet`
- `main_cleaned_report.json`
```

### `data/splits/README.md`

```markdown
# data/splits

本目录用于存放固定的数据划分文件。

要求：

- 训练集、验证集、测试集划分必须可复现。
- locked_test 只能用于最终验收。
- 不得根据 locked_test 结果继续调参。
```

### `runs/README.md`

```markdown
# runs

本目录用于保存每次实验输出。

每次实验应创建独立目录，例如：

```text
runs/EXP-0001_lightgbm_baseline/
├─ config.yaml
├─ metrics.json
├─ model.joblib
├─ predictions.parquet
└─ notes.md
```
```

### `figures/README.md`

```markdown
# figures

本目录用于保存模型评估图和解释性图表。

建议包括：

- predicted_vs_actual
- residuals
- error_by_site
- error_by_season
- feature_importance
- shap
```

---

## 28. 正式启动 Claude 的第一条 prompt

准备好以上文件后，可以用以下 prompt 启动 Claude。

```text
请先阅读 `CLAUDE.md` 和 `memory/INDEX.md`。你当前只允许执行阶段 0：旧模型审计。

旧项目 `model/` 只能读取，不能修改。请审计旧项目的数据来源、清洗逻辑、目标变量、模型方法、评估指标、可复用经验和潜在风险。

完成后写入：

1. `memory/old_model_lessons.md`
2. `reports/old_model_audit_report.md`
3. 更新 `memory/INDEX.md`
4. 更新 `memory/decisions.md`
5. 生成发给 GPT 的 review packet

禁止事项：

1. 不得训练模型。
2. 不得修改旧项目 `model/`。
3. 不得删除、覆盖或移动 `data/raw/` 中任何文件。
4. 不得复制旧项目代码到 `model_redo/`。
5. 不得直接继承旧模型结论。

完成后请使用 `memory/gpt_review_template.md` 的格式向 GPT 请求审查，并将 GPT 反馈记录到 `memory/gpt_review_log.md`。
```

---

## 29. GPT 交流策略

你希望 Claude 和 GPT 充分交流，这个方向是合理的，但建议采用“阶段闸门制”。

### 需要 GPT 审查的情况

| 情况 | 是否需要 GPT |
|---|---:|
| 创建目录结构 | 不需要 |
| 写普通辅助函数 | 不需要 |
| 完成旧模型审计 | 需要 |
| 确定目标变量 | 必须 |
| 确定清洗规则 | 必须 |
| 固定数据划分 | 必须 |
| baseline 结果出来 | 必须 |
| 模型优化方向改变 | 必须 |
| 最终测试集评估前 | 必须 |
| 最终报告完成后 | 必须 |

### 每次 GPT 交流必须包含

```text
你保持怀疑态度。你不一定都是对的，我也不一定是对的，但我们都力求最优。
```

### 每次 GPT 交流后必须记录

1. GPT 认为可以进入下一阶段吗？
2. GPT 指出了哪些高风险问题？
3. 哪些建议被接受？
4. 哪些建议被拒绝？为什么？
5. 哪些建议需要实验验证？
6. Claude 是否发现 GPT 可能判断错误？

---

## 30. 最终启动前检查表

正式运行 Claude 之前，请检查：

- [ ] `model_redo/CLAUDE.md` 已存在。
- [ ] `model_redo/memory/INDEX.md` 已存在。
- [ ] `model_redo/memory/decisions.md` 已存在。
- [ ] `model_redo/memory/gpt_review_log.md` 已存在。
- [ ] `model_redo/memory/gpt_review_template.md` 已存在。
- [ ] `model_redo/memory/context_refresh_template.md` 已存在。
- [ ] `model_redo/memory/stage_goals.md` 已存在。
- [ ] `.gitignore` 已设置，原始数据不会误提交。
- [ ] `data/raw/` 中原始数据已备份。
- [ ] 已明确旧项目 `model/` 只读。
- [ ] 已明确当前只运行阶段 0。
- [ ] 已明确不能训练模型。
- [ ] 已明确每阶段结束后需要 GPT 审查。
- [ ] 已明确 GPT 不是最终裁判。

---

## 31. 核心提醒

本项目的正确运行方式是：

```text
Claude 执行工程任务
GPT 进行外部审查
memory 文件记录长期状态
experiment_log 记录实验事实
数据划分和指标作为最终裁判
```

不要让 Claude 和 GPT 只是互相说服。  
每一次推进都必须留下文件、指标、报告和决策记录。

最重要的一句话：

> 新版 `model_redo` 不继承旧模型的结论，只继承旧模型中经审计后确认有价值的经验。
