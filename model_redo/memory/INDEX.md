# memory/INDEX.md

## 当前阶段

阶段 0-10 全部完成。Baseline 已运行，R² 偏低需改善。详见 `reports/autonomous_run_summary.md`。

## 项目目标

重建微囊藻毒素浓度预测模型。

**任务定义（Decision 003）：**
- 任务 A（主）：总 microcystins 浓度回归
- 任务 B：MC-LR 小样本验证
- 任务 C：中国场景迁移

## Baseline 结果

- Lake Erie（总 MC）：Ridge R²=0.063, RF R²=-0.042
- HABs NLA（总 MC）：RF R²=0.219
- EMLS（MC-LR）：Ridge R²=0.195（测试集仅 17 行）

**问题**：R² 太低，可能缺少关键特征或需要更强模型。

## 清洗后数据

- erie_clean.pkl: 3,074 行（总 MC）
- habs_nla_clean.pkl: 3,664 行（总 MC）
- emls_clean.pkl: 369 行（MC-LR）
- ncca2015_clean.pkl: 592 行（MC-LR，外部验证）

## 当前待办

1. ✅ 全部阶段 0-10
2. ⬜ 安装 pyarrow
3. ⬜ 下载 EPA NLA 数据
4. ⬜ 尝试 XGBoost/LightGBM
5. ⬜ 加入更多特征
6. ⬜ MC-LR 零值专门处理

## 重要文件

- `CLAUDE.md`
- `memory/old_model_lessons.md`
- `memory/decisions.md`
- `memory/gpt_review_log.md`
- `reports/autonomous_run_summary.md`
- `reports/baseline_results.json`
- `data/docs/统一数据字典.md`
- `data/docs/建模数据选择方案.md`
- `data/splits/split_manifest.json`
- `run_clean.py`, `run_split.py`, `run_train.py`, `run_audit.py`
