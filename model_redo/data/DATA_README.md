# data 目录总览 — 模型重建数据仓库

> 更新日期: 2026-08-10（第二轮数据扩张完成：deep-research 定向搜寻）

## 目录结构

| 目录 | 内容 | 大小 |
|---|---|---|
| `raw/` | 本地原始数据(EMLS、Lake Erie、HABs、清远水龙头等,314 文件) | 0.05 GB |
| `external_raw/` | 外部数据集(140 个数据集目录,含 README) | 26.67 GB |
| `nars/` | EPA NARS 全国水生资源调查全量(16 组) | 1.35 GB |
| `tmp_code/` | 临时下载/处理脚本 | — |
| `DATA_README.md` | 本总览 | — |

**合计:约 28 GB。140/140 个数据集目录均有 README.md。**

## 第二轮数据扩张成果（2026-08-10，deep-research 工作流 + 定向下载）

### 1. 工作流核查（100 子智能体，23 条确认声明）
- **P0 东湖毒素**：未发现开放机器可读数据；CERN 东湖站无毒素指标；唯一论文级来源为贺小敏 2012（LOD MC-LR 0.0234 µg/L，无实测浓度）
- **P1 中国湖泊毒素**：确认 6 个 geodata.cn 毒素数据集存在（巢湖12点、太湖9点17项水质配对、太湖/巢湖/滇池7+5+2点、梅梁湾42条溶解态MC配对等），全部需注册+订单+人工审核
- **P2 外部动态**：确认 CLMS 湖面水温 NRT、GRDC 径流、GEE/CDS ERA5-Land 入口
- **P3 传感器**：EIS 抗体传感器 + 3D 打印荧光传感器补充材料已下载（标定曲线为图）

### 2. 新增 13 个数据集目录（全部含中文 README + SHA-256）
- **P3_Biosensor_EIS_MCLR_SciRep2024**（Sci Rep 2024 + Microchim Acta 2024 传感器标定补充）
- **CHN_Figshare_Taihu_Toxins_Su2015**（太湖32点毒素论文全文，不可训练）
- **CHN_Geodata_Chaohu_ToxinWQ_2008_2009**（巢湖12点×12月 MC+水质配对，P1 黄金目标，需申请）
- **CHN_Geodata_Taihu_MC_WQ_Paired_2009_2010**（42条溶解态MC+水温/pH/DO配对，需申请）
- **CHN_Geodata_Microcystis_Growth_Toxin_2021_2022**（IHB 2021-2022 产毒实验，唯一2021+源，需申请）
- **CHN_Geodata_LakeTaihu_ToxinFlux_2008_2009**、**CHN_Geodata_Taihu_WaterColumn_Toxin**、**CHN_Geodata_Taihu_Intracellular_Toxin**、**CHN_Geodata_FACHB905_Toxin_2009/2010**、**CHN_Geodata_ToxigenicStrains_2008_2012**（样例/文档级）
- **CHN_Figshare_Taihu_Microcystis_Growth_MC**、**P3_iGEM_Jilin2014_MCLR_Biosensor**（参考级）

### 3. 交付物
- `data_search_manifest.csv`（28 条候选/已下载数据集，含状态/URL/DOI/许可/哈希/适用度）
- `data_gap_coverage_report.md`（P0–P3 缺口报告 + 申请步骤 + 推荐申请文本）

### 1. EPA NARS 数据页全量下载 ✅
- 723 个文件全部下载成功(0 失败,1.3 GB),16 个调查组:
  - **NLA** 2007/2012/2017/2022(全国湖泊)— 2012/2017/2022 含总微囊藻毒素 MICX(ELISA, μg/L)
  - **NCCA** 2010/2015/2020(海岸+五大湖)— 2015 含 MC-LR 专属(LC-MS/MS)
  - **NRSA** 2008-09/2013-14/2018-19/2023-24(河流)— 2013 起含 MICX
  - **NWCA** 2011/2016/2021(湿地)、WSA 2008-09、NCA 2013-14
- 每组均有 README(字段/量纲/适用度评分)

### 2. 全网扫描(6 个子智能体并行)✅ 新增 83 个数据集目录(约 23.4 GB)

| 方向 | 新增目录数 | 亮点 |
|---|---|---|
| 中国湖泊水质 | 23 | 太湖 THQBCA(925MB)、云南高原8湖 MC、长江流域水质(317K行)、东湖/滇池/鄱阳湖系列 |
| 全球湖泊水质 | 15 | GEMStat 全球水质(42国)、德国 FRED、日本霞ヶ浦、维多利亚湖、英国 EA 湖泊网 |
| 卫星遥感 | 6 | GLAST 全球湖泊水温(9.2万湖)、洱海藻蓝蛋白、HydroLAKES、GLSEA 五大湖水温 |
| 流域/气候环境 | 7 | HydroBASINS、CHELSA 气候(8GB)、ESA WorldCover(6GB)、NHDPlus(2.5GB) |
| 学术仓库 | 21 | Iowa 湖泊 MC(1734行,ELISA)、伊利湖水华物候、乌拉圭、Buffalo Pound 等 |
| 五大湖补充 | 13 | WQP MC-LR 专属(13776行)、ECCC 五大湖水化(146万行)、NCEI 卫星 HAB 等 |

### 3. 旧数据集补 README ✅
- 43 个 8 月 6 日前下载的旧数据集目录已全部补写 README.md

## 关键发现

1. **MC-LR 专属标签**(任务 B):主要来自 EPA NCCA 2015(LC-MS/MS)、USGS Sacramento-SanJoaquin Delta(25,418行)、WQP MC-LR 查询(13,776行)、EMLS
2. **总 MC 标签**(任务 A):NLA 2012/2017/2022、NOAA 伊利湖、WQP 全美(72,660行)、HABs、NCCA 2020 等
3. **中国场景**(任务 C):东湖 NESDC 物化/生物/气象 + 太湖/滇池/巢湖系列 + 长江流域,但**均无毒素标签**(仅云南高原8湖有 MC 汇总 PDF,建议联系作者获取原始数据)
4. 两个重要缺口:HydroATLAS 属性表(figshare 403)与 EEA Waterbase(传输中断),均留有下载指引

## 需人工处理的源

| 源 | 原因 | 指引位置 |
|---|---|---|
| NASA Earthdata(CyAN 产品) | 需注册 | `RS_CyAN_Sentinel3_CI/README.md` |
| HydroATLAS BasinATLAS 属性表 | figshare 403 | `ENV_HydroATLAS/README.md` |
| EEA Waterbase WQ | 传输中断 | `EU_EEA_Waterbase_WQ/README.md` |
| ERA5-Land | 需 CDS 账号 | `ENV_ERA5/README.md` |
| GLCP 湖泊流域气候 | 需人机验证 | `ENV_GLCP/README.md` |
| geodata.cn 旧版 MC 数据集 | 需联系作者 | 中国智能体汇报 |
| NESDC/ScienceDB 部分 | 需登录 | 中国智能体汇报 |
