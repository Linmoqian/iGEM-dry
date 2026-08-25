# 高水平论文检索与模型架构适配评审

检索日期：2026-08-10  
证据范围：OpenAlex 学术元数据、论文原文、作者/机构官方仓库、模型官方文档。  
机器记录：`references/literature_search_results.csv/json`、`references/paper_download_manifest.csv/json`。

## 1. 检索方法与边界

本轮使用 20 组主题检索式，覆盖：

- 表格基础模型、深度表格模型、GBDT 与综合基准；
- IID、跨时间、跨分组和域偏移；
- 左删失/区间删失、概率回归、分位数与 conformal prediction；
- 微囊藻毒素、蓝藻水华、遥感和水质预测。

OpenAlex 返回并保存 240 条候选记录。随后按“同行评审级别、最新性、公开实现、任务直接相关性、可获得全文”人工精选 21 篇；17 篇 PDF 下载成功并通过 `%PDF` 文件头与 SHA-256 校验，4 篇领域论文因站点 403 未自动下载，但保留正式 DOI/页面。论文、预印本和技术报告在文档中分别标注。

“全量查询”在这里指对公开可检索来源进行宽主题、可复现的系统扫描，不代表任何单一数据库能够覆盖全世界所有论文。后续可在新模型或新数据出现时重跑脚本增量更新。

## 2. 最重要的证据结论

### 2.1 最新排行榜第一不等于本任务第一

[TabICLv2](https://arxiv.org/abs/2602.11139)（ICML 2026）报告其在 TabArena 与 TALENT 的分类/回归上达到很强的免调参表现，官方实现采用 BSD-3-Clause，支持缺失值、回归和量化回归微调；从样本数和特征数看，本项目约 2 万 × 138 列处于可运行范围。[官方仓库](https://github.com/soda-inria/tabicl)

但更贴近本项目的 [Beyond IID](https://arxiv.org/abs/2606.30410) 对 142 个数据集的 IID、temporal 和 grouped 任务进行比较，结论是表格基础模型主要在 tiny/medium IID 数据上占优，调优和集成后的传统树模型与深度模型在非 IID、较大和高维任务仍占优势。本项目存在来源、湖泊、国家和时间偏移，因此 TabICLv2 应是强挑战者，而不是未经实验直接指定的冠军。[BeyondArena 官方仓库](https://github.com/autogluon/tabarena)

### 2.2 GBDT 仍必须保留

[Why do tree-based models still outperform deep learning on typical tabular data?](https://arxiv.org/abs/2207.08815) 指出树模型在典型异构表格数据上更容易得到良好性能；[TabArena](https://arxiv.org/abs/2506.16791) 和 BeyondArena 又表明验证协议、调优与折后集成会显著改变排名。本项目有大量缺失、非平滑关系和不同特征面板，所以 CatBoost、LightGBM、XGBoost 不是“旧模型”，而是必须击败的强基线。

特别是 [XGBoost AFT 官方实现](https://xgboost.readthedocs.io/en/stable/tutorials/aft_survival_analysis.html) 原生接受标签下界与上界，可表达区间删失。尽管 AFT 最初用于生存时间，把正浓度作为区间响应需要做分布适配验证，但它是当前最容易复现的删失树模型比较器。

### 2.3 可训练深度模型比纯 Transformer 更适合自定义删失多任务

[TabM](https://arxiv.org/abs/2410.24210)（ICLR 2025）用参数高效的 MLP ensemble 获得强表格性能，结构简单、Apache-2.0 实现，便于加入：

- 精确值密度与删失区间概率联合损失；
- total MC / MC-LR 分析物嵌入和独立输出头；
- 来源均衡或 GroupDRO；
- 分位数、异方差和混合分布输出。

因此 TabM 比 FT-Transformer 更适合作为本项目的可修改深度骨干。[官方仓库](https://github.com/yandex-research/tabm)

[RealMLP / Better by default](https://arxiv.org/abs/2407.04491)（NeurIPS 2024）显示好的默认值使 MLP 能与 GBDT 竞争，并建议在中等预算下同时测试 NN 与 GBDT。PyTabKit 当前还提供多分位数回归，是很好的强基线与不确定度比较器。[官方仓库](https://github.com/dholzmueller/pytabkit)

### 2.4 概率输出和域偏移不能事后补一个误差条

- [NGBoost](https://proceedings.mlr.press/v119/duan20a.html) 提供条件分布预测，可作为异方差概率树基线，但没有直接解决左删失。
- [Conformalized Quantile Regression](https://arxiv.org/abs/1905.03222) 可包裹树或神经网络，在交换性假设下提供有限样本边际覆盖保证。
- [Conformal Prediction Under Covariate Shift](https://arxiv.org/abs/1904.06019) 提供在可估密度比条件下的加权校准思路，适用于利用大量无标签中国协变量。
- [GroupDRO](https://arxiv.org/abs/1911.08731) 说明只优化平均损失可能牺牲小来源，最差组训练还必须配合正则化。
- [WILDS](https://arxiv.org/abs/2012.07421) 强调真实域偏移下的专门验证集和最差组报告；这直接支持本项目的来源/湖泊/时间外切分。

注意：标准 CQR 的覆盖保证依赖交换性；跨国家、跨年代时不能直接声称保证仍成立。必须在来源/时间条件下报告经验覆盖，并将加权 conformal 作为敏感性方案。

### 2.5 领域文献支持多源数据，但不支持无条件合并

- [Harmful algal blooms in inland waters](https://doi.org/10.1038/s43017-024-00578-2)（Nature Reviews Earth & Environment, 2024）综合指出营养盐、气候、水文、生态过程和监测尺度共同影响内陆水华；支持多面板环境特征，而不是只靠一个水质变量。
- [Combining national and state data improves predictions of microcystin concentration](https://doi.org/10.1016/j.hal.2019.02.009) 直接说明组合国家和州级数据可以改善微囊藻毒素模型，但来源差异必须进入验证设计。
- [A systematic literature review of forecasting and predictive models for cyanobacteria blooms in freshwater lakes](https://doi.org/10.1016/j.watres.2020.115959) 说明“藻华预测”研究很多，但藻华/Chla 预测不等于毒素亚型浓度预测。
- [Investigating the Relationship Between Microcystin Concentrations and Water Quality Parameters ... Using Random Forest](https://doi.org/10.3390/w17162361)（2025）可用于近期特征假设，不足以据三个农塘决定全球模型架构。
- [Global elevation of algal bloom frequency in large lakes over the past two decades](https://doi.org/10.1093/nsr/nwaf011)（2025）支持遥感和长期季节背景的价值，但遥感藻华指标仍是代理特征，不是 MC-LR 真值。

检索还命中 2026 年的 [Leveraging interpretable machine learning to predict and understand microcystin dynamics in Lake Erie](https://doi.org/10.22541/essoar.15006820/v1) 和 2025 年的 [Prediction of Cyanobacteria Bloom in Taihu Lake Based on Time-Delay Response and Nonlinear Machine Learning](https://doi.org/10.2139/ssrn.5343308)。它们与本项目地域/任务接近，但当前属于预印本或 SSRN 工作，作为最新方向监测和特征假设来源，不作为架构胜负的高等级证据。

## 3. 候选模型逐项判断

以下 0–10 分是**设计期适配分**，综合删失、缺失、非 IID、可修改性、许可、计算和解释性，不是训练成绩。

| 模型/方法 | 设计分 | 优点 | 核心缺点 | 决策角色 |
|---|---:|---|---|---|
| XGBoost AFT | 9.0 | 原生上下界标签；成熟、快速、Apache-2.0 | 分布假设需验证；多任务与分位数灵活性有限 | 删失主基线/核心分支 |
| CatBoost + MultiQuantile | 8.8 | 缺失和类别处理强；多分位数；Apache-2.0 | 无原生左删失似然 | 强点/分位数树分支 |
| LightGBM quantile | 8.6 | 快、成熟、MIT；调参和集成方便 | 无原生区间删失；类别处理需谨慎 | 强树基线 |
| TabM（自定义损失） | 8.9 | 可改删失 NLL、多任务、GroupDRO；Apache-2.0 | 需 GPU/训练；小 MC-LR 源易过拟合 | 最终深度骨干 |
| TabICLv2 | 8.4 | 最新强免调参表格基础模型；BSD-3；缺失/回归/量化微调 | 原生推理不理解本项目删失区间；非 IID 未必领先 | 强挑战者与折外集成候选 |
| RealMLP / PyTabKit | 8.1 | 强默认、可多分位数、Apache-2.0 | 不直接处理删失；需插补/编码审计 | 深度强基线 |
| NGBoost | 7.3 | 输出完整条件分布；模块化 | 左删失需自定义；长尾分布选择敏感 | 概率基线 |
| TabPFN-3 | 6.8 | 2026 新一代 TFM；规模能力较强 | 2.5/2.6/3 权重为非商业许可，首次使用需接受许可/令牌；非 IID 仍需验证 | 仅研究对照，非默认交付 |
| TabR | 6.5 | 邻域检索能利用局部相似性；MIT | 相邻站点/日期跨折时极易泄漏；推理和索引成本 | 严格 group split 下的消融 |
| FT-Transformer | 5.8 | 经典、可修改 | 当前证据下不如新 MLP/TFM；计算更重 | 历史对照，不进主赛道 |
| TFT/LSTM/Chronos | 4.0 | 获得密集序列后适合多时距预测 | 当前大多数记录非连续序列，无法发挥优势 | 数据门槛满足后再启用 |
| 时空 GNN | 3.5 | 可表达湖泊/河网传播 | 目前没有稳定图边、连续图信号和东湖标签 | 暂缓 |

相关官方能力和许可链接：[TabPFN](https://github.com/PriorLabs/TabPFN)、[TabICLv2](https://github.com/soda-inria/tabicl)、[CatBoost regression objectives](https://catboost.ai/docs/en/concepts/loss-functions-regression)、[LightGBM objectives](https://lightgbm.readthedocs.io/en/stable/Parameters.html#objective)。

## 4. 最强可用架构的结论

不存在一个论文模型能同时原生解决“左删失 + 两种不等价分析物 + 多来源偏移 + 无标签中国迁移 + 概率校准”。因此最终候选应是组合架构：

1. XGBoost AFT 或自定义区间似然树负责删失分布基线；
2. CatBoost/LightGBM 负责强非线性树和多分位数；
3. TabM 负责可修改的删失多任务与来源稳健训练；
4. TabICLv2 作为最新公开基础模型挑战者；
5. 只使用折外预测学习非负集成权重；
6. 最后按外层来源/时间折做条件 conformal 校准和 OOD 拒绝。

如果实验显示一个简单 CatBoost 或 XGBoost AFT 在所有非 IID 门禁上领先，就应交付简单模型，而不是为了“先进架构”保留深度模块。复杂度必须用锁定实验换取。

## 5. 许可与可复现性判断

- TabICLv2：官方仓库为 BSD-3-Clause，适合默认研究与交付候选。
- TabM、CatBoost、XGBoost、PyTabKit：Apache-2.0；LightGBM、TabR：MIT。
- TabPFN：代码和部分旧权重许可与新权重许可不同；官方仓库说明 TabPFN-2.5/2.6/3 权重为非商业许可，且需要账户接受条款。除非项目明确接受对应许可并记录模型哈希，不进入默认生产流水线。
- 论文“可下载”不代表模型权重可任意商用；模型卡必须分别记录代码许可、权重许可和数据许可。

## 6. 仍需持续跟踪的研究方向

- 面向区间删失表格基础模型的直接微调方法；
- 非 IID 表格基础模型在 grouped/temporal 数据上的新版本；
- 多来源检测方法的测量误差模型与层次贝叶斯校准；
- covariate shift 之外的 label/concept shift 不确定度；
- 获得东湖序列后再比较 TFT、状态空间模型和时空图模型。
