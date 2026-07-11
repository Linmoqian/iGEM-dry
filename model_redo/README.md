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
