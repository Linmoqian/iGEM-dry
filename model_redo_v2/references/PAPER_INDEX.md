# 论文与官方实现证据索引

检索/下载日期：2026-08-10。完整元数据和哈希见 `paper_download_manifest.csv/json`；宽检索结果见 `literature_search_results.csv/json`。

## 已下载并校验的论文

| 年份 | 论文 | 级别/状态 | 本项目用途 | 本地文件 |
|---:|---|---|---|---|
| 2026 | [TabICLv2](https://arxiv.org/abs/2602.11139) | ICML 2026 / arXiv | 最新公开 TFM 强挑战者 | [PDF](papers/2026_tabiclv2_2026.pdf) |
| 2026 | [Beyond IID](https://arxiv.org/abs/2606.30410) | 预印本 | grouped/temporal 非 IID 选择依据 | [PDF](papers/2026_beyond_iid_2026.pdf) |
| 2026 | [TabPFN-3 Technical Report](https://arxiv.org/abs/2605.13986) | 技术报告/预印本 | 最新 TabPFN 研究对照与许可审计 | [PDF](papers/2026_tabpfn3_2026.pdf) |
| 2025 | [TabArena](https://arxiv.org/abs/2506.16791) | NeurIPS 2025 Datasets & Benchmarks | 现代模型公平比较和外层重复设计 | [PDF](papers/2025_tabarena_2025.pdf) |
| 2025 | [TabICL](https://arxiv.org/abs/2502.05564) | ICML 2025 | TabICLv2 前代与中型表格 ICL 证据 | [PDF](papers/2025_tabicl_2025.pdf) |
| 2025 | [TabM](https://arxiv.org/abs/2410.24210) | ICLR 2025 | 自定义删失多任务深度骨干 | [PDF](papers/2025_tabm_2025.pdf) |
| 2025 | [Accurate predictions on small data with a tabular foundation model](https://doi.org/10.1038/s41586-024-08328-6) | Nature | TabPFN 高水平基础证据 | [PDF](papers/2025_tabpfn_nature_2025.pdf) |
| 2024 | [TabR](https://arxiv.org/abs/2307.14338) | ICLR 2024 | 检索式模型和近邻泄漏消融 | [PDF](papers/2024_tabr_2024.pdf) |
| 2024 | [Better by default / RealMLP](https://arxiv.org/abs/2407.04491) | NeurIPS 2024 | 强预调 MLP 与树基线 | [PDF](papers/2024_realmlp_2024.pdf) |
| 2024 | [A Closer Look at Deep Learning Methods on Tabular Datasets / TALENT](https://arxiv.org/abs/2407.00956) | arXiv benchmark | 表格模型与预处理大规模比较 | [PDF](papers/2024_talent_2024.pdf) |
| 2022 | [Why do tree-based models still outperform deep learning on typical tabular data?](https://arxiv.org/abs/2207.08815) | NeurIPS 2022 | 保留 GBDT 的理论/实证依据 | [PDF](papers/2022_tree_vs_dl_2022.pdf) |
| 2021 | [Revisiting Deep Learning Models for Tabular Data](https://arxiv.org/abs/2106.11959) | NeurIPS 2021 | FT-Transformer 历史对照 | [PDF](papers/2021_ft_transformer_2021.pdf) |
| 2021 | [WILDS](https://arxiv.org/abs/2012.07421) | ICML 2021 | 真实域偏移评价协议 | [PDF](papers/2021_wilds_2021.pdf) |
| 2020 | [NGBoost](https://proceedings.mlr.press/v119/duan20a.html) | ICML 2020 | 概率回归基线 | [PDF](papers/2020_ngboost_2020.pdf) |
| 2020 | [GroupDRO](https://arxiv.org/abs/1911.08731) | ICLR 2020 | 最差来源目标与正则化 | [PDF](papers/2020_group_dro_2020.pdf) |
| 2019 | [Conformalized Quantile Regression](https://arxiv.org/abs/1905.03222) | NeurIPS 2019 | 自适应预测区间 | [PDF](papers/2019_cqr_2019.pdf) |
| 2019 | [Conformal Prediction Under Covariate Shift](https://arxiv.org/abs/1904.06019) | NeurIPS 2019 | 中国无标签域的加权校准依据 | [PDF](papers/2019_conformal_covariate_shift_2019.pdf) |

## 已纳入评审但站点阻止自动 PDF 下载

以下页面/DOI 可正常定位，自动 PDF 请求返回 HTTP 403。未绕过站点限制；正式引用和用途已记录，下载失败不会被伪装为成功。

| 年份 | 论文 | 用途 | 官方入口 |
|---:|---|---|---|
| 2024 | Harmful algal blooms in inland waters | 领域综述、驱动因素与监测尺度 | [DOI](https://doi.org/10.1038/s43017-024-00578-2) |
| 2019 | Combining national and state data improves predictions of microcystin concentration | 多来源微囊藻毒素直接证据 | [DOI](https://doi.org/10.1016/j.hal.2019.02.009) |
| 2025 | Investigating the Relationship Between Microcystin Concentrations ... Using Random Forest | 最新任务特征假设 | [DOI](https://doi.org/10.3390/w17162361) |
| 2025 | Global elevation of algal bloom frequency in large lakes over the past two decades | 长期遥感/季节背景 | [DOI](https://doi.org/10.1093/nsr/nwaf011) |

## 关键官方软件与文档

- [TabICLv2 官方仓库](https://github.com/soda-inria/tabicl)：BSD-3-Clause；支持回归、缺失值和量化回归训练。
- [TabPFN 官方仓库](https://github.com/PriorLabs/TabPFN)：当前模型规模、认证与权重许可说明。
- [TabArena / BeyondArena](https://github.com/autogluon/tabarena)：IID、grouped、temporal 基准与模型实现。
- [TabM 官方仓库](https://github.com/yandex-research/tabm)：Apache-2.0。
- [TabR 官方仓库](https://github.com/yandex-research/tabular-dl-tabr)：MIT。
- [PyTabKit / RealMLP](https://github.com/dholzmueller/pytabkit)：Apache-2.0，多分位数回归。
- [XGBoost AFT](https://xgboost.readthedocs.io/en/stable/tutorials/aft_survival_analysis.html)：上下界标签和 interval censoring。
- [CatBoost MultiQuantile](https://catboost.ai/docs/en/concepts/loss-functions-regression)：分位数目标。
- [LightGBM objectives](https://lightgbm.readthedocs.io/en/stable/Parameters.html#objective)：quantile 等回归目标。

## 最新但未进入核心证据层的任务预印本

- [Leveraging interpretable machine learning to predict and understand microcystin dynamics in Lake Erie](https://doi.org/10.22541/essoar.15006820/v1)（2026，ESSOAr）：任务高度相关，但尚不与同行评审论文等权。
- [Prediction of Cyanobacteria Bloom in Taihu Lake Based on Time-Delay Response and Nonlinear Machine Learning](https://doi.org/10.2139/ssrn.5343308)（2025，SSRN）：可参考时滞特征设计；预测藻华不等于预测 MC-LR。

## 下载完整性

脚本对成功文件检查 PDF 文件头并记录 SHA-256。最终校验还应在环境锁定后再次用 PDF 解析器逐文件打开；论文仅用于研究评审，不应将全文复制进模型报告或训练数据。
