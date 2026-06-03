# memory/INDEX.md

## 当前阶段

阶段 0-5 已完成，阶段 6-9 待推进。详见 `reports/autonomous_run_summary.md`。

## 项目目标

重建微囊藻毒素浓度预测模型。

**任务定义（Decision 003，已采纳）：**
- 任务 A（主任务）：总 microcystins 浓度回归与风险分类
- 任务 B（受限验证）：MC-LR 专属小样本模型
- 任务 C（场景迁移）：中国/东湖场景适配

## 当前关键结论

- `model_redo/` 是新版建模工程
- 旧项目 `model/` 只读经验库，不直接继承
- 旧模型审计完成，详见 [[old-model-lessons]]
- 本地数据仅 EMLS Europe 有 MC-LR（369 行），等级 C
- 已下载 EPA NCCA 2015 MC-LR 数据（592 行，含 10 种 MC 异构体）
- MC-LR 样本合计 961 行（EMLS 369 + EPA 592）
- GPT 审查建议任务拆分，已采纳
- 严禁随机切分（GroupKFold / leave-one-lake-out）
- 检测限必须单独建模（Tobit / 左删失 / sensitivity）

## 当前禁止事项

- 不得修改旧项目 `model/`
- 不得删除 `data/raw/` 原始数据
- 不得使用 locked_test 做模型选择
- 不得把总 MC 模型包装成 MC-LR 模型

## 当前待办

1. ✅ 旧模型审计
2. ✅ 本地数据源审计
3. ✅ 数据适合性评估
4. ✅ 外部数据检索 + GPT 审查
5. ⬜ 下载 EPA NLA 水质+毒素数据
6. ⬜ 下载 GLERL-CIGLR 数据
7. ⬜ 统一数据字典与建模方案
8. ⬜ 清洗流水线
9. ⬜ 数据划分
10. ⬜ Baseline
11. ⬜ 优化（最多 3 轮）

## 重要文件

- `CLAUDE.md`
- `memory/old_model_lessons.md`
- `memory/decisions.md`
- `memory/gpt_review_log.md`
- `reports/autonomous_run_summary.md`
- `reports/old_model_audit_report.md`
- `reports/data_suitability_assessment.md`
- `data/docs/数据源审计报告.md`
- `data/docs/外部数据源检索报告.md`
