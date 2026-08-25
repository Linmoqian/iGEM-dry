# MC-LR 降解动力学模型 —— 文献综述报告

> 干实验子任务：MC-LR 降解动力学模型构建的前期调研（板块 1）
> 撰写日期：2026-08（模型架构报告请见同目录 `02_模型架构设计报告.md`）
> 目标：为「通过 MC-LR 降解推演预测，从而决定投放剂量与治理时间」的模型提供权威文献依据、可借鉴方法
> 与可复用的动力学参数。

---

## 0. 结论速览（TL;DR）

1. **全球范围内不存在**公开可下载的、面向"工程菌降解菌投放剂量→MC-LR 浓度随时间变化"的端到端降解动力学原始数据集；绝大多数动力学数据以**论文图/表**形式存在，需要人工数字化提取（本项目已从 2 篇关键论文中提取并重构为 CSV，见 `../data/`）。这是本模型建设的**首要数据缺口**。
2. **可直接借鉴的方法学模板已找到**：
   - `Water Research (2018) 10.1016/j.watres.2018.11.014` —— 用**非结构动力学模型（first-order / Monod）** 预测微囊藻毒素生物降解，是本模型"机理内核"的最直接先例；
   - `Annals of Microbiology (2019) 10.1007/s13213-019-01510-6`（Lysinibacillus CQ5）—— 完整给出 **Gompertz 菌生长 + 一级降解 + 修正 Monod（Vmax/Ks）** 三件套方程及实测参数；
   - `EST (2026) 10.1021/acs.est.5c16532` —— 生物沙滤中藻毒素降解的**表观一级速率常数 k_app、Arrhenius 活化能、动力学级数判定**的完整建模流程；
   - `Toxins (2022) 10.3390/toxins14040240`（Sphingopyxis YF1）—— **Box-Behnken 响应面（RSM）** 建立温度×pH×浓度→降解率的二次模型，可直接作为"环境修正函数"的经验底座。
3. **可用的实物级动力学参数（全部来自开放/已验证文献）**：环境浓度下整细胞近似一级 `k ≈ 0.25 h⁻¹`（m6，30℃，pH7）；重组 MlrA 粗酶伪一级最高 `9.36 h⁻¹`；原位菌群 `8.8–10 d⁻¹`；经典纯培养 `0.01537 h⁻¹`（CQ5）～`1.3 d⁻¹`（P. toxinivorans），跨体系差异超过 **3 个数量级** —— 这决定了模型必须采用**层次贝叶斯 + 株间随机效应**而非单一全局常数。
4. **关键机理信息**（决定模型状态变量设置）：降解是**多步酶级联**（MlrA 开环→MlrB→MlrC→小分子），第一步 MlrA 开环是最重要/最快步骤；`mlrA` 等基因在底物诱导下 1 h 内上调可达 25 倍；菌可把 MC-LR 作为碳氮源（部分菌）+ 自身死亡/光控自杀（本项目 YF1-FixJ 模块）会限制有效降解窗口。
5. **2026-08 复查新增两条强证据**：① [EST 2025](https://doi.org/10.1021/acs.est.5c09247) 的**结构-反应性规则**——微囊藻素仅在 Adda-Arg 位被水解（MC-LR/YR/RR 可降解），Adda-Leu/Tyr（如 MC-LL）不水解，支持"底物特异性矩阵"先验；② **株间温度响应差异极大**——m6 最适 30℃、接近 40℃ 失效，而 Klebsiella TA13/14/19 最适≥40℃ 且 pH 6–10 平坦——环境修正函数必须先验分层（详见架构报告 §5/§8.1 与数据报告 D14）。

---

## 1. 检索方法与范围

- 检索渠道：Europe PMC REST API（`https://www.ebi.ac.uk/europepmc/webservices/rest/search`）、Crossref API、OpenAlex API、Semantic Scholar API（部分被限流）、NCBI E-utilities（GenBank/蛋白质库）、ScienceBase（USGS）等；
- 检索词组合：`microcystin-LR` × (degradation/kinetics/biodegradation/model/prediction/mlrA/microcystinase)、`cyanotoxin` × (degradation kinetics)、`microcystin` × (mlr gene cluster / biodegradation / Mesocosm / water quality) 等 20+ 组；
- 范围限定：优先 2010–2026 年、被引高、期刊权威（Water Research、EST、L&O、Chemosphere、Toxins、Frontiers、EP）；中文文献（知网）仅作补充；
- 时间投入：共核验文献 30+ 篇，其中 22 篇写入本报告；**12 篇开放获取全文 PDF 已下载至 `../references/`**（统一文件夹，含 2026-08 复查新增的 USGS SIR 2023-5137），其余以 DOI/PubMed/OpenAlex 链接记录（版权限制未能下载）；另下载 2 份补充数据 xlsx 至 `../data/raw/`（Figshare EST 2025 SI、Frontiers mlr SI）。

## 2. 文献目录（按与模型的相关性分类）

> 标注：✅=已下载全文至 `../references/`；🔒=付费墙/平台拦截，仅记录元数据与摘要要点。

### 2.A 生物降解动力学与机理（第一优先级）

#### A1. Further Understanding of Degradation Pathways of Microcystin-LR by an Indigenous Sphingopyxis sp. in Environmentally Relevant Pollution Concentrations ✅
- **期刊/年份**：Toxins 2018, 10(12), 536 | DOI：[10.3390/toxins10120536](https://doi.org/10.3390/toxins10120536) | PMC：[PMC6315713](https://pmc.ncbi.nlm.nih.gov/articles/PMC6315713/)
- **本地文件**：`../references/2018_Toxins_Sphingopyxis_m6_DegradationPaths_MCLR.pdf`
- **简要介绍**：首次在**环境相关浓度（1–50 μg/L）**下系统研究 Sphingopyxis sp. m6 对 MC-LR 的降解，发现 1–50 μg/L 可在 4 h 内完全降解（无延迟期），并鉴定出 5+8 种降解产物；定量了 4 个 mlr 基因的诱导表达动态。
- **方法与思路**：HPLC/UPLC-MS/MS 定量底物与产物；单因素实验分别改变 浓度(1–50 μg/L)/温度(20/30/37/40℃)/pH(3–11)；qPCR 测定 mlrA-D 表达 fold-change（0.5–6 h）；对比 10 mg/L 高浓度实验（平均 60 mg/L/d，首小时 136.3 mg/L/d）。
- **对本模型的启示**（直接量化）：
  - 环境浓度下速率 ≈ 0.25 × C₀（μg/L·h⁻¹），即**近似一级、k≈0.25 h⁻¹**（30℃/pH7，菌密度 7×10⁹ CFU/mL 量级）；
  - 温度最优 30℃（20℃≈0.5×、37℃≈0.6×、40℃≈0）；pH 钟形最适 7；
  - **诱导动态**：mlrA 首小时上调 25 倍 → 模型需要"酶浓度 E(t)"状态而非常数速率；
  - 产物谱 → 多步级联（线性化→四肽→Adda）需要 2–4 个状态变量。

#### A2. Optimization of Biodegradation Characteristics of Sphingopyxis sp. YF1 against Crude Microcystin-LR Using Response Surface Methodology ✅
- **期刊/年份**：Toxins 2022, 14(4), 240 | DOI：[10.3390/toxins14040240](https://doi.org/10.3390/toxins14040240) | PMC：[PMC9026303](https://pmc.ncbi.nlm.nih.gov/articles/PMC9026303/)
- **本地文件**：`../references/2022_Toxins_Sphingopyxis_YF1_RSM_biodegradation_optimization.pdf`
- **简要介绍**：用 Box-Behnken 设计（BBD）+ 响应面法优化 YF1 对粗品 MC-LR 的生物降解条件；60 min 降解率分布在 29.7%–100%；二次模型 R²=0.9888（pH 为最显著因子，p=0.0007；温度与浓度主效应不显著）。
- **方法与思路**：三因素三水平 BBD（T:20/30/40℃，pH:5/7/9，MC-LR:1/3/5 μg/mL），Design-Expert 拟合二次多项式；ANOVA 检验；残差正态性检验；单因子实验观察 60 min 内速率（最高 0.083 μg/mL/min @ 5 μg/mL, 30℃, pH7）。
- **对本模型的启示**：
  - **RSM 二次多项式 = 现成的"环境修正函数"经验模板**（温度×pH×浓度交互项）；
  - 表 2 的 17 组设计矩阵+响应值已提取为本项目数据集：`../data/processed/YF1_RSM_BBD_17runs_extracted.csv`；
  - 提示：**在 μg/mL 级浓度下，pH 对速率的影响显著大于温度**——环境修正函数应保留非线性项与交互项（RSM 优于简单乘积因子）。

#### A3. Biodegradation kinetics of microcystins-LR crude extract by Lysinibacillus boronitolerans strain CQ5 🔒（全文下载被 BMC 反爬拦截，已获取完整摘要与全部动力学参数）
- **期刊/年份**：Annals of Microbiology 2019, 69(8), 881–888 | DOI：[10.1007/s13213-019-01510-6](https://doi.org/10.1007/s13213-019-01510-6)（Springer/BMC 开放获取，可人工下载）
- **简要介绍**：以 MC-LR 粗提物为唯一碳/氮源筛选到 CQ5，建立**菌生长动力学 + 底物降解动力学**耦合模型，实现"以生长推降解"。
- **方法与思路**（重要：全部为可复用模型）：
  - 生长：**Gompertz 模型** `N_t = 1.3119·exp(−0.1237·exp(−6.6341·t))`，R²>0.99；
  - 降解：**一级动力学** `ln S = 2.64764 − 0.01537·t`，R²>0.99 → `k = 0.01537 h⁻¹`（244 h 内 14.12→1.57 μg/L，降解率 88.88%）；
  - 耦合：**修正 Monod** `V = 0.342·S`（低底物区，Vmax/Ks = 0.342）→ 统一模型 `S = 14.12·e^(−0.342·N·t)`，N=1.08；
  - 条件：初始 pH 7、接种量 3%（v/v）。
- **对本模型的启示**：
  - 这是**"生长-底物耦合"（Growth-linked）动力学的完整教科书案例**：菌量 N(t) 进入降解速率、并同时被底物驱动生长（底物为碳氮源）；
  - 本项目工程菌若**不能**利用 MC-LR 作为碳源（更可能），则需改为"维持型"（μ=0、常数活菌量衰减）——这正好对应"机理内核中生长项开关"的设计；
  - 提供了一级+Monod 双形式之间的衔接范例（低浓度下 Monod 退化为一阶）。

#### A4. Simultaneous Removal of the Freshwater Bloom-Forming Cyanobacterium Microcystis and Cyanotoxin Microcystins via Combined Use of Algicidal Bacterial Filtrate and the Microcystin-Degrading Enzymatic Agent, MlrA ✅
- **期刊/年份**：Microorganisms 2021, 9(8), 1594 | DOI：[10.3390/microorganisms9081594](https://doi.org/10.3390/microorganisms9081594) | PMC：[PMC8401626](https://pmc.ncbi.nlm.nih.gov/articles/PMC8401626/)
- **本地文件**：`../references/2021_Microorganisms_MlrA_algicidal_combined_removal.pdf`
- **简要介绍**：将藻类杀菌滤液（Paenibacillus SJ-73）与重组 MlrA 酶联用，同时杀藻与降解毒素；给出酶制剂剂量-效果关系与脉冲式投加实验（0.8 mg/L MlrA，单次 vs 两次投加）。
- **方法与思路**：重组 E. coli 表达 Sphingopyxis sp. HW MlrA 粗酶；UPLC-MS 定量；宏培养（M. aeruginosa PCC 7806, 4.4×10⁷ cells/mL）与殖民地型（TH1701）实验；伪一级速率常数拟合；**剂量-投加次数-残留量**分析。
- **关键数据**：粗酶对 [D-Asp³]MC-LR 降解速率 **17.82 mg L⁻¹ h⁻¹**；伪一级速率常数最高 **9.36 h⁻¹**；可降解最低浓度 **<0.8 μg/L**；天然菌株对照仅 0.34 mg L⁻¹ h⁻¹（≈52 倍差距）；两次投加（0 d/3 d）后 MCs 去除率 79.1%–94.2%。
- **对本模型的启示**：
  - **酶剂量→降解效率**可直接量化 → 决策层"剂量-响应"臂；
  - **半衰期<小时级**的酶促降解 vs 天然水中 MC 半衰期约 10 周（文中引文）→ 工程菌/酶的价值来源；
  - 注意 pH 漂移（8.6→9.5）对酶活的影响 → 模型应包含 pH 时变路径（pH 作为状态或外生时变输入）。

#### A5. MlrA, an Essential Enzyme for Microcystins and Nodularin on First Step Biodegradation 🔒
- **期刊/年份**：Chemical Research in Toxicology 2024 | DOI：[10.1021/acs.chemrestox.3c00341](https://doi.org/10.1021/acs.chemrestox.3c00341)（付费墙；摘要经 OpenAlex 获取）
- **简要介绍**：用 Sphingopyxis sp. C-1 野生型与 mlrA 敲除突变株 CMS01 对比，证实 MlrA 是多种 MCs 与 Nodularin 第一步降解的必要酶；底物特异性为：MC-LR/RR/YR 在 **Adda-Arg** 位开环；MC-LA/LW/LY/LF 在 **Adda-L-氨基酸** 位点；也能降解 Nodularin。
- **对本模型的启示**：确认第一步开环底物谱（模型可做"毒素变体扩展"）；MlrA 敲除→无降解，说明**单酶阻断实验**可用于模型参数验证（可辨识性设计）。

#### A6. Heterologous expression and characterisation of microcystinase 🔒
- **期刊/年份**：Toxicon 2012, 59(5), 578–586 | DOI：[10.1016/j.toxicon.2012.01.001](https://doi.org/10.1016/j.toxicon.2012.01.001)（付费墙）
- **简要介绍**：MlrA（microcystinase）异源表达与生化表征的奠基性工作，提供酶活测定方法（Adda-Arg 水解活性、速率测定、Km/kcat 体系）。
- **对本模型的启示**：MlrA 纯酶动力学（Km/kcat）的测定方法学 → 本项目湿实验可直接复刻；模型预留 **kcat/Km 型双参数**而非单一 k。

#### A7. Structural insight into the substrate-binding mode and catalytic mechanism for MlrC enzyme of Sphingomonas sp. ACM-3962 in linearized microcystin biodegradation ✅
- **期刊/年份**：Frontiers in Microbiology 2023 | DOI：[10.3389/fmicb.2023.1057264](https://doi.org/10.3389/fmicb.2023.1057264) | PMC：[PMC9982164](https://pmc.ncbi.nlm.nih.gov/articles/PMC9982164/)
- **本地文件**：`../references/2023_FrontMicrobiol_MlrC_structure_catalysis.pdf`
- **简要介绍**：解析 MlrC 结构并阐明其对线性化 MCs 的底物结合与催化机制（羧肽酶类），确认第三步肽段水解。
- **对本模型的启示**：MlrB（丝氨酸蛋白酶）与 MlrC（羧肽酶）可合并为"后续步骤"以简化状态空间，但保留其**较 MlrA 更慢**的属性（文献证据支持 MlrA 为限速/最显著步骤）。

#### A8. Enzymatic pathway for biodegrading microcystin LR in Sphingopyxis sp. C-1 🔒
- **期刊/年份**：Journal of Bioscience and Bioengineering 2012 | DOI：[10.1016/j.jbiosc.2012.07.004](https://doi.org/10.1016/j.jbiosc.2012.07.004)（付费墙）
- **简要介绍**：确立 C-1 株 MlrA→MlrB→MlrC 完整酶学通路及各步产物（线性化 MC-LR→四肽→Adda 等），是"级联状态方程"的生物学依据。

#### A9. Microcystin-LR Degradation and Gene Regulation of Microcystin-Degrading Novosphingobium sp. THN1 at Different Carbon Concentrations ✅
- **期刊/年份**：Frontiers in Microbiology 2019 | DOI：[10.3389/fmicb.2019.01750](https://doi.org/10.3389/fmicb.2019.01750) | PMC：[PMC6691742](https://pmc.ncbi.nlm.nih.gov/articles/PMC6691742/)
- **本地文件**：`../references/2019_FrontMicrobiol_THN1_carbon_gene_regulation.pdf`
- **简要介绍**：不同碳浓度下 mlr 基因表达规模与降解效率的联动；低碳条件下 mlr 表达上调、降解率更高（诱导型调控）。
- **对本模型的启示**：**基质（碳源/营养盐）作为外生变量进入酶表达模块**；环境营养状态会在降解率上造成多倍差异——混合模型需含"碳/营养状态"特征。

#### A10. Presence or Absence of mlr Genes and Nutrient Concentrations Co-Determine the Microcystin Biodegradation Efficiency of a Natural Bacterial Community ✅
- **期刊/年份**：Toxins 2016, 8(11), 318 | DOI：[10.3390/toxins8110318](https://doi.org/10.3390/toxins8110318) | PMC：[PMC5127115](https://pmc.ncbi.nlm.nih.gov/articles/PMC5127115/)
- **本地文件**：`../references/2016_Toxins_mlrGenes_Nutrients_codetermine_biodegradation.pdf`
- **简要介绍**：天然群落中 mlr 基因有无与营养盐浓度共同决定 MC 生物降解效率（mlr⁺ 群落效率显著更高；氨氮/磷酸盐影响降解能力）。
- **对本模型的启示**：① 天然菌群背景降解（本底速率 k_bg）需作为"背景项"进入模型；② 环境营养盐是外生协变量。

#### A11. Microcystin-LR Biodegradation by Bacillus sp.: Reaction Rates and Possible Genes Involved in the Degradation 🔒（MDPI 反爬，未能下载；非 PMC 收录）
- **期刊/年份**：Water 2016, 8(11), 508 | DOI：[10.3390/w8110508](https://doi.org/10.3390/w8110508)
- **简要介绍**：Bacillus sp. 对 MC-LR 的反应速率（**非 mlr 途径**，k≈0.4 d⁻¹，慢速）与潜在降解基因鉴定；为"非 mlr 慢速途径"的代表。
- **对本模型的启示**：提供**慢速路径参数先验**（与 mlr⁻ 菌群 1.3 d⁻¹、mlr⁺ 纯培养 0.25 h⁻¹ 等形成"快-慢"双层参数结构）。

#### A12. Quantification of microcystin production and biodegradation rates in the western basin of Lake Erie ✅
- **期刊/年份**：Limnology and Oceanography 2022, 67(7), 1467–1480 | DOI：[10.1002/lno.12096](https://doi.org/10.1002/lno.12096) | PMC：[PMC9543754](https://pmc.ncbi.nlm.nih.gov/articles/PMC9543754/)
- **本地文件**：`../references/2022_LimnolOceanogr_LakeErie_MC_production_biodegradation_rates.pdf`
- **简要介绍**：在伊利湖西部流域用 **¹⁵N 标记 MC-LR** 微宇宙实验原位定量**产生速率与生物降解速率**，并通过 NanoSIMS 证明降解由异养菌群完成；为"湖库尺度降解速率"提供了极稀缺的原位数据。
- **方法与思路**：15N-MC-LR 添加+平行监测 14N 天然 MC 释放；准一级速率常数拟合；P/N 施肥处理区分产生速率；NanoSIMS 同位素显微成像；2 周间隔的季节采样。
- **关键数据**：近岸最高速率实验（19 Aug 2019）中 15N-MC-LR **15 h 内低于检测限**；天然 MC 首 24 h **k≈10 d⁻¹**（15N 标记对照 8.8 d⁻¹）；后期降至 3.6 d⁻¹；对比：mlr⁻（P. toxinivorans）1.3 d⁻¹、Bacillus 0.4 d⁻¹、mlr⁺ 纯培养 ≈10 d⁻¹。
- **对本模型的启示**：提供"完全群落"（community-level）上行速率常数；**浓度峰值后降解最快**（底物/酶诱导响应）→ 支持诱导型动力学而非恒速模型；数据可用性声明指向 Ohio Sea Grant `live/water` 门户（见数据报告）。

#### A13. The Effect of a Combined Hydrogen Peroxide-MlrA Treatment on the Phytoplankton Community and Microcystin Concentrations in a Mesocosm Experiment in Lake Ludoš ✅
- **期刊/年份**：Toxins 2019, 11(12), 725 | DOI：[10.3390/toxins11120725](https://doi.org/10.3390/toxins11120725) | PMC：[PMC6950535](https://pmc.ncbi.nlm.nih.gov/articles/PMC6950535/)
- **本地文件**：`../references/2019_Toxins_mesocosm_H2O2_MlrA_LakeLudos.pdf`
- **简要介绍**：真实湖泊（Ludoš, Serbia）中宇宙实验：H₂O₂ 压制水华 + MlrA 酶降解 MC 的联合治理，连续多日监测 MC（含胞内/胞外）与浮游植物群落。
- **对本模型的启示**：① **中试级（mesocosm）剂量-效应数据**是本模型"决策层"最接近的实地验证来源；② 治理过程中**胞内毒素释放**（杀藻后释放）会形成"峰值"→ 模型必须区分胞内/胞外 MC 池（状态变量建议增加 `C_intracellular`）；③ 多日尺度的再增长/再释放 → 二次投放策略。

#### A14. Biodegradation of Microcystins by Aquatic Bacteria Klebsiella spp. Isolated from Lake Kasumigaura ✅
- **期刊/年份**：Toxins 2025, 17(7), 346 | DOI：[10.3390/toxins17070346](https://doi.org/10.3390/toxins17070346) | PMC：[PMC12298343](https://pmc.ncbi.nlm.nih.gov/articles/PMC12298343/)
- **本地文件**：`../references/2025_Toxins_Klebsiella_Kasumigaura_biodegradation.pdf`
- **简要介绍**：日本霞浦湖分离的 Klebsiella（TA13/14/19）可在 pH 6.0–11.0 生长并降解 MCs；给出碱性水域降解可能性。
- **对本模型的启示**：补充 **碱性 pH 区（pH 9–11）** 降解行为的证据 → 修正 f_pH 的右侧尾部（比对 m6 的 pH11=0.52×）。

### 2.B 建模与预测方法学（第二优先级）

#### A15. Biotransformation Dynamics and Products of Cyanobacterial Secondary Metabolites in Surface Waters 🔒（论文付费墙；补充数据已下载 ✅）
- **期刊/年份**：Environmental Science & Technology 2025, 59(38), 20726–20737 | DOI：[10.1021/acs.est.5c09247](https://doi.org/10.1021/acs.est.5c09247) | PMC：[PMC12490008](https://pmc.ncbi.nlm.nih.gov/articles/PMC12490008/)（Eawag, Wang/Ingold/Janssen）
- **补充数据**：Figshare [30170897](https://figshare.com/articles/dataset/Biotransformation_Dynamics_and_Products_of_Cyanobacterial_Secondary_Metabolites_in_Surface_Waters/30170897)（es5c09247_si_002.xlsx，3.3 MB，✅ 已下载至 ../data/raw/Figshare_Biotransformation_Cyanopeptides_2025/）
- **简要介绍**：在表层水与原位富集生物膜悬浮液中，系统测定 **40 种蓝藻环肽**（微囊藻素、anabaenopeptin、cyanopeptolin 等）的生物转化动力学与产物；表面水中多数环肽 7 天降解不显著，而三条河流的生物膜中呈现广泛差异；生物膜密度增加→滞后期缩短+初期去除率提升；初始浓度升高→滞后期延长（底物对自身转化酶的抑制效应）。
- **对本模型的启示**（重要）：
  1. **结构-反应性规则**：微囊藻素仅在 **Adda-Arg** 连接时被水解成四肽（即 MC-LR/YR/RR 类可被 MlrA 水解），**Adda-Leu/Tyr 连接（MC-LL 等）不水解**——直接给出底物特异性矩阵先验，支撑模型向多毒素（MC-LR/YR/RR + 不降解变体）扩展时的差异速率分层；
  2. **滞后期（lag）建模**：浓度升高→滞后期延长（自抑制）与生物膜密度→滞后缩短，说明模型的 E(t) 诱导/表达模块应考虑"密度依赖的启动时间"（当前 Hill 诱导项的延伸方向）；
  3. 与 A1（m6）/A4（粗酶）对照：环境表面水（无富集生物膜）7 天不显著 → 背景 k_bg 下限（约"无活性菌"半衰期周级）的独立证据。

#### B1. Application of unstructured kinetic models to predict microcystin biodegradation: Towards a practical approach for drinking water treatment 🔒（关键方法论文）
- **期刊/年份**：Water Research 2018（卷/页见 DOI 落地页）| DOI：[10.1016/j.watres.2018.11.014](https://doi.org/10.1016/j.watres.2018.11.014)（付费墙；摘要见 OpenAlex）
- **简要介绍**：以**非结构动力学模型**（unstructured kinetic models：一级/零级/Monod 型）拟合与预测给水厂沙滤/生物处理中的 MCs 生物降解。
- **方法与思路**：对批式/连续流数据做模型比较（AIC/BIC），以解析式或 ODE 拟合，外推不同停留时间下的去除率。
- **对本模型的启示**：**这是"用简单非结构模型做工程预测"的最直接先例**——本项目的机理内核（一级+Monod+修正项）与其哲学一致，但在其基础上增加：株级层次效应、环境修正、不确定性、剂量反问题。

#### B2. Degradation of Toxins and Metabolites of Cyanobacteria and Micropollutants during Biological Sand Filtration ✅
- **期刊/年份**：Environmental Science & Technology 2026, 60(12), 9647–9659 | DOI：[10.1021/acs.est.5c16532](https://doi.org/10.1021/acs.est.5c16532) | PMC：[PMC13045012](https://pmc.ncbi.nlm.nih.gov/articles/PMC13045012/)
- **本地文件**：`../references/2026_EST_sand_filtration_kinetic_modeling.pdf`
- **简要介绍**：实验室砂柱中微生物降解藻毒素与微污染物的动力学建模：**表观一级 k_app、Arrhenius 活化能 Ea、零级/一级统计比较、停流时间（plug-flow 理想近似）偏差校正、浓度依赖性、驯化（acclimation）效应**。
- **关键数据**：微囊藻类 k_app ≃ (5–30)×10⁻⁴ s⁻¹ @21℃（约 1×10⁻³–0.03 h⁻¹ 量级换算需注意列间差异）；未驯化柱低 3–15 倍；MC-LR 聚类分析中与环酰胺类（cyclamides）行为相近。
- **对本模型的启示**：① **k_app 的"生物量密度-温度-驯化"分解**是表观速率常数建模的标准范式；② "零级 vs 一级"统计检验（比较拟合优度）应写入模型自动选择流程（当底物浓度接近 Km 时出现混合级数——论文明确提示此点）；③ 低温 Arrhenius 修正 + 驯化隐含 "历史上暴露"状态的记忆项 → 对本项目"每 3 天投放"的节律有直接参考。

#### B3. Determination of rate constants and half-lives for the simultaneous biodegradation of several cyanobacterial metabolites in Australian source waters 🔒
- **期刊/年份**：Water Research 2012 | DOI：[10.1016/j.watres.2012.08.003](https://doi.org/10.1016/j.watres.2012.08.003)（付费墙）
- **简要介绍**：L. Ho 团队对多种蓝藻代谢物（MC-LR/MC-RR/cylindrospermopsin 等）在澳大利亚水源水中的**同时生物降解速率常数与半衰期**的经典测定；是"多底物竞争降解"的数据来源。
- **对本模型的启示**：多毒素并存时存在**底物竞争** → 模型状态扩展为多底物向量（MC-LR/YR/RR），采用竞争型 Michaelis-Menten。

#### B4. Microcystin-LR degradation kinetics during chlorination: Role of water quality conditions 🔒
- **期刊/年份**：Water Research 2020 | DOI：[10.1016/j.watres.2020.116305](https://doi.org/10.1016/j.watres.2020.116305)（付费墙）
- **简要介绍**：氯化条件下 MC-LR 降解动力学随**水质条件**（pH、温度、DOC、氯剂量）的变化；展示"条件依赖性速率常数"的表征范式（与中国知网 ANN 氯化/臭氧模型可互参）。
- **对本模型的启示**：为"外生水质特征→速率修正"提供统计范式（多维协变量的准一级 k 建模），可迁移为**"环境特征→菌降解速率"的经验代理**。

#### B5. Simultaneous Microcystin Degradation and Microcystis aeruginosa Inhibition with the Single Enzyme Microcystinase A 🔒
- **期刊/年份**：Environmental Science & Technology 2020 | DOI：[10.1021/acs.est.0c02155](https://doi.org/10.1021/acs.est.0c02155)（付费墙；摘要经 OpenAlex 获取）
- **简要介绍**：首次在 E. coli 中获得 >90% 纯度 MlrA；高温/碱性稳定性高、半衰期长；纯酶可同时**降解胞外 MC**并**下调 MC 合成基因、抑制光合作用**而选择性抑制产毒 Microcystis（对非产毒 Synechocystis 无影响）。
- **对本模型的启示**：① 纯酶制剂的"稳定窗口"（温度/pH/时长）→ 酶失活项建模；② **酶不只是降解器，还是杀藻/抑藻器** → 系统级模型中"胞内 MC 池-再释放"的耦合。

#### B6. 臭氧降解微囊藻毒素的人工神经网络模型（中文文献，知网）🔒
- **来源**：中南大学学报（自然科学版）2011 年 01 期 | [知网链接](https://wap.cnki.net/touch/web/Journal/Article/ZNGD201101043.html)
- **简要介绍**：以 ANN 建立臭氧降解 MC 的输入（臭氧浓度、pH、时间等）→ 降解率/残留模型；说明"数据驱动降解模型"在国内已有先例。
- **对本模型的启示**：工程实践中 **GBDT/ANN 经验代理是模式认可的做法**——本项目以"机理 ODE+贝叶斯"为主干、ML 为代理的双轨方案与之兼容且更优（可外推、可解释）。

### 2.C 工程化/应用案例（第三优先级）

#### C1. Immobilization of Microcystin by the Hydrogel-Biochar Composite to Enhance Biodegradation during Drinking Water Treatment ✅
- **期刊/年份**：ACS ES&T Water 2023 | DOI：[10.1021/acsestwater.3c00240](https://doi.org/10.1021/acsestwater.3c00240) | PMC：[PMC10496130](https://pmc.ncbi.nlm.nih.gov/articles/PMC10496130/)
- **本地文件**：`../references/2023_ACSESTWater_hydrogel_biochar_MC_biodegradation.pdf`
- **简要介绍**：吸附-生物降解联合：水凝胶-生物炭复合物先将 MC 富集，提升后续生物降解——展示"吸附汇+生物降解"耦合模型的需求。
- **对本模型的启示**：天然水体中**颗粒物/沉积物吸附**是 MC 的竞争性汇项 → 状态方程增加"可逆吸附"项（快速吸附/解吸），否则会高估生物降解 k。

#### C2. Bioreactor study employing bacteria with enhanced activity toward cyanobacterial toxins microcystins（Dziga 等先导工作）✅（PMC 开放）
- **来源**：[PMC4147588](https://pmc.ncbi.nlm.nih.gov/articles/PMC4147588/)（文献的 PMC 全文可用；本报告未单独保存 PDF）
- **简要介绍**：将高活性 MC 降解菌用于**生物反应器**（优化菌密度、载体、流态），是"菌密度→降解通量"的动力学/工程尺度汇总。
- **对本模型的启示**：生物反应器研究与湖泊投放的换算（单位体积菌量、停留时间）→ 剂量换算链。

#### C4. Isolation and Identification of Microcystin-Degrading Bacteria in Lake Erie Source Waters and Drinking-Water Plant Sand Filters ✅
- **期刊/年份**：USGS Scientific Investigations Report 2023-5137, 23 p.（2024）| DOI：[10.3133/sir20235137](https://doi.org/10.3133/sir20235137)
- **本地文件**：../references/2023_USGS_SIR5137_MCLR_degraders_LakeErie_sandfilters.pdf（2.0 MB，✅ 已下载）
- **配套数据**：USGS data release [10.5066/P9DL080Y](https://doi.org/10.5066/P9DL080Y)（微宇宙实验数据，✅ 已下载，见数据报告 D11）
- **简要介绍**：2015–2018 年在伊利湖西流域 4 个饮用水源水 + 7 个砂滤水样品中富集、分离与鉴定微囊藻素降解菌：微宇宙+微板实验测定 MC-LR 消失动力学（ELISA）、以 MC-LR 为唯一碳源的生长、生物膜形成潜力，并检测降解菌中的 mlrA 基因；共分离出 10 株候选降解菌（如 *S. rhizophila*、*Pseudomonas* 等）。
- **对本模型的启示**：① 提供了"天然水处理基质中降解菌群"的完整方法学与实测数据（与 B2 生物沙滤互为印证）；② **负对照 E. coli 也表现出 MC-LR 下降**（T0 3.51→T8 2.13 µg/L）——这是"非特异低效背景去除"的量化证据（模型 k_bg 先验的一部分）；③ 菌株级分离-鉴定工作流程可直接迁移到本项目降解菌的湿实验设计。

#### C3. iGEM 社区资源（干湿实验衔接）
- [iGEM 2021 Stony Brook 团队](https://2021.igem.org/Team:Stony_Brook)（MC 降解主题）；iGEM Parts：[BBa_K2960007](https://parts.igem.org/wiki/index.php/Part%3aBBa_K2960007)、[BBa_K3738033](https://parts.igem.org/Part:BBa_K3738033)、[K3699001](https://parts.igem.org/wiki/index.php?title=Part:BBa_K3699001&diff=cur&oldid=491996)（与 mc/微囊藻毒素相关的生物砖）。
- **对本模型的启示**：生物砖级联可用性 + 竞赛届的"前车之鉴"（避免重复造轮子）。

### 2.D 环境归趋与背景数据（第四优先级）

- **D1. Microcystins are susceptible to biodegradation by aquatic bacteria found naturally in surface waters**（US EPA HAB 建议书引文，[PDF](https://epa.illinois.gov/content/dam/soi/en/web/epa/topics/water-quality/monitoring/algal-bloom/documents/hh-rec-criteria-habs-document-2019.pdf)）：自然水体细菌可降解 MCs —— 背景本底速率存在性的官方文档依据。
- **D2. Removal of the algal toxin microcystin-LR in permeable coastal sediments: Physical and numerical models**，L&O 2018, [10.1002/lno.10794](https://aslopubs.onlinelibrary.wiley.com/doi/abs/10.1002/lno.10794)：沉积物-孔隙水-水流中 MC-LR 的**物理-数值耦合模型**（吸附、弥散、生物降解）——与本项目的"2D 水流 + 降解汇"耦合完全同类，可借鉴其空间离散与源汇处理。
- **D3. Early warning of limit-exceeding concentrations of cyanobacteria and cyanotoxins in drinking water reservoirs by inferential modelling**（[AGRIS 记录](https://agris.fao.org/search/zh/records/65de53a3b766d82b18fd2605)）：水库藻毒素超限预警的推断建模——预警-治理联动思路。
- **D4. A mechanistic population-level (i.e. differential equation) model of Microcystis growth and toxin production**（ScienceDirect 2025, [链接](https://www.sciencedirect.com/science/article/pii/S0304380025000808)）：Microcystis 生长-产毒的群体水平微分方程模型 —— 藻华-产毒-降解**前向耦合**（上游产生项）的建模范本。

---

## 3. 关键动力学参数汇集（模型先验来源）

> 完整机器可读版本见 `../data/processed/literature_kinetic_parameters.csv`。

| 体系 | 条件 | 速率/常数 | 来源 DOI |
|---|---|---|---|
| Sphingopyxis sp. m6（整细胞） | 1–50 μg/L, 30℃, pH7 | 伪一级 k ≈ **0.25 h⁻¹**；1–50 μg/L 速率 1–12.5 μg/L/h | [10.3390/toxins10120536](https://doi.org/10.3390/toxins10120536) |
| Sphingopyxis sp. m6 | 10 mg/L | 平均 60 mg/L/d；首小时 136.3 mg/L/d；4 h 内 >99% | 同上 |
| 重组 E. coli 粗 MlrA（HW 来源） | [D-Asp³]MC-LR | **17.82 mg/L/h**；伪一级最高 **9.36 h⁻¹**；最低可降解 <0.8 μg/L | [10.3390/microorganisms9081594](https://doi.org/10.3390/microorganisms9081594) |
| 天然 Sphingopyxis sp. HW | — | 0.34 mg/L/h（≈粗酶 1/52） | 同上 |
| Lake Erie 原位菌群（¹⁵N 示踪） | 水华峰值后，近岸 | k ≈ **8.8–10 d⁻¹**（15 h 内<检测限）；后期 3.6 d⁻¹ | [10.1002/lno.12096](https://doi.org/10.1002/lno.12096) |
| Paucibacter toxinivorans（mlr⁻） | — | k ≈ 1.3 d⁻¹ | 同上（引 Morcillo-Lopez 2017） |
| Bacillus sp.（mlr⁻，Kansole & Lin） | — | k ≈ 0.4 d⁻¹ | [10.3390/w8110508](https://doi.org/10.3390/w8110508) |
| Lysinibacillus CQ5（碳氮源生长） | pH7, 3% 接种 | 一级 k = **0.01537 h⁻¹**；Vmax/Ks = 0.342；Gompertz 生长参数见上 | [10.1007/s13213-019-01510-6](https://doi.org/10.1007/s13213-019-01510-6) |
| 生物沙滤生物膜（MC 类群） | 21℃, 驯化柱 | k_app ≈ (5–30)×10⁻⁴ s⁻¹；未驯化低 3–15 倍 | [10.1021/acs.est.5c16532](https://doi.org/10.1021/acs.est.5c16532) |
| MC-LR 自然水环境 | 无活性菌群 | 半衰期 ≈ 10 周（抗强温/极端 pH/阳光） | [10.3390/microorganisms9081594](https://doi.org/10.3390/microorganisms9081594) 引文 |

**要点**：同类"生物降解"速率常数跨 3–4 个数量级（0.015 h⁻¹ ↔ 9.36 h⁻¹）。任何**单一固定 k 的确定性模型都不足以支撑剂量决策**；需（a）按菌株/酶型/环境条件分层的参数结构；（b）显式不确定性传播；（c）以湿实验数据（本项目降解菌）做在线校准。

---

## 4. 文献方法学对模型架构的映射（10 条结论）

1. **状态变量**：环状 MC-LR C → 线性化 L → 四肽 P → Adda/小分子 X（多步级联，MlrA 首步限速/最显著）；另需 B（菌）、E（酶）、C_intra（胞内 MC，来自杀藻/胞内池不可忽略）。
2. **速率形式**：低环境浓度（≤ μg/L 级）下 Monod 退化为一阶（k≈0.25 h⁻¹ 量级）；高浓度（mg/L）出现饱和/抑制 → 用 Michaelis-Menten + 可选底物抑制。
3. **环境修正**：温度钟形（最适 30℃）、pH 钟形（最适 7，碱性尾部非零）、DO/碳源/营养盐协变量；用 RSM 二次模型或乘积指数函数表征（YF1 数据表明交互项重要）。
4. **生长-降解耦合**：CQ5 模板（Gompertz + 修正 Monod + 一级）完整可用；工程菌无碳源利用能力时切换为维持/衰减模式。
5. **诱导动力学**：mlrA 诱导上调（m6：25 倍/1 h；THN1：低碳诱导）→ 酶表达子模型（Hill 型 + 降解/失活）。
6. **菌死亡率**：光控自杀模块（YF1-FixJ，蓝光→死亡）→ δ(I_light) 时变死亡率（本项目特有、且是决策窗口的关键约束，需湿实验标定 δ-光强曲线）。
7. **非生物汇项**：吸附（沉积物/颗粒物）、光解/氧化（水体表层）、稀释扩散（与 2D 水流模型耦合）、背景菌群降解（k_bg 本底项）。
8. **不确定性**：参数跨文献离散（3–4 个数量级）→ 层次贝叶斯（株间随机效应 + 文献先验）+ 蒙特卡洛/后验预测区间；这是**剂量决策必须带误差带**的核心理由。
9. **决策**：反问题（在限时内达标的最小剂量）+ 剂量-时间等值线图；参考"杀虫/杀菌剂脉冲投加剂量-频率研究"（如 PAH 降解模拟培养研究：剂量浓度与脉冲频率共同决定降解效率，[10.1007/s11356-023-26546-9](https://pubmed.ncbi.nlm.nih.gov/37016250/)）。
10. **验证策略**：文献级验证（参数重现：用 m6/YF1/CQ5 数据回测模型）→ 现场级验证（Lake Ludoš 型中宇宙参数）→ 本项目湿实验闭环校准。

## 5. 参考文献（含下载状态汇总）

> 下载文件夹：`../references/`（pdf），文本提取缓存 `../references/_extracted_text/`。

| # | 文献 | 链接 | 下载 |
|---|---|---|---|
| A1 | Sphingopyxis m6, Toxins 2018 | [DOI](https://doi.org/10.3390/toxins10120536) | ✅ |
| A2 | Sphingopyxis YF1 RSM, Toxins 2022 | [DOI](https://doi.org/10.3390/toxins14040240) | ✅ |
| A3 | CQ5 kinetics, Ann. Microbiol. 2019 | [DOI](https://doi.org/10.1007/s13213-019-01510-6) | ⚠️ 反爬拦截（摘要+全部参数已获取） |
| A4 | MlrA+algicidal, Microorganisms 2021 | [DOI](https://doi.org/10.3390/microorganisms9081594) | ✅ |
| A5 | MlrA essential enzyme, Chem. Res. Toxicol. 2024 | [DOI](https://doi.org/10.1021/acs.chemrestox.3c00341) | 🔒 付费墙 |
| A6 | Microcystinase characterization, Toxicon 2012 | [DOI](https://doi.org/10.1016/j.toxicon.2012.01.001) | 🔒 付费墙 |
| A7 | MlrC structure/catalysis, Front. Microbiol. 2023 | [DOI](https://doi.org/10.3389/fmicb.2023.1057264) | ✅ |
| A8 | C-1 酶学通路, J. Biosci. Bioeng. 2012 | [DOI](https://doi.org/10.1016/j.jbiosc.2012.07.004) | 🔒 付费墙 |
| A9 | THN1 carbon regulation, Front. Microbiol. 2019 | [DOI](https://doi.org/10.3389/fmicb.2019.01750) | ✅ |
| A10 | mlr genes & nutrients, Toxins 2016 | [DOI](https://doi.org/10.3390/toxins8110318) | ✅ |
| A11 | Bacillus sp. reaction rates, Water 2016 | [DOI](https://doi.org/10.3390/w8110508) | 🔒 MDPI 反爬 |
| A12 | Lake Erie rates, L&O 2022 | [DOI](https://doi.org/10.1002/lno.12096) | ✅ |
| A13 | Mesocosm H2O2+MlrA, Toxins 2019 | [DOI](https://doi.org/10.3390/toxins11120725) | ✅ |
| A14 | Klebsiella Kasumigaura, Toxins 2025 | [DOI](https://doi.org/10.3390/toxins17070346) | ✅ |
| A15 | Cyanopeptide biotransformation, EST 2025 | [DOI](https://doi.org/10.1021/acs.est.5c09247) | 🔒 论文付费；✅ SI 已下载 (Figshare) |
| C4 | USGS SIR 2023-5137 降解菌分离鉴定报告 | [DOI](https://doi.org/10.3133/sir20235137) | ✅ |
| B1 | Unstructured kinetic models, Water Res. 2018 | [DOI](https://doi.org/10.1016/j.watres.2018.11.014) | 🔒 付费墙 |
| B2 | Sand filtration kinetics, EST 2026 | [DOI](https://doi.org/10.1021/acs.est.5c16532) | ✅ |
| B3 | Ho rate constants, Water Res. 2012 | [DOI](https://doi.org/10.1016/j.watres.2012.08.003) | 🔒 付费墙 |
| B4 | Chlorination kinetics, Water Res. 2020 | [DOI](https://doi.org/10.1016/j.watres.2020.116305) | 🔒 付费墙 |
| B5 | Single enzyme microcystinase A, EST 2020 | [DOI](https://doi.org/10.1021/acs.est.0c02155) | 🔒 付费墙 |
| B6 | 臭氧降解 MC 的 ANN 模型 | [知网](https://wap.cnki.net/touch/web/Journal/Article/ZNGD201101043.html) | 🔒 CNKI |
| C1 | Hydrogel-biochar, ACS EST Water 2023 | [DOI](https://doi.org/10.1021/acsestwater.3c00240) | ✅ |
| C2 | Bioreactor enhanced bacteria | [PMC4147588](https://pmc.ncbi.nlm.nih.gov/articles/PMC4147588/) | 🔗 在线全文 |
| C3 | iGEM 社区资源 | [iGEM 2021 SBU](https://2021.igem.org/Team:Stony_Brook) | 🔗 在线 |
| D2 | 沉积物中 MC-LR 物理-数值模型, L&O 2018 | [DOI](https://aslopubs.onlinelibrary.wiley.com/doi/abs/10.1002/lno.10794) | 🔒 付费墙 |
| D4 | Microcystis 群体水平模型 2025 | [链接](https://www.sciencedirect.com/science/article/pii/S0304380025000808) | 🔒 付费墙 |

**总体说明**：12 篇 OA 论文已成功下载至统一文件夹（合计约 34 MB；2026-08 复查轮新增 USGS SIR 2023-5137）；4 篇因付费墙、1 篇因平台反爬（MDPI/BMC/Springer 直链）未能自动下载，均已记录作者信息与链接，建议人工通过机构权限获取；其核心方法/参数已通过摘要与公开全文（Europe PMC/OpenAlex/Crossref）核实并写入本文档。另：论文配套补充数据 2 份（EST 2025 SI、Frontiers mlr SI）经 Figshare 成功下载至 ../data/raw/。
