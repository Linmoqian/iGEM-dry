# pmlrA 启动子与 tig123 tiggerRNA 适配体的 MCLR 响应整合分析报告

## 摘要

本报告分析 `pmlra` 和 `tig123` 两组新数据。由于本批图片没有 0h 基线，本次不计算 0h 校正的 Δsignal，而直接以原始有效读数作为响应指标。`pmlra` 只使用前 3 列有效读数；`tig123` 当前文件夹内只有 0.5h 图片，因此只能做 0.5h 的横向比较，不能判断时间动态。

`pmlra` 的双因素 ANOVA 显示：MCLR 浓度效应 p = 7.01e-11 (***)，时间效应 p = <1e-12 (***)，浓度×时间交互 p = 0.9992 (ns)。
`tig123` 在 0.5h 的双因素 ANOVA 显示：MCLR 浓度效应 p = 0.5392 (ns)，trigger 类型效应 p = <1e-12 (***)，浓度×trigger 交互 p = 0.5876 (ns)。

总体上，`pmlra` 的时间变化明显，但是否具备稳定 MCLR 剂量响应需要看浓度效应和曲线单调性；`tig123` 在 0.5h 不同 trigger 的基础信号差异很强，但目前只有一个时间点，不能与 tig4567 那样评估完整时间响应。

显著性规则：ns: p ≥ 0.05；*: p < 0.05；**: p < 0.01；***: p < 0.001。

## 实验结论

### pmlrA 启动子

- MCLR 浓度效应：p = 7.01e-11 (***)。
- 时间效应：p = <1e-12 (***)。
- MCLR 浓度×时间交互：p = 0.9992 (ns)。
pmlrA 宽表中修正后的数据已同步到长表，本次统计基于修正后的 pmlrA 数值。当前结果显示 pmlrA 存在显著浓度效应和时间效应，但仍缺少 0h 基线，因此建议下一轮补 0h、空白扣除和 OD600 归一化后再判断定量性能。

### tig123 trigger0/1/2/3

- MCLR 浓度效应：p = 0.5392 (ns)。
- trigger 类型效应：p = <1e-12 (***)。
- MCLR 浓度×trigger 交互：p = 0.5876 (ns)。
因为当前 tig123 只有 0.5h，结论只能说明不同 trigger 在该时间点的信号水平和浓度差异，不能说明响应是否随时间持续或增强。

## 图与结果解读

### Figure 1. pmlrA 时间响应与 2.5h 终点剂量响应

![Fig1](figures_pmlra_tig123/Fig1_pmlra_response.png)

图 1a 展示 pmlrA 在 0.5-2.5h 的原始信号随时间变化。图 1b 展示 2.5h 终点的剂量响应。由于没有 0h，本图展示的是原始信号而不是 Δsignal。

### Figure 2. pmlrA 热图与 tig123 trigger 比较

![Fig2](figures_pmlra_tig123/Fig2_pmlra_tig123_overview.png)

图 2a 展示 pmlrA 在不同 MCLR 浓度和时间点的均值热图。图 2b 展示 tig123 在 0.5h 时 trigger0-3 的浓度响应。trigger 间基础信号差异较大，因此后续最好与更多时间点和归一化数据结合判断。

### Figure 3. 统计显著性摘要

![Fig3](figures_pmlra_tig123/Fig3_pmlra_tig123_statistics.png)

图 3a 显示 pmlrA 每个时间点 one-way ANOVA 的 p 值强度。图 3b 显示 tig123 每个 trigger 在 0.5h 下不同浓度之间 one-way ANOVA 的 p 值强度。

pmlrA 各时间点 one-way ANOVA：
- 0.5h: p = 0.0959 (ns)
- 1h: p = 0.0673 (ns)
- 1.5h: p = 0.0493 (*)
- 2h: p = 0.0354 (*)
- 2.5h: p = 0.0159 (*)

tig123 各 trigger one-way ANOVA：
- trigger0: p = 0.8481 (ns)
- trigger1: p = 0.0896 (ns)
- trigger2: p = 0.1568 (ns)
- trigger3: p = 0.6951 (ns)

## 后续建议

1. 请补齐 tig123 的后续时间点图片，或确认当前只需要 0.5h 横向比较。
2. pmlrA 建议补充 0h、空白扣除和 OD600 归一化，用于确认修正后浓度差异是否可重复。
3. 后续若要和 pmcy、tig4567 横向比较，应统一加入 0h、空白扣除和 OD600 归一化。
4. 当前所有统计均基于技术重复，最终结论需要独立生物学重复支持。

## 输出文件

- 统计分析表：`pmlra_tig123_statistical_analysis.xlsx`
- 图像文件夹：`figures_pmlra_tig123/`
