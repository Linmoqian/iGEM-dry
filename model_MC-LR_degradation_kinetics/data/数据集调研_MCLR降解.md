# MC-LR 降解动力学模型 —— 数据集调研与下载报告

> 干实验子任务：MC-LR 降解动力学模型构建的前期调研（板块 2）
> 目标：寻找可用于"菌株/酶降解 MC-LR 的动力学建模"的数据集；记录名称、内容、适配程度、下载链接；实际下载并在本文档写明结果。
> 数据文件存放：`./raw/`（原始下载）、`./processed/`（本团队从论文提取/重构的曲线数据）。

---

## 0. 结论速览（TL;DR）

1. **全网不存在**面向"工程菌降解 MC-LR 动力学"的现成数据库/开放数据集——这一细分方向的所有定量数据都以论文图/表形式存在（这与检索到的综述与 30+ 篇论文的"数据可用性声明"一致：要么"作者提供"，要么只给图）。**2026-08 复查轮的最新进展：新找到两批"毒素浓度-时间序列"级公开数据并成功下载（D11/D12/D13），把"仅有终点速率/去除率"推进到"可拟合真实降解曲线"（D11 尤其关键）。**
2. **最能直接支撑建模的三类数据已落地**：
   - ✅ **USGS/Tennessee 水库 2022–2024 微囊藻毒素实测数据集**（已下载 5 个 CSV，含 MC 浓度、SPATT 被动采样、原位水质、eDNA）——用于"环境条件（温度 pH 等）与 MC 水平"耦合校准；
   - ✅ **文献重构数据集**（本团队从两篇 OA 论文中提取并制作 CSV，含完整出处）：YF1 响应面 17 组降解实验 + m6 环境因子速率矩阵 + 全文献动力学参数表；
   - ✅ **NCBI 微囊藻酶（microcystinase/MlrA）蛋白序列库**（17 条，可用作同源比对与活性推断的特征来源）。
3. **标注为"受限/失败"的下载**（本文档如实记录，并给出人工下载路径）：Mendeley Data（需 API key）、NOAA NCEI 0276941（JS 下载页 / FTP 超时）、Ohio Sea Grant live/water（门户站点）、NCBI SRA 原始测序（需 sra-tools 且与降解动力学无关）。
4. **最大缺口**：本项目自己的降解菌（mlr 基因簇）降解实验数据尚不存在 → 本报告给出**推荐实验设计（Table/方案）**，使模型可从"文献先验"平滑切换到"湿实验校准"。

---

## 1. 数据集清单（总表）

| # | 名称 | 来源/链接 | 内容 | 适配程度（1–5★） | 下载状态 |
|---|---|---|---|---|---|
| D1 | MidTN HABs：SPATT/水样毒素+水质数据 (USGS, 2022–2024) | [ScienceBase 67869215d34e60ddd4de1fdb](https://www.sciencebase.gov/catalog/item/67869215d34e60ddd4de1fdb)，DOI [10.5066/P13Q2TD5](https://doi.org/10.5066/P13Q2TD5) | 微囊藻毒素（ELISA）、CYL/ATX/SAX、SPATT 被动采样浓度、水温/pH/溶解氧/浊度/叶绿素等原位水质、站点信息、eDNA | ★★★★（环境耦合校准首选；非降解动力学实验） | ✅ 已下载 5 个 CSV（见 §2.1） |
| D2 | Lake Erie 总微囊藻毒素+水质数据 2013–2024 (NOAA NCEI 0276941) | [NOAA NCEI 0276941](https://www.ncei.noaa.gov/archive/accession/0276941) | 总 MCs、叶绿素、水质多年序列 | ★★★（环境浓度长序列；与 [10.1002/lno.12096](https://doi.org/10.1002/lno.12096) 的降解速率研究同水域） | ⚠️ 自动下载受限（JS 下载页 + FTP 超时）；可浏览器下载 zip |
| D3 | Ohio Sea Grant / Stone Lab Lake Erie live/water 门户数据 | [live/water](https://ohioseagrant.osu.edu/research/live/water) | 湖上监测浮标/手动采样的水质+毒素时间序列（[10.1002/lno.12096](https://doi.org/10.1002/lno.12096) 官方数据可用性声明指向） | ★★★ | ⚠️ 门户型站点（WQDataLive），需人工浏览导出 |
| D4 | Mendeley Data：Filterable bacterioplankton able to degrade microcystin 原始数据 | [Mendeley tx76zz3gt3/1](https://data.mendeley.com/datasets/tx76zz3gt3/1)，DOI [10.17632/tx76zz3gt3.1](https://doi.org/10.17632/tx76zz3gt3.1) | MC-LR 生物降解实验浓度数据 + 16S/宏基因组细菌群落表征 | ★★★★（**罕见"生物降解实验浓度+群落"组合**） | ⚠️ 下载需 Mendeley API key（页面 401）；API 公开端点 404；见 §2.4 人工路径 |
| D5 | NCBI 蛋白库：microcystinase / MlrA 序列 | [NCBI E-utilities](https://eutils.ncbi.nlm.nih.gov)（db=protein，query `(microcystinase[All Fields] AND mlrA[All Fields])`） | 17 条微囊藻酶 A/C 蛋白序列（Sphingopyxis、Sphingorhabdus、Roseateles、Stenotrophomonas、Petrimonas 等） | ★★★（序列特征→活性/株系参数先验；不提供速率数据） | ✅ 已下载 `raw/NCBI_mlrA_microcystinase_proteins_v2.fasta` |
| D6 | 论文 Table 2 重构：YF1 Box-Behnken 响应面降解实验 | [Toxins 2022, 14, 240](https://doi.org/10.3390/toxins14040240) Table 2 | 17 组（温度 20/30/40℃，pH 5/7/9，MC-LR 1/3/5 μg/mL）60 min 降解率 29.7–100% | ★★★★★（**降解率 vs 多环境因子的完整设计矩阵**——环境修正函数校准金标准） | ✅ 团队提取为 `processed/YF1_RSM_BBD_17runs_extracted.csv` |
| D7 | 论文 Figure 3 重构：m6 环境因子速率矩阵 | [Toxins 2018, 10, 536](https://doi.org/10.3390/toxins10120536) Fig.3 | 1–50 μg/L 六种初始浓度、四种温度、五种 pH 下的平均降解速率 (μg/L/h) | ★★★★★（**环境相关浓度下的真实速率-因子关系**，接近一级 k≈0.25 h⁻¹） | ✅ 团队提取为 `processed/m6_environment_rate_matrix_extracted.csv` |
| D8 | 全文献动力学参数表（curated） | 本报告 01 号文档 §3 + 11 篇 OA 全文 | 9 类体系（整细胞/酶/原位菌群/生物膜）的 k、半衰期、速率、条件 | ★★★★★（**贝叶斯先验/初始参数集**） | ✅ 团队构建为 `processed/literature_kinetic_parameters.csv` |
| D9 | NCBI SRA：微囊藻降解菌基因组/测序数据 | [SAMN13494103](https://www.ncbi.nlm.nih.gov/sra?term=SAMN13494103) 等 | Lake Erie Pseudomonas 等降解菌 WGS | ★★（菌株基因组，与动力学速率无直接关联；可用于基因组/代谢潜能分析） | ⚠️ 仅查录元数据；原始 reads 需 sra-tools 且体积 GB 级 |
| D10 | 本项目湿实验：降解菌降解曲线（**待产生**） | — | C(t)、B(t)（OD600/CFU）、残留子产物、T/pH/DO/光强记录 | ★★★★★（最终校准数据） | ⏳ 未产生；§4 给出推荐实验设计 |

---

## 2. 数据集详情与下载情况

### 2.1 ✅ D1 —— USGS MidTN HABs（Tennessee 水库 SPATT + 水质 + 毒素）
- **内容**：5 个已下载文件
  - `1_MidTN_HABs_site_list.csv` —— 站点信息（水库/井，2022–2024）；
  - `2_MidTN_HABs_QW_field_data.csv` —— 现场水质参数（温度/电导/pH/DO/浊度/叶绿素等，逐次采样）；
  - `5_MidTN_HABs_MC_conc_SPATT.csv` —— **SPATT 被动采样器提取液微囊藻毒素浓度**（时间序列）;
  - `6_MidTN_HABs_MC_conc_water.csv` —— **水样中微囊藻毒素浓度**（时间序列）;
  - `8_MidTN_HABs_eDNA.csv` —— 环境 DNA（藻类/毒素合成基因标记）。
- **下载方式**：ScienceBase 文件接口 `https://www.sciencebase.gov/catalog/file/get/67869215d34e60ddd4de1fdb?f=__disk__...`（API 返回完整文件清单后逐个 GET），共 5 个文件 69.5 KB 全部成功。
- **适配程度 ★★★★**：这是**真实湖库中 MC 浓度 + 同步水质**的稀缺公开数据，可用于：(a) 环境条件（T/pH/chl-a）对 MC 水平的实测耦合；(b) 为环境修正函数 f_T/f_pH 提供现场分布先验；(c) 与 Lab 降解动力学联合评估"现场可达速率"；**局限**：无"投菌后的降解时间序列"，不能直接拟合降解动力学。

### 2.2 ⚠️ D2 —— NOAA NCEI 0276941（Lake Erie 2013–2024）
- **内容**：总微囊藻毒素（ELISA/LC-MS 混合方法）、叶绿素及其他水质数据的多年月度/事件序列（对应 [10.1002/lno.12096](https://doi.org/10.1002/lno.12096) 研究区域）。
- **下载尝试记录**：`GET /archive/accession/0276941` 为 JS 渲染下载页（无直链）；`/archive/accession/download/276941` 返回"Download accessions"脚本页；`ftp-oceans.ncei.noaa.gov/nodc/archive/arc0211/0276941/`（FTP 镜像）超时；`/1.1/`、`manifest.json` 等路径均返回 prd Error。
- **结论/建议**：需在浏览器中打开数据页（或使用 NCEI 的 [OAS 下载向导](https://www.ncei.noaa.gov/archive/accession/0276941)）下载 zip；由于该数据集与 D3（Ohio Sea Grant）同源，也可以从 D3 门户取得近似数据。**（2026-08 复查：页面 200 可访问，但数据仍仅提供 ftp://ftp-oceans.ncei.noaa.gov/nodc/archive/arc0211/0276941/ 与 OAS wizard 两条路径；无 HTTP 直链——维持 ⚠️ 记录；其核心降解速率信息已由 [10.1002/lno.12096](https://doi.org/10.1002/lno.12096) 全文+新下载的 USGS 微宇宙数据替代。）**

### 2.3 ⚠️ D3 —— Ohio Sea Grant / Stone Lab live/water
- **内容**：湖水水质+毒素在线/离线监测（伊利湖）；[10.1002/lno.12096](https://doi.org/10.1002/lno.12096) 的数据可用性声明指定的公开来源。
- **下载尝试记录**：门户页面加载 200，但数据经由 **WQDataLive**（`http://wqdatalive.com/public/64`）提供——需要用户交互选择时间范围导出 CSV；自动化导出接口未公开。
- **建议**：人工在 wqdatalive 项目页面导出 2018–2019 夏季近岸站点数据（与湖中降解速率实验同期）。

### 2.4 ⚠️ D4 —— Mendeley Data tx76zz3gt3
- **内容**（页面描述原文翻译）：对应论文 *Filterable bacterioplankton able to degrade microcystin* 的原始数据，包含：**MC-LR 生物降解实验的浓度数据** + 细菌群落 16S/宏基因组数据（用于表征可能参与 MC 生物降解的群落）。
- **下载尝试记录**：4 个文件 ID（aeb7f197-…/2901e90a-…/20cd3e9d-…/792550dd-…）均无法通过公开端点下载：`data.mendeley.com/public-files/datasets/tx76zz3gt3/files/{id}/download` → **404**；`api.mendeley.com/datasets/tx76zz3gt3/files` → **401 Unauthorized**（需注册 API key）。
- **结论/建议**：① 在 Mendeley Data 页面注册免费账号后于网页端"Download All"；② 或向作者（Universidade Federal do Rio de Janeiro 组）索取；③ 记录：本数据集若到手，是"生物降解浓度-时间"数据的**首个外部来源**，建议优先争取。对应论文线索：*Filterable bacterioplankton able to degrade microcystin*（同一小组 2020s 论文）。

### 2.5 ✅ D5 —— NCBI microcystinase / MlrA 蛋白序列
- **检索**：NCBI E-utilities `esearch(db=protein) query=(microcystinase[All Fields] AND mlrA[All Fields])` → 17 条；`efetch rettype=fasta`。
- **内容**：Microcystinase C（MlrC, UniProt Q93CA6）、微囊藻酶 A（MlrA, 部分序列，Sphingopyxis sp.）、微囊藻酶（Roseateles toxinivorans、Stenotrophomonas sp. EMS、Sphingorhabdus sp.、Petrimonas mucosa 等）。
- **适配程度 ★★★**：用于 (a) 同源比对——判定"本项目工程菌 mlrA 与已知高活性株的序列相似度"并借用其文献速率作为先验；(b) 序列-活性映射（未来 ML 特征）；(c) **不提供速率/动力学数据**。
- **注意**：NCBI 中"mlrA"词名同时命中"转录调控因子 MlrA"（Salmonella 等），检索时必须用 `microcystinase` 关键词限定（本数据集已如此处理）。

### 2.6 ✅ D6/D7/D8 —— 团队从论文重构/整理的动力学数据集（高优先级）
- **D6** `processed/YF1_RSM_BBD_17runs_extracted.csv`：源 [Toxins 2022, 14, 240](https://doi.org/10.3390/toxins14040240) Table 2（17 runs；已将编码 -1/0/+1 译回 T/pH/浓度实际值）。
- **D7** `processed/m6_environment_rate_matrix_extracted.csv`：源 [Toxins 2018, 10, 536](https://doi.org/10.3390/toxins10120536) Figure 3（浓度/温度/pH → 平均速率 μg/L/h）。
- **D8** `processed/literature_kinetic_parameters.csv`：11 篇 OA 全文 + 已核验摘要中提取的 k/半衰期/速率（详见报告 01 §3）。
- **适配程度 ★★★★★**：D6 可直接拟合"RSM 二次型环境修正函数"；D7 可直接标定"环境浓度段的一级系数与 f_T/f_pH 形状"；D8 用作贝叶斯先验。**局限**：均为"平均速率/终点去除率"型数据，缺少多时间点曲线（需要时可用 WebPlotDigitizer 从 D6 论文 Figure 1–3 进一步数字化成完整曲线）。

### 2.7 ⚠️ D9 —— NCBI SRA 降解菌基因组
- **检索**：`SAMN13494103`（Whole genome sequencing of microcystin degrading Lake Erie Pseudomonas）等；SRA runinfo 接口返回 400（参数格式变化），更推荐用 [Bioproject 页面](https://www.ncbi.nlm.nih.gov/bioproject) 手工查询。
- **适配程度 ★★**：基因组有助于 (a) 确认 mlr 基因簇完整性/同源性；(b) 代谢潜能分析；**无法直接提供降解速率**；下载原始 reads 需 sra-tools，体积 GB 级，不建议纳入本项目最小数据集。

### 2.8 其他已核验但未纳入的候选（说明）
- **EPA/州级 HABs 数据库**（伊利湖、五大湖）：与 D2/D3 重叠，且上一阶段模型（`model/`）已使用 Lake Erie 数据集（cleaned parquet 在仓库 `model/data/cleaned/`），本次不再重复下载；
- **Kaggle 检索结果**：无 MC-LR 降解动力学专数据；
- **USGS ScienceBase 其他 SPATT 数据集**（NJ Salem River、NY Finger Lakes、North Atlantic Appalachian）：与本项目东湖场景关联较弱，仅记录（NJ：[item](https://www.sciencebase.gov/catalog/item/65f4b43ad34ebfb8e1679c9f)）。

---

### 2.10 ✅ 用户补充数据核查（2026-08-23）：D16–D18（详见 05 号报告 §1）

#### D16 —— Mendeley：Filterable bacterioplankton（微囊藻素降解滤过菌群）原始数据（✅ 已下载 38.5 MB）
- 来源：https://data.mendeley.com/datasets/tx76zz3gt3/1（§2.4 曾记录 API 401/404 需人工，用户已人工下载成功）。
- 内容：12 sheets；核心 sheet MC-LR raw data_submit（4 处理组 × 6 次采样事件 × rep1-3/mean/SD，raw ng/mL + %remaining），另有 16S OTU + PICRUST（Nov16/Nov17）。
- 团队提取（src/extract_mendeley_mclr.py）：processed/Mendeley_filterable_MCLR_time_series.csv（32 行）+ Mendeley_MCLR_apparent_k_estimates.csv（12 行，含删失标识）。
- 关键结论：灭活对照 ≤0.026 d-1（7 天无降解）；<0.22 µm 0.17–0.64 d-1；<0.45 µm 0.22–≥0.77 d-1（5/6 次事件 7 天内≤LOD）；季节差异显著（2016-05 无降解）。
- 适配程度 ★★★★★（k_bg 分层先验第一层；季节协变量证据）。

#### D17 —— Lake Erie 水质/毒素数据（用户下载 2 个 xlsx）
- waterqualitysamplingdata2018-2019habs.xlsx（274 行 × 50 列：全 MC 变体 LCMSMS + 总MC/胞外 MC + qPCR mcyE/sxtA + 营养盐）+ waterqualitydata2013-2022.xlsx（2139 行 × 43 列长序列）。
- 团队统计（src/extract_lake_erie_ratios.py）：MC-LR/总MC 中位 0.278（IQR 0.219–0.362，P90 0.532）；总MC P50/P90/P95=1.30/6.88/11.02 µg/L；MC-LR P50/P90/P95=0.35/1.50/2.43 µg/L；胞外比例中位 0.10 → 胞内(藻结合)中位 0.90。
- 适配程度 ★★★★★（f_LR 站点先验、C_intra 开启依据、C0 场景库）。

#### D18 —— 武汉东湖 2009 水华 MC 论文（用户下载 PDF）
- 固相萃取-高效液相色谱法测定武汉东湖水体中微囊藻毒素.pdf（贺小敏等，中国环境监测 2012, 28(1):53）。
- 数据：2009-08 官桥湖水华 6 点 MC-LR = 2.85/1.01/0.43/0.29/0.27/0.25 µg/L；MC-RR = 0.67/0.24/ND×4；检出限 MC-LR 0.0234 µg/L。
- 适配程度 ★★★★（东湖 C0 包络 + 站点 f_LR（LR 主导）+ 抑藻后毒素释放缓慢的胞内池现场证据）。

---


### 2.9 ✅ 本轮复查新增（2026-08）：D11–D15

#### D11 —— USGS：微囊藻降解菌微宇宙实验数据（Lake Erie 水源/砂滤水，2015–18）
- **名称/DOI**：*Microcosm experiment data of microcystin-degrading bacteria in Lake Erie source waters and drinking-water plants, 2015-18*，**DOI [10.5066/P9DL080Y](https://doi.org/10.5066/P9DL080Y)**（USGS data release，Francy & Cicale 2024）。
- **内容**（ScienceBase 下载的 zip，5 个表 + 元数据）：
  - *Table 1*：微宇宙（4 种水源样 + 砂滤样）MC-LR 浓度随时间的 ELISA 实测（T0/T1/T2/T4/T8/T14，µg/L，含重复与复加样）；
  - *Table 2*：10 株潜在降解菌 96 h 微板生长曲线（吸光度，多种富集培养基）；
  - *Table 3*：10 株菌生物膜形成潜力（A595）；
  - *Table 4*：MC-LR 为唯一碳源的 96 h 生长（A595 T0/T8）；
  - *Table 5*：微板孔 MC-LR 8 天浓度（ELISA，T0/T8，正/负对照 + 6 株分离株）。
- **适配程度 ★★★★★**：当前唯一可下载的"真实水样-天然降解菌-毒素浓度时间序列"数据；Table 1 的 T4→T8 段与 Table 5 的 8 天衰减可直接拟合表观一级 k（已提取为 processed/USGS_microcosm_apparent_k_estimates.csv，作为背景/天然菌群降解 k_bg 的实测先验：中位 k≈0.073 d⁻¹，区间 0–0.56 d⁻¹）。
- **下载情况**：✅ 成功（raw/USGS_Microcosm_MCLR_degraders_2015-18/，zip 12.1 KB + 5 CSV + Metadata.xml 41 KB；ScienceBase file/get 接口直接返回 zip，无需登录）。
- **局限**：微宇宙为"富集-复加"设计（Table 1 含多次投加段，ND=低于检出限），拟合需按段切分；菌株为天然分离株而非本项目工程菌。

#### D12 —— Figshare：蓝藻次级代谢物生物转化动力学与产物（EST 2025 SI）
- **名称**：*Biotransformation Dynamics and Products of Cyanobacterial Secondary Metabolites in Surface Waters*（Wang, Ingold & Janssen，Environ. Sci. Technol. 2025，[10.1021/acs.est.5c09247](https://doi.org/10.1021/acs.est.5c09247)）补充数据；Figshare 文章号 [30170897](https://figshare.com/articles/dataset/Biotransformation_Dynamics_and_Products_of_Cyanobacterial_Secondary_Metabolites_in_Surface_Waters/30170897)。
- **内容**：es5c09247_si_002.xlsx（3.3 MB）：40 种蓝藻环肽（含多种微囊藻素异构体）在表层水/原位富集生物膜中的生物转化与产物质谱数据（MetaboliteList、MC-LL、MC-YR_TP1-3、MC-LR_TP1、Anabaenopeptin TP1-4 等 sheet）。
- **适配程度 ★★★**：① 结构-反应性关系：微囊藻素仅 Adda-Arg 连接时生成四肽（MC-LR/YR/RR 可水解），Adda-Leu/Tyr 连接（如 MC-LL）不水解——支撑"底物特异性"先验与多毒素扩展；② 生物膜密度↑→滞后期↓、初始浓度↑→滞后期↑（自抑制证据）；③ 局限：xlsx 主体为 MS2 谱/产物鉴定表（动力学主数据在论文正文图内），需人工数字化进模型。
- **下载情况**：✅ 成功（Figshare 公开 API v2 + ndownloader.figshare.com/files/58109633）。

#### D13 —— Figshare：Lake Erie 与太湖微囊藻素生物降解分子机制（Frontiers SI）
- **名称**：*Data_Sheet_1_Insight Into the Molecular Mechanisms for Microcystin Biodegradation in Lake Erie and Lake Taihu*（Krausfeldt et al., Front. Microbiol., [10.3389/fmicb.2019.02741](https://doi.org/10.3389/fmicb.2019.02741)；Figshare [11345129](https://figshare.com/articles/dataset/Data_Sheet_1_Insight_Into_the_Molecular_Mechanisms_for_Microcystin_Biodegradation_in_Lake_Erie_and_Lake_Taihu_xlsx/11345129)）。
- **内容**：宏转录组/宏基因组拼接 mlrA/mlrB/mlrC contigs 与同源比对（E-value、identity%），含核苷酸序列。
- **适配程度 ★★★**：① 天然湖泊中 mlr 基因被表达（支持诱导型酶表达 E(t) 状态）；② 序列同源性→株间层次先验；③ 不提供速率/浓度数据。
- **下载情况**：✅ 成功（raw/Figshare_Frontiers_LakeErieTaihu_mlr_expression/，63.5 KB）。

#### D14 —— 团队提取：Klebsiella sp. TA13/14/19 温度×pH 速率矩阵
- **来源**：[Toxins 2025, 17, 346 Tables 2 & 3](https://doi.org/10.3390/toxins17070346)（全文已下载）。
- **内容**：3 株 × (5 温度 × 3 MC 变体) + 3 株 × (5 pH × 3 MC 变体) 降解速率（mg/L/h，3 mg/L 初始、无菌营养培养基、UPLC 定量）。
- **适配程度 ★★★★**：首个既有高温上限又有碱性 pH 区间的完整速率矩阵；关键发现：Topt≥40℃（vs m6 的 30℃）、pH 6–10 平坦（max/min≤1.35，vs m6 强钟形）——"株间环境修正函数必须分层"的最强定量证据（写入架构报告 §5 与 §8.1）。
- **文件**：processed/Klebsiella_T_pH_rate_matrix_extracted.csv（由 src/fit_literature.py 重建，含出处）。

#### D15 —— 团队拟合：环境修正函数校准参数表 + USGS 微宇宙 k 估计
- **来源**：src/fit_literature.py 对 D6/D7/D14/D11 的数值拟合。
- **内容**：processed/fitted_env_correction_params.csv（14 行拟合记录：k_app、CTMI 温型四参数、非对称 pH 高斯、YF1 RSM 交互增益、微宇宙 k 分布）+ processed/USGS_microcosm_apparent_k_estimates.csv（7 行）。
- **适配程度 ★★★★★**：把"文献先验"推进为"已校准参数"（详见架构报告 §12.1）。

---

## 3. 数据适配度矩阵（模型模块 ↔ 数据）

| 模型模块 | 依赖数据 | 当前状态 |
|---|---|---|
| 机理内核（状态方程、级联步骤） | MlrA/B/C 底物谱、产物链 | ✅ A1/A7/A8 文献 |
| 环境修正 f_T/f_pH | 单因子/RSM 降解率矩阵 | ✅ D6/D7（可拟合） |
| 菌生长/死亡 | 生长曲线、光控自杀 δ(I) | ⚠️ 无本项目实测；文献（CQ5 Gompertz）可先验 |
| 酶表达诱导 | mlrA 表达 fold-change | ⚠️ 仅 m6/THN1 文献定性+半定量 |
| 剂量-时间决策 | 酶/菌剂量→速率 | ✅ A4（MlrA 0.8 mg/L 两次投加） |
| 现场环境条件 | 真实湖库 T/pH/MC 时间序列 | ✅ D1（东湖数据可后续替换） |
| 湿实验校准 | 本项目降解菌 C(t)/B(t) | ⏳ 待实验（§4 设计） |
| 参数先验 | 跨文献 k 分布 | ✅ D8 |

---

## 4. 未覆盖的"金数据"：推荐湿实验设计方案（模型校准用）

> 说明：这是数据调研最重要的产出之一——公开数据不足，**必须由自实验补齐**，方案遵循 Box-Behnken + 时间序列的复合设计，兼顾效率与模型可辨识性。

1. **主设计（BBD/DoE）**：三因素三水平 Box-Behnken（温度 25/30/35℃、pH 6.5/7.5/8.5、初始浓度 1/5/20 μg/L）× 4 菌密度（0.5/1/2/4 × 基准 5×10⁸ CFU/mL），每条件≤3 生物重复 → 18–45 组，拟合"速率 = f(T,pH,C,D)"；
2. **时间序列补充（每组至少 6 个采样点）**：0/0.5/1/2/4/8/24 h；多时间点使"一级/Monod/诱导"模型可辨识（1 h 内细采样对诱导项尤其重要，m6 的 25 倍上调发生在首小时）；
3. **关键对照**：① 无菌对照（光解/水解背景）；② mlrA⁻ 菌株对照（验证通路贡献，类似 [10.1021/acs.chemrestox.3c00341](https://doi.org/10.1021/acs.chemrestox.3c00341) 的 CMS01 设计）；③ 暗/光对照（光控自杀模块的 δ(I) 标定，蓝光梯度 0/10/50/100 μmol/m²/s）；
4. **测量**：LC-MS/MS（MC-LR + 线性化产物）、OD600/CFU、mlrA qPCR（表达动态）、T/pH/DO 连续记录；
5. **数据格式**：长表 CSV（time, treatment_id, C, B, E_expr, T, pH, DO, light, replicate），与模型输入 schema 对齐（见架构报告 §10）。

---

## 5. 下载情况汇总（诚实记录）

| 数据集 | 计划 | 结果 | 文件/说明 |
|---|---|---|---|
| D1 USGS MidTN | 下载 9 个文件 | ✅ 成功 5/9（毒素/水质/eDNA/站点；另 CYL/SAX/几何元数据未下载，非必需） | `raw/1_…8_*.csv` 共 69.5 KB |
| D2 NOAA NCEI 0276941 | 下载 zip | ⚠️ 未成功 —— JS 下载页/FTP 超时/路径 404 | 建议浏览器下载 |
| D3 Ohio Sea Grant | 导出 CSV | ⚠️ 未成功 —— WQDataLive 需人工操作 | 建议人工导出 |
| D4 Mendeley tx76zz3gt3 | 下载 4 文件 | ❌ 未成功 —— API 需 key（401），公开端点 404 | 注册账号或联系作者；**高价值，建议争取** |
| D5 NCBI 蛋白序列 | 下载 fasta | ✅ 成功 17 条 | `raw/NCBI_mlrA_microcystinase_proteins_v2.fasta`（5.3 KB） |
| D6 YF1 RSM 重构 | 提取 Table 2 | ✅ 成功 17 runs | `processed/YF1_RSM_BBD_17runs_extracted.csv` |
| D7 m6 速率矩阵 | 提取 Fig.3 | ✅ 成功 15 行 | `processed/m6_environment_rate_matrix_extracted.csv` |
| D8 文献参数表 | 整理 | ✅ 10 类体系 | `processed/literature_kinetic_parameters.csv` |
| D9 NCBI SRA | 元数据 | ⚠️ 仅检索（raw reads 不在本地） | 需 sra-tools；不建议本项目使用 |
| D11 USGS 微宇宙 | 下载 zip | ✅ 成功（5 CSV + 元数据） | `raw/USGS_Microcosm_MCLR_degraders_2015-18/` |
| D12 Figshare EST SI | 下载 xlsx | ✅ 成功（3.3 MB） | `raw/Figshare_Biotransformation_Cyanopeptides_2025/` |
| D13 Frontiers mlr SI | 下载 xlsx | ✅ 成功（63.5 KB） | `raw/Figshare_Frontiers_LakeErieTaihu_mlr_expression/` |
| D14 Klebsiella 矩阵 | 提取 Tables 2&3 | ✅ 成功 45 行 | `processed/Klebsiella_T_pH_rate_matrix_extracted.csv` |
| D15 校准参数 | 数值拟合 | ✅ 14 行 + 7 行 | `processed/fitted_env_correction_params.csv`、`processed/USGS_microcosm_apparent_k_estimates.csv` |

**说明**：所有"⚠️/❌"均给出替代获取路径与原因，未有数据凭空声称已下载；本目录 `raw/` 中不存在任何未记录的下载文件（可在 [数据清单 manifest](./data_manifest.csv) 核对；manifest 与 `raw/`、`processed/` 中文件一一对应）。
