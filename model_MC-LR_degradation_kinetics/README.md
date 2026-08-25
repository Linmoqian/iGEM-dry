# model_MC-LR_degradation_kinetics —— 目录说明

MC-LR 降解动力学模型（干实验板块）：通过 MC-LR 降解推演预测，决定工程菌投放剂量与治理时间。

## 目录结构

| 路径 | 内容 |
|---|---|
| `report/01_文献综述_MCLR降解动力学.md` | **板块1**：文献调研（标题/链接/简介/方法思路；12 篇 OA 全文已下载 + 2 份 Figshare 补充数据） |
| `report/02_模型架构设计报告_MCLR降解动力学.md` | **板块3**：模型架构（32 轮评审记录、图文并茂、选择理由、优缺点、未来方向；v1.1 含文献层数值校准） |
| `report/03_模型教学详解_MCLR降解动力学.md` | **教学文档**：新手向全流程讲解（每个模块的选型原因与作用、批判性阅读提示、模块选型速答表） |
| `report/04_交付物质量审查报告.md` | **2026-08 第三方审查**：逐字核对原文/代码/数字的验证方法与结论（A/B/C 分级问题清单 + 修复优先级） |
| `report/05_五模型管线协同调研与降解模型适配评估.md` | **五模型管线视角**：用户补充数据核查（D16–D18）、接口契约核对、适配评估（3+2 项调整）、传统数学优劣势、v1.2→v1.3→联动路线图 |
| `data/数据集调研_MCLR降解.md` | **板块2**：数据集调研（名称/内容/适配度/链接/下载情况；D11–D18，其中 D16–D18 为用户 2026-08-22 补充下载） |
| `data/raw/` | 已下载原始数据（USGS MidTN HABs 5 CSV、NCBI microcystinase fasta、**USGS 微宇宙 5 表**、**Figshare EST2025 SI**、**Frontiers mlr SI**） |
| `data/processed/` | 团队自论文重构/拟合数据（YF1 RSM 17 组、m6 速率矩阵、Klebsiella 矩阵、USGS k 估计、**Mendeley 时间序列与 k 估计**、环境修正拟合参数表、文献参数先验表） |
| `data/data_manifest.csv` | 数据清单（文件-来源-下载状态 一一对应） |
| `references/` | 文献全文 PDF 统一存放处（12 篇；另有 `_extracted_text/` 为文本提取缓存） |
| `figures/` | 架构图与验证示意图（fig1–fig6 由 `src/prototype_v1.py` 生成；fig7 文献校准图由 `src/fit_literature.py` 生成；fig8 管线接口图由 `src/fig8_pipeline.py` 生成） |
| `src/prototype_v1.py` | 原型代码（机理 ODE + 环境修正 + 不确定性蒙特卡洛；可运行复现 fig1–fig6） |
| `src/fit_literature.py` | 文献校准代码（CTMI/非对称高斯/RSM 对比/USGS k；输出 fig7 + 两张参数表，可运行复现） |
| `src/extract_mendeley_mclr.py` | 用户补充数据（Mendeley）提取：时间序列 + 表观 k（含删失标识） |
| `src/extract_lake_erie_ratios.py` | 用户补充数据（Lake Erie 2018-19）：MC-LR/总MC 比例 + 胞内/胞外池比例 |
| `src/fig8_pipeline.py` | 五模型管线接口图生成（fig8，报告 05 配图） |

v1.1 说明：新增 **USGS 微宇宙降解时间序列（DOI 10.5066/P9DL080Y）** 等 3 组真实数据下载；环境修正函数完成文献层数值校准（f_T 改用 CTMI 温型、f_pH 改用非对称高斯，见 02 号报告 §12.1）。

## 一句话结论

**五模型管线定位（2026-08 协同调研结论，详见报告 05）**：降解模型是管线中的**反应核服务**——上游标定/预测模型给 C0 与触发，水流模型给投放点/覆盖/漂移，路径规划给到达时刻与投递包数；当前架构（灰箱内核）适应但需 3 项接口适配（服务化 API、斑块级空间参数化、投放时滞）与 2 项先验更新（k_bg 分层、C_intra 默认开启）；**先完成 v1.2 数字换锚（报告 04 A1–A4 + 报告 05 A5/A6），再启动管线联调**。

全网无现成"工程菌降解 MC-LR 动力学"数据集（文献速率跨 3–4 个数量级），因此采用 **灰箱混合架构**（机理 ODE 内核 + 层次贝叶斯校准 + 机会约束剂量决策 + ML 代理），并以"文献提取数据（已完成）+ 建议湿实验设计（见数据报告 §4）"双轨补齐数据。

## 复现

```bash
python src/prototype_v1.py   # 生成 figures/ 下 fig1–fig6 (架构与机理示意图)
python src/fit_literature.py # 生成 figures/fig7 与 data/processed/ 两张校准参数表
```

首次运行需：`pip install numpy pandas scipy matplotlib`（fit_literature.py 用 pandas 读取各提取 CSV）。
