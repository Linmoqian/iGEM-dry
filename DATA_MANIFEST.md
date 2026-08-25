# 阶段快照数据清单

本仓库的阶段性交付以**源码、配置、报告、图件和轻量级实验摘要**为边界。为满足 GitHub 的单文件与仓库体积限制，下列本地资源不随 Git 推送；它们不是验收源码结构或已提交结论的前置条件。

| 模块 | 未随 Git 推送的内容 | 获取/复现说明 |
| --- | --- | --- |
| `model_concentration_calibration/` | `data/` 下的原始测量数据、`references/` 的论文 PDF | 阅读 `README.md`、`report/02_数据集调研与下载.md`；脚本会在本地数据到位后运行。 |
| `model_MC-LR_degradation_kinetics/` | `data/raw/` 与 `references/` 的原始资料 | 阅读模块 `README.md` 中的数据来源和复现命令。 |
| `model_Two-dimensional_water_flow/` | 水深、OSM、气象与流场中间数据 | 阅读模块 `README.md` 和 `data/` 下保留的数据说明。 |
| `model_path_planning/` | 原始任务数据、训练权重和大型运行产物 | 阅读模块 `README.md`；已提交的归档报告和轻量结果用于核验结论。 |
| `model_redo/`、`model_redo_v2/` | 外部数据表、下载论文、模型权重、预测明细 | 通过各模块的下载、数据准备和训练脚本在本地重建；保留的 JSON 摘要用于核验。 |
| `model_redo_v2_server_20260810/` | 服务器快照中的数据、论文、权重和运行缓存 | 该目录保留服务器环境所需的源码、配置与说明；数据准备方式见其 `README.md`。 |

此外，`design-assets/page-objectives-redesign/patches/generated/chrome-profile-*` 是本地浏览器自动化 profile，可能含会话状态，已明确排除。生成的页面图和设计资产仍会提交。

验收时应以仓库的冻结标签为准。若需要重新运行依赖原始数据的实验，请先按对应模块 README 中的数据来源与环境说明准备本地数据，再执行其中列出的命令。
