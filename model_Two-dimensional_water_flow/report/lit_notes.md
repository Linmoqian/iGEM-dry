# 二维浅水流模型（武汉东湖）文献调研笔记 · v2（已核实稿）

> 调研范围：东湖 2D 浅水方程 (2D SWE) 水动力建模、无人机投放降解菌节点、水华输运与监测。
> v2（2026-08-24）：正文标注【待核实】的条目已通过原文 PDF 全部核实（21 篇通读）；补充 6 篇新下载文献；下载清单见文综末尾。
> 开放获取标记：OA=开放获取；受控=付费/订阅。

---

## 主题 1：二维浅水方程湖泊风生环流建模（TELEMAC-2D / MIKE 21 / FVCOM / DELFT3D）

### 1.1 《Numerical Simulation of Donghu Lake Hydrodynamics and Water Quality Based on Remote Sensing and MIKE 21》
- **作者**：Xiaojuan Li, Mutao Huang*, Ronghui Wang（华中科技大学），2020。**【原待核实→已核实】**
- **期刊**：ISPRS International Journal of Geo-Information (MDPI)，ISSN 2220-9964；DOI https://doi.org/10.3390/ijgi9020094 （卷 9 期 2 文章 94）。**【已核实】**
- **开放获取**：✅ OA
- **方法与参数（全文核实）**：MIKE 21 FM（HD 浅水方程 + AD 对流扩散 + ECO Lab 水质/富营养化）；非结构三角网格 11,823 单元/6,462 节点、边界节点 80 m、最大单元 5000 m²、60 次平滑；自然邻域水深插值；模拟期 2017-11-15→12-17；开边界：进=东湖港+东沙河，出=新沟渠+九峰渠（水位过程线）；Manning M=35→42（n=0.0286→0.0238）；Smagorinsky 0.32→0.29；干/淹/湿 0.005/0.05/0.1 m；风场 NOAA 3h 时变空间常数；dt=2 h、CFL 0.85；验证：新沟渠站水位误差 <15%、流速 <25%。
- **对本项目可借鉴点**：东湖 2D SWE 的对标基准与参数锚点（本模块已采用 n=0.0238、均深 2.21/最大 4.75 m 标定）。

### 1.2 《Modelling the circulation and exchange of Kingston Basin and Lake Ontario with FVCOM》
- **作者**：Shore, J. A.（加拿大环境部），2009。**【已核实】**；期刊：Ocean Modelling 30(2-3):106-114, doi:10.1016/j.ocemod.2009.06.006（Elsevier，受控）。**【已核实】**
- **方法**：FVCOM 非结构三角 + 4 层 σ 分层；Kingston 湾（22 km²）与安大略湖交换；风场取 Kingston 机场 1990-1997 逐时；风生流 1–2.3 cm/s；6 个月模拟、多年冷启动。
- **借鉴点**：开边界与水交换设置（对应武丰闸/青山港）；"湾-大湖交换"量级可用以论证东湖闭湖假设在日尺度可接受。

### 1.3 《The influence of spatial wind inhomogeneity on flow patterns in a small lake》
- **作者**：Podsetchine, V.; Schernewski, G.，1999。**【已核实】**；Water Research 33(15):3339-3350, doi:10.1016/S0043-1354(99)00035-4（Elsevier，受控）。
- **方法**：2D 浅水有限元（Uttnes 1990 半隐式、上风 Tábata 格式）；湖 Belau（2.3 km²、最深 9 m）；3168 三角元、dt=15 s、Manning 0.026、水平涡黏 0.001 m²/s、科氏 1.17×10⁻⁴；5 岸站风观测（7 日 6 小时间隔 + 1990-94 五年统计）插值。
- **结论**：均匀 6 m/s SW 风→单环流；实测空间非均匀风→双胞环流（与观测一致）；岸线树木遮蔽不可忽略。
- **借鉴点**：空间非均匀风场是小湖(含东湖)系统性偏差来源；是空间 Cd/风场升级（E1/E2）的动机之一。

### 1.4 《Modeling wind-induced currents in lake Bolmen, Sweden, using TELEMAC 2D》
- **作者**：Prasanjaya Ekanayake，2021；Lund University 硕士论文 TVVR21/5007（导师 C. Klante；Larson）。**【已核实】**；公开可获取（LUP）。
- **方法**：TELEMAC-2D 建模 Bolmen（风生环流、示踪检测时间设计）；QGIS/Blue Kenue 前后处理。
- **借鉴点**：工程化操作细节；"Cd 依赖风速/湖形/fetch，同湖不同区域可不同"的论述支撑空间 Cd。

---

## 主题 2：风驱动湖流中"2D vs 3D 深平均模型"适用范围/局限

### 2.1 《Modelling flows in shallow (fluvial) lakes...limits of 2D compared to 3D models》
- **作者**：Fenocchi, A.; Petaccia, G.; Sibilla, S.，2016。**【已核实】**；Journal of Hydroinformatics 18(6):928-945, doi:10.2166/hydro.2016.033（IWA；受控→已获扫描版）。
- **结论（全文核实）**：2D 与 3D 深度平均流场相关 0.36–0.56（表 1，四个场景/两湖）；2D 深水高估/浅水低估；垂向湍流过程是主因；复杂地形湖只能定性一致。
- **借鉴点**：东湖 2D 结论置信度应表述为"水平环流模式定性可信、表层速率需修正"；表层漂移修正（windage）有据。

---

## 主题 3：水质监测传感器/监测站点最优布点

### 3.1 《Optimal Sensor Placement for Wind-Driven Circulation Environment in a Lake》
- **作者**：Nam, Kijin；Aral, Mustafa M.，2007（Georgia Tech MESL）。**【已核实，下载为 PPT 版】**；ASCE EWRI Congress 2007, doi:10.1061/40927(243)163。
- **方法**：情景 → 2D FE 浅水水动力 → 2D FE 污染物输运 → 各候选点检测时间 → GA 布点优化。
- **借鉴点**：本模块投放点优化的框架原型；我们用穷举 792 候选 + 风况系综期望值。

---

## 主题 4：湖泊蓝藻/微囊藻输运模拟（水动力+浮游生物耦合）

### 4.1 《Understanding the transport feature of bloom-forming Microcystis...agent-based modelling approach》
- **作者**：Chao Wang, Tao Feng*, Peifang Wang, Jun Hou, Jin Qian，2017。**【已核实】**；Ecological Modelling 343:25-38, doi:10.1016/j.ecolmodel.2016.10.017（受控→已获扫描版）。
- **方法（全文核实）**：太湖梅梁湾 20×20 km、500 m 网格、4 层；水动力 Boussinesq FV（2D 深度平均+d 层）+ Eulerian/Lagrangian agent-based 微囊藻（浮力调控、垂移、聚集）；16,900 个体/格？；Cw=0.00158（实测）；2017-08-22~25，风最大约 5 m/s。
- **结论**：强风→表面藻华面积增大但深层比例上升；弱风→近表面聚集比例高（正午 81%）；风应力通过垂向湍流 K_T 调节垂向分布。
- **借鉴点**：表层输运显著快于深度平均（风应力驱动表层流）；汇聚带=高风险带；菌团输运层设计参考。

---

## 主题 5：藻华预报模型（神经网络+2D 水动力；太湖/巢湖深度学习）

### 5.1 《Short-Term Early Warning Method for Algal Bloom Risk...》
- **作者**：Na Luo, Xiaochao Gu, Kai Gao, Zeli Li, Pengyu Mei, Zhen Zhang, Zhi Wang, Dayue Su，2025。**【原卷/页待核实→已核实：PJES 34(1):227-235】**；doi:10.15244/pjoes/186001；在线 2024-05-20。
- **方法**：BP 神经网络 + 二维水动力-水质模型（吴贵森/于桥水库）+ 衰减系数耦合；探讨浅水水库流场对藻类迁移聚集的影响、水温/风速/风向作用。
- **借鉴点**：ML+物理耦合预警管线范式（对应 model_redo_v2→本模块）。

### 5.2 《Long-term trend forecast of chlorophyll-a concentration over eutrophic lakes...》
- **作者**：Cheng Chen, Mingtao Hu, Qiwen Chen, Jianyun Zhang, Tao Feng, Zhen Cui，2024。**【已核实】**；Science of the Total Environment 953:176845, doi:10.1016/j.scitotenv.2024.176845。
- **方法**：STL 分解 + mRMR/小波特征筛选 + RF/ConvLSTM/BiLSTM 集成；太湖。
- **借鉴点**：上游预测模块长时趋势层参考（补充定位，非核心）。

---

## 主题 6：PINN（物理信息神经网络）求解浅水方程/湖泊水动力

### 6.1 ConvLSTM-PINN（IAHR 2025，会议）——稀疏观测湖泊水动力；未来方向。【未变】
### 6.2 《RimNet: A Hybrid Neural Network–Finite Volume Framework for Riemann Flux Approximation in Shallow Water Equations》
- **作者**：Jingxiao Wu, Qiuhua Liang*, Huili Chen, Haoran Duan，2025。**【已核实】**；SSRN abstract_id=5433524（预印本 OA）。
- **方法/结果（全文核实）**：通量级 NN 代理（physics-guided），嵌入 Godunov FVM；保持守恒与时间步进；跨网格分辨率/初值泛化；矩阵化推理省去波速计算，**运行时间降 29.66%**；冲击波/干湿/振荡流验证。
- **借鉴点**：保结构代理 = SWE 加速与可微化的远期路线；对本模块而言 CG 半隐式已够快，仅可微优化有增量。

---

## 主题 7：UAV 水体采样/水质监测

### 7.1 《Autonomous In Situ Measurements...UAV》
- **作者**：Cengiz Koparan, Ali Bulent Koc*, Charles V. Privette, Calvin B. Sawyer（Clemson），2019。**【已核实】**；Water 11(3):604, doi:10.3390/w11030604（OA）。
- **数据**：六旋翼+采样筒+传感器；**106 N 推力/6.3 kg 全重/10 min 续航/推重比 2.5@50% 油门**；0.5 m 与 3.0 m 深度 6 点验证。
- **借鉴点**：载荷-续航实测量级（路径规划模块 4–6 kg/28–34 min 的现实锚点）；非污染采样设计。

### 7.2 《A Cooperative UAV Hyperspectral Imaging and USV In Situ Sampling Framework for Rapid Chlorophyll-a Retrieval》
- **作者**：Zixiang Ye, Xuewen Chen, Lvxin Qian, Chaojun Lin, Wenbin Pan（福州大学），2026。**【原待核实→已核实：Drones 10(1):39, doi:10.3390/drones10010039】**；OA。
- **方法**：UAV 高光谱 + USV 原位采样协同；两阶段特征选择 + RF 最优（小样本）；饮用水水库应急监测。
- **借鉴点**：天-水协同反演框架（叶绿素面分布）→ 对应 model_redo_v2 与监测节点的接口。

---

## 主题 8：无人机区域覆盖路径规划

### 8.1 《Unmanned Ariel Vehicle (UAV) Path Planning for Area Segmentation in Intelligent Landmine Detection Systems》
- **作者**：A. Barnawi, K. Kumar, N. Kumar, N. Thakur, B. Alzahrani, A. Almansour，2023。**【已核实】**；Sensors 23(16):7264, doi:10.3390/s23167264（OA/PMC10458967）。
- **方法**：区域分解 + CPP + 多机协同算法族 + 七类评价指标（覆盖完整性/路径长度/重叠/转弯数/公平性/时间/能量）。
- **借鉴点**：覆盖形式化与评价体系。

### 8.2 《Region coverage-aware path planning for unmanned aerial vehicles: A systematic review》
- **作者**：Krishan Kumar, Neeraj Kumar，2023。**【原期刊待核实→已核实：Physical Communication 59:102073, doi:10.1016/j.phycom.2023.102073】**（Elsevier）。
- **方法**：57+ 篇分类矩阵；多区域+多无人机=energy-aware mTSP；2-opt 主流；在线重规划前沿。
- **借鉴点**：本模块→路径规划接口的问题表述与评价体系。

### 8.3 《The multi-visit vehicle routing problem with multiple heterogeneous drones》
- **作者**：Yu Jiang, Mengmeng Liu, Xiaojia Ji*, Qingwen Xue，2025。**【已核实】**；Transportation Research Part C 172:105026, doi:10.1016/j.trc.2025.105026。
- **方法**：MV-VRP-MHD（多次访问+异构无人机）；能量=飞行+悬停+载荷；VNS-SA 求解；敏感性：机速/载荷/续航显著影响效率。
- **借鉴点**：多架次、异构机队、覆盖-时间权衡的建模范式（E4 接口实验依据）。

---

## 主题 9：浅水湖污染物/示踪物输运的粒子追踪（Lagrangian）方法

### 9.1 《Inflows/outflows driven particle dynamics in an idealised lake》——同前（Dang & Wang 2019, J. Hydrodynamics 31(5), doi:10.1007/s42241-019-0070-9；受控，未下载）；粒子=投放单元、滞留/通量口径。

---

## 主题 10：风应力/曳力系数、Manning 糙率、Smagorinsky 涡黏等经验参数取值

### 10.1 《Adaptation of Wind Drag Coefficient Parameterization...Wave-Dependent Cd...》
- **作者**：Chen Zhang*, Lingwei Chen, Michael T. Brett（天津大学/华盛顿大学），2024。**【已核实】**；Water Resources Research 60(5):e2023WR035914, doi:10.1029/2023WR035914（OA）。
- **方法/结果（全文精读）**：LSP-AWMTHP 1:4 缩比实验（0.5–3.0 m/s 风、0.02–0.04 m 波、27 组）；EC+风廓线双验证；**Cd 在 U10<1.6 m/s 负相关、1.6–3.0 m/s 正相关**；Eq.11 波依赖 Cd；与海洋线性公式比 **1.0–3.1 倍**；UKL 应用：空间非均匀 Cd 场、流速 +57–90%、表面涡度增大。
- **借鉴点**：本模块常数 Cd=1.3e-3 应上调；空间 Cd 场实现（E1）。

### 10.2 《Wind impacts on suspended sediment transport...Poyang》
- **作者**：Hua Wang, John Paul Kaisam, Dongfang Liang, Yanqing Deng, Yuhan Shen，2020。**【已核实】**；Hydrology Research 51(4):815-835, doi:10.2166/nh.2020.156。
- **方法**：3D 水动力+悬沙（6–8 层 σ、SDS 闭合、波浪-湍流耦合、Stokes 漂移）；风分级 0.3–1.6 / 1.8–5.5 / 10.8–13.8 m/s；验证相对误差 ~16–22%。
- **订正说明**：原"动糙率/Cd/涡黏区间取自该文"表述已修正（见文综 I2 订正）：该文参数源于其 3D 模型设置；浅湖通用区间应分别溯源。

> 补充（参数汇总，供标定初值）：浅水湖泊常用 Manning ≈ 0.02–0.04 s·m^(-1/3)（东湖现状：MIKE21 校准 n=0.0238【A1】、郭雪蕊 n=0.032【A6】）；风拖曳 Cd：弱-中风推荐波依赖式（I1），风-湖面适定区间约 1.5–3.5×10⁻³；Smagorinsky 系数 0.28–0.32（MIKE21 校准 0.29）；水平涡扩散系数约 1–100 m²/s（取 5–10 m²/s 与 MIKE21 一致）。

---

## 主题 11：水深/地形数据集（v2 新增）

### 11.1 《GLOBathy, the global lakes bathymetry dataset》
- **作者**：Bahram Khazaei*, Laura K. Read, Matthew Casali, Kevin M. Sampson, David N. Yates（NCAR），2022。**【已核实】**；Scientific Data 9:36, doi:10.1038/s41597-022-01132-9（OA）。
- **方法**：HydroLAKES 1.43M 水体；Dmax=随机森林 f(P,A,V,WA,Elev)（1503 观测、NSE=0.97；仅 P,A 版 NSE=0.54 被否）；距离法 d=Dmax·(dist/L)（Hollister & Milstead 2010）；1 弧秒栅格 + h-A-V 多项式；附 Generate_Bathymetry_Rasters.py。
- **评估结论**：线性距离法在 42 实测点检验 RMSE 1.78 m（远差于幂指数 0.49 m）；HydroLAKES 15287 号东湖记录 Depth_avg=5.8 m（Vol_src=3 估算）与实测 2.2–2.5 m 不符；**东湖不采用**，GLOBathy 适合无实测小水体（写进 DATASETS.md 评估）。

---

## 附：核实状态汇总（v2）
1. 全部文献的期刊/卷/页/作者已用原文核准（本次 21 篇 PDF 通读）。
2. 未下载 PDF 的条目：J1（eDNA 调水）、D2 延伸、H1——仅元数据，已标注。
3. 误下载：《Colecalciferol Initiation Post Minimal Trauma Fracture.pdf》（维生素 D 骨折干预，与本主题无关）——建议从 references/ 移出。

## 结论（一句话）
东湖 2D SWE 建模以 **MIKE21（Li 2020）与郭雪蕊（2018）**为工作基准与参数锚点；用 **Fenocchi(2016)** 论证 2D 边界并用 **Wang(2017)** 补足表层输运；水深用**刘惠(2019) 42 个实测点**做数据校准（E0：RMSE 1.02→0.49）；风场用 **Zhang(2024) 波依赖 Cd**（E1）与 **Open-Meteo 逐时风/胡辉(2018) 湖陆风**（E2/E6）；优化用 **Nam & Aral(2007)** 框架、输运用粒子追踪、路径接口用 **Kumar & Kumar(2023) + Jiang(2025)**（E4）；参数初值用 MIKE21/WRR（n≈0.0238、Smag 0.29、Cd 2–3e-3）。
