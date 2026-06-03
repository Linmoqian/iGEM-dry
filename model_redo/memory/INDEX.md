# memory/INDEX.md

## 当前阶段

阶段 0：旧模型审计 — **已完成，待 GPT 审查**。

## 项目目标

重建 MC-LR（微囊藻毒素-LR）浓度预测模型。

主任务：MC-LR 浓度回归预测。
辅助任务：基于阈值的风险分类。

## 当前关键结论

- `model_redo/` 是新版建模工程。
- 旧项目 `model/` 只能作为只读经验库和审计对象。
- 不直接继承旧模型结论。
- 旧模型审计已完成，核心发现见 [[old-model-lessons]]。
- **旧模型不包含 MC-LR 亚型数据**，目标变量均为"总微囊藻毒素"。
- **旧模型回归任务丢弃 66% 未检出样本**。
- **存在信息泄漏风险**（蓝藻叶绿素、qPCR 特征）。
- **无时间/站点外推验证**，**无 baseline**。
- 当前尚未开始数据源审计、清洗或训练。

## 当前禁止事项

- 不得修改旧项目 `model/`。
- 不得删除、覆盖或移动 `data/raw/` 中的任何原始数据。
- 不得在完成数据源审计前训练模型。
- 不得使用 locked_test 做模型选择。
- 不得把 GPT 的意见当作最终事实。

## 当前待办

1. ✅ 完成 `CLAUDE.md`。
2. ✅ 完成 `memory/` 初始文件。
3. ✅ 完成阶段 0 `/goal`。
4. ✅ 启动旧模型审计。
5. ✅ 生成 `memory/old_model_lessons.md`。
6. ✅ 生成 `reports/old_model_audit_report.md`。
7. ⬜ 向 GPT 提交阶段 0 review packet。
8. ⬜ 等待 GPT 审查反馈。
9. ⬜ 根据反馈修订或进入阶段 1。

## 下一次 GPT 审查点

旧模型审计完成后，请 GPT 审查：

- `memory/old_model_lessons.md`
- `reports/old_model_audit_report.md`
- `reports/gpt_review_packet_stage0.md`

## 重要文件

- `CLAUDE.md`
- `memory/old_model_lessons.md` — 旧模型审计详细结论
- `memory/decisions.md`
- `memory/gpt_review_log.md`
- `memory/experiment_log.jsonl`
- `reports/old_model_audit_report.md` — 旧模型正式审计报告（24 个发现项）
- `reports/gpt_review_packet_stage0.md` — GPT 审查包
