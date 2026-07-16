# gpt_review_log.md

本文件用于记录 Claude 向 GPT 提交阶段性成果后的审查意见、采纳情况和后续动作。

---

## Review 001

日期：2026-06-04
阶段：阶段 3：外部数据源检索
状态：已完成
对话 URL：https://chatgpt.com/c/6a20ae60-8b24-83a7-b63c-077e09532321

### 提交给 GPT 的 review packet

`reports/gpt_review_packets/stage3_external_dataset_search_request.md`

### GPT 主要反馈

1. **任务定义应拆分**：A（总 MC 回归）+ B（MC-LR 小样本验证）+ C（中国场景迁移）
2. **不要把总 MC 模型包装成 MC-LR 模型**
3. **推荐 12 个外部数据集**，高优先级：EPA NLA（3,027 观测）、NOAA NCEI Lake Erie、GLERL-CIGLR、EPA WQP
4. **严禁随机切分**：必须用 GroupKFold / leave-one-lake-out / leave-one-year-out
5. **检测限必须单独建模**：Tobit / 左删失 / sensitivity analysis
6. **中国公开数据不含 MC-LR**，只适合做辅助特征

### Claude 判断

GPT 的核心判断与 Claude 审计结论高度一致：
- 本地数据仅 EMLS 有 MC-LR，样本量不足
- 总 MC 数据充足但不等于 MC-LR
- 需要任务重定义

### 采纳项

- [x] 任务拆分为 A/B/C 三层
- [x] 主模型改为"总 MC 风险模型"
- [x] MC-LR 作为受限小样本验证
- [x] 严禁随机切分
- [x] 检测限单独建模
- [x] 新增数据集候选（EPA NLA、GLERL-CIGLR、WQP、Figshare、data.gov）

### 未采纳项

- 暂无

### 需要进一步验证项

- EPA NLA 2022 数据字段一致性
- WQP 中 MC-LR 精确匹配的样本量
- Figshare Global Microcystin 数据集下载可达性
- data.gov 20 Reservoirs 是否含 MC 浓度

### 下一步

1. 更新外部数据源检索报告
2. 下载 EPA NLA 数据
3. 验证 GLERL-CIGLR 数据
4. 尝试 WQP API 查询 MC-LR
5. 更新任务定义和数据方案

---

## Review 002

日期：2026-06-08
阶段：阶段 8 — 模型迭代审查
状态：已完成
对话 URL：https://chatgpt.com/c/6a2622f6-7cbc-83a5-8c86-6740bc16f56e

### 提交给 GPT 的 review packet

`reports/gpt_review_packets/stage8_model_iteration_review_packet.md`

### GPT 主要反馈

1. **总体判断**：阶段 8 结果有审计价值，但不能支持"重建 MC-LR 模型"的主叙事。当前最可靠的是 Lake Erie 总 MC 同步估计模型。
2. **任务名称不匹配**：不能用总 MC 模型证明 MC-LR 有效。
3. **近标签代理变量风险**：蓝藻叶绿素同步测量时，模型是诊断性估计而非预测。
4. **HABs 随机划分不可信**：必须 GroupKFold by DSGN_CYCLE。
5. **EMLS 零值是核心风险**：54% 零值需要 sensitivity 分析。
6. **跨数据集失败先查 bug**：R²=-19M 首先怀疑工程问题。
7. **中国部署无证据链**：需本地校准。

### Claude 判断

GPT 的审查非常深刻，核心判断与 Claude 自身分析高度一致：
- 蓝藻叶绿素的泄漏风险需要进一步确认
- 跨数据集泛化失败确实需要先排除工程问题
- EMLS 零值处理是关键风险
- 项目叙事需要调整

### 采纳项

- [x] 保存 GPT 审查回复
- [x] 记录审查摘要到 gpt_review_log.md
- [ ] 修改项目主叙事（需要用户确认）
- [ ] 重跑 HABs GroupKFold（需要更多时间）
- [ ] Lake Erie A1/A2 版本分离（需要更多时间）
- [ ] EMLS 零值 sensitivity 分析（需要更多时间）
- [ ] 跨数据集 pipeline 审计（需要更多时间）

### 未采纳项

- 暂无。GPT 的所有建议都合理。

### 需要进一步验证项

1. 蓝藻叶绿素的测量时间（同步 vs 前置）
2. 跨数据集 R²=-19M 是否为工程 bug
3. EMLS 零值的真实含义
4. HABs GroupKFold 结果
