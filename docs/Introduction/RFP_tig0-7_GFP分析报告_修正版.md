# RFP\_tig0\-7\_GFP分析报告\_修正版

RFP 内参归一化的 ths\-GFP/tiggerRNA 适配体 MCLR 响应分析报告

# 摘要

本次实验将 RFP 与 ths\-GFP 放在同一质粒中，因此以 GFP/RFP 作为主读数，用 RFP 校正菌量、质粒拷贝数和孔间表达背景差异；随后对每个 trigger、每个浓度和每个重复按 0h 做基线校正，得到 Δ\(GFP/RFP\)。统计分析使用每个 trigger 内的双因素 ANOVA，因素为 MCLR 浓度和时间；0h 作为校正基线，不纳入 ANOVA。每个浓度为 3 个技术重复。

综合统计显著性和响应幅度，当前最值得优先复测的是 **trigger1**：它同时具有最强的浓度效应统计证据和最大的峰值响应幅度。峰值出现在 2h、1 μg/L，峰值 Δ\(GFP/RFP\) = 0\.2147；**trigger0** 可作为第二候选。

显著性标记：ns: p \>= 0\.05；\*: p \< 0\.05；**: p \< 0\.01；**\*: p \< 0\.001。

# 方法

- 内参归一化：每孔计算 GFP/RFP。

- 基线校正：按相同 trigger、浓度和重复，计算 Δ\(GFP/RFP\) = \(GFP/RFP\)\_t \- \(GFP/RFP\)\_0h。

- 统计方法：每个 trigger 分别做双因素 ANOVA：Δ\(GFP/RFP\) \~ MCLR浓度 × 时间；每个时间点另做 one\-way ANOVA；与 0 μg/L 对照比较使用 Welch t\-test。

# 主要统计结果

|**trigger**|**MCLR 浓度效应**|**时间效应**|**浓度×时间交互**|**峰值时间**|**峰值浓度**|**峰值 Δ\(GFP/RFP\)**|
|---|---|---|---|---|---|---|
|trigger0|p=\<1e\-12 \*\*\*|p=\<1e\-12 \*\*\*|p=0\.4196 ns|2h|0\.25|0\.1936|
|trigger1|p=\<1e\-12 \*\*\*|p=\<1e\-12 \*\*\*|p=1\.0000 ns|2h|1|0\.2147|
|trigger2|p=\<1e\-12 \*\*\*|p=\<1e\-12 \*\*\*|p=0\.9584 ns|2h|5|0\.1711|
|trigger3|p=4\.52e\-05 \*\*\*|p=\<1e\-12 \*\*\*|p=0\.0597 ns|2h|0\.05|0\.1715|
|trigger4|p=\<1e\-12 \*\*\*|p=\<1e\-12 \*\*\*|p=1\.0000 ns|2h|1|0\.1466|
|trigger5|p=\<1e\-12 \*\*\*|p=\<1e\-12 \*\*\*|p=0\.9974 ns|2h|0\.5|0\.1408|
|trigger6|p=2\.02e\-06 \*\*\*|p=\<1e\-12 \*\*\*|p=0\.8317 ns|2h|1|0\.1450|
|trigger7|p=2\.15e\-05 \*\*\*|p=\<1e\-12 \*\*\*|p=1\.0000 ns|9h|1|\-0\.1309|



# 图与结果解读

## 图 1\. RFP 归一化后的时间响应曲线

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MGZmODEzNDYzNzE1MGY5NDJhNmQ2MjFkZmE3YjFhZTJfMzFhMmFhOWMzMmJmYTU1MTA0ODZkODg3ZmNiNWI1ZTZfSUQ6NzY1MjE5MjQyNjczMTUyMzA1MF8xNzg3MzMzNDg4OjE3ODc0MTk4ODhfVjM)

*Fig1*

图 1 展示每个 trigger 在不同 MCLR 浓度下的 Δ\(GFP/RFP\) 随时间变化。横轴使用真实采样时间，因此 9h 到 24h、24h 到 33h 的间隔不会被压缩成等距。该图用于判断响应是否随时间累积、是否出现早期响应，以及不同浓度曲线是否能拉开。

## 图 2\. trigger0\-7 的全局响应热图

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZmE0ODE1Njg0MzhiYWVjMWZkYjVmYjVmOWMyMDY4ZDdfZTJiZWI1MTRjMTg5NmU0NDc0YzllZTFmOWQ4MGIxYTNfSUQ6NzY1MjE5MjQyNTc2Mjk5OTI2NF8xNzg3MzMzNDg4OjE3ODc0MTk4ODhfVjM)

*Fig2*

图 2 将每个 trigger 的平均 Δ\(GFP/RFP\) 展示为浓度\-时间热图。颜色越偏绿表示相对 0h 的 GFP/RFP 增强，越偏紫表示降低。该图用于快速比较哪个 trigger 的响应幅度更大、响应区域是否集中在特定浓度或时间段。

## 图 3\. 24h 与 33h 终点剂量响应

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NjlmYzI2ODk0NGUwNTk3NzlhODc5OGEzNzBjNzY2MmFfMWIwN2Y5MGY3ZjU0MGM5NzFjOTA2OGQ1OWVhNzdlNmFfSUQ6NzY1MjE5MjQyNjQxMzAxODA5M18xNzg3MzMzNDg4OjE3ODc0MTk4ODhfVjM)

*Fig3*

图 3 比较 24h 和 33h 的剂量响应，并在每个小图中标出该时间点 one\-way ANOVA 的 p 值。若某个 trigger 在终点时间既有显著 p 值，又能形成可解释的剂量梯度，则更适合作为检测候选。

## 图 4\. 统计显著性与效应量摘要

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=N2Y5ODA4MzA0N2MzMjY1YjdkZWU5M2E3MGMzYjk3MjJfMjRhYzJmOGNkMDMwN2JlNmExZTFlNDllMDc2NTRiODBfSUQ6NzY1MjE5MjQyNDQ5MjMyMTc2MF8xNzg3MzMzNDg4OjE3ODc0MTk4ODhfVjM)

*Fig4*

图 4a 显示每个 trigger 的双因素 ANOVA 证据强度，颜色为 \-log10\(p\)，格内星号为显著性。图 4b 显示每个 trigger 的最大响应幅度及出现时间。统计显著但幅度很小的 trigger 不一定适合实际检测；幅度大但交互复杂的 trigger 需要进一步确认重复性。

# 结论

在 RFP 内参校正后，**trigger1** 同时表现出最稳定的 MCLR 浓度效应和最大的归一化响应幅度，是当前优先复测候选。**trigger0** 可作为补充候选。若后续目标是建立 MCLR 定量检测体系，建议优先围绕这些 trigger 进行重复实验，并保留同质粒 RFP 内参策略。

不过，本批数据仍来自照片提取，且只有技术重复。下一轮建议直接导出酶标仪原始 Excel/CSV，加入空白孔扣除、OD600 或 RFP 双重归一化，并设置独立生物学重复。

---

\[rfp\_tig0\-7\_extracted\_SOURCE\_CORRECTED\_33h\_clear\.xlsx\]

