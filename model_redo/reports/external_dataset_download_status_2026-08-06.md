# 外部数据集对照、下载状态与补下载报告

> 复核日期：2026-08-06  
> 复核范围：对话中提出的“优先级—数据集—主要增量价值—需要注意”和“数据集—用途与限制”两类表格；本地 `model_redo/data/raw/`、`model_redo/data/external_raw/` 及其下载清单。  
> 说明：对话原表没有作为独立文件保存，本报告按仓库中的检索/审计文档和原表语义重建，并在末列加入“是否下载”。因此“是否下载”是对当前本地文件的核对结果，不是对远端目录存在性的推断。

## 1. 判定口径

- **是**：目标数据文件已落盘，并通过文件大小/哈希清单；ZIP/XLSX/DOCX 在最终库存中通过归档完整性检查。
- **部分**：数据集的可用主体或替代版本已落盘，但原发布中仍有一个或多个文件因官方 404、需要登录或超大文件不可续传而缺失。
- **否（受限）**：已核对官方元数据并重试，但下载端点持续返回 WAF/Cloudflare/登录页/错误页；错误页没有计入数据文件。
- “总 MC”与“MC-LR”严格区分：ELISA/总微囊藻毒素不能在报告中改称 MC-LR；WQP 的 `Microcystin` 查询也不等于 MC-LR 专属测定。

## 2. 原优先级表重建（新增“是否下载”列）

来源依据：`model_redo/reports/gpt_responses/stage3_external_dataset_search_response.md`、`model_redo/data/docs/外部数据源检索报告.md`。增量价值和注意事项按当前数据结构重新核对。

| 优先级 | 数据集 | 主要增量价值 | 需要注意 | 是否下载 |
|---|---|---|---|---|
| 高 | EPA NLA 2007/2012/2017/2022 | 多轮全国湖泊调查；水化学、营养盐、叶绿素、藻毒素和景观变量，适合总 MC 风险建模及跨轮次验证 | 轮次不是同一批湖；检测限、缺失和字段版本不同；行数是文件行而非去重样本数 | **是（四轮文件均在 `data/raw/NLA 2022/`；2017 另有外部副本）** |
| 高 | NOAA NCEI 0276941 Lake Erie | 与工程菌场景最接近的长期现场配对数据；总 MC、温度、营养盐、叶绿素、透明度、坐标和日期 | 目标是总 MC；同一湖泊/重复站点导致空间外推能力有限；检测限需左删失处理 | **是（本轮新增 13 个 NCEI 文件，并保留原始 3,074 行配对表）** |
| 高 | GLERL–CIGLR Western Lake Erie HAB | 五大湖 HAB 现场监测，含颗粒态/溶解态 MC、营养盐、荧光和 CTD 协变量 | 采样航次和项目协议不完全一致；颗粒态/溶解态不可直接当作 total MC | **是（NOAA/GLERL NCEI 目录已落盘，含 0276355 等 accession）** |
| 高 | EPA Water Quality Portal | 可按站点、时间和指标扩展全国水质观测；可作外部验证和 Cheney 14 年配对数据来源 | 字段名/单位/检测限不统一；`Microcystin` 聚合查询不是 MC-LR；MC-LR 精确查询返回 HTTP 400 | **是（全美 Microcystin ZIP+解包表；Cheney 站点全量结果另存）** |
| 中 | Figshare Global Microcystin（Buley et al.） | 全球湖库环境变量与总 MC，可检验跨地区迁移 | 文献汇编异质性大，检测方法和非检出规则不同；当前 Figshare/T&F 端点对本网络出口持续 403 | **否（受限；已确认 DOI/文章 16574963，未保存 WAF 页）** |
| 中 | data.gov 20 Reservoirs 1987–2018 | 多水库长期水质与蓝藻数据，可补充时间序列和水库类型 | 目标字段并非每条都明确为 MC-LR；站点/年份结构需重新整理 | **是（EPA 20 Reservoirs 13 个文件）** |
| 中 | USGS Tennessee Reservoirs 2022–2024 | 水库现场总 MC、营养盐和现场协变量，补充非 Erie 场景 | 样本量较小、站点和年份集中；不适合作为唯一训练集 | **是（9 个文件）** |
| 中 | Cheney Reservoir 14-year | 单一水库长期环境—藻毒素关系；可演示时间外推、滞后特征和可解释建模 | 同湖长期序列会放大“湖泊识别”捷径；官方 2022/2015 ScienceBase 有缺失对象 | **是（WQP 全量结果 + 2020 浮游植物版；官方缺失对象标为部分）** |
| 低 | USGS Large Rivers 2017–2019 | 河流/大河场景的 MC 与浮游植物配对数据，做跨水体外部测试 | 2019 某 CSV 404；不同年份文件结构和检测方法需统一 | **部分（2017/2018 及大部分 2019、浮游植物已在；1 个 2019 对象缺失）** |
| 低 | USGS North Atlantic Appalachian 2020 | 五个河流盆地的毒素、基因、藻类、叶绿素和 sonde 数据；新增区域外推 | 单次季节采样、样本量小；“总 MC”与基因信号不能混为标签 | **是（本轮新增 9 个文件）** |
| 低 | USGS SE Wadeable Streams 2014 | 75 条东南部涉水河流的 MC、水质、藻类和站点信息；可作跨河流验证 | 2014 单年、站点异质性高；不能替代湖泊长期序列 | **是（本轮新增 5 个文件）** |
| 中国辅助 | CNEMC / NESDC 东湖站 / Figshare 中国湖库 | 为东湖 covariate-shift、基线水质和气象对齐提供中国场景特征 | 东湖公开包不含 MC 标签；Figshare 中国全国水质包当前 403；不能用无毒素标签数据宣称完成 MC 预测 | **部分（NESDC 东湖物化、生物、气象三组已下载；Figshare 22584742 未下载）** |

## 3. 本地数据用途与限制表（新增“是否下载”列）

该表把 `数据源审计报告.md`、`建模数据选择方案.md` 中的“用途/风险/限制”合并为用户要求的“用途与限制”。

| 数据集 | 用途与限制 | 是否下载 |
|---|---|---|
| EMLS Europe（369 行） | 唯一明确含 `MC_LR_ugL` 的本地专属 MC-LR 数据；适合做 MC-LR 小样本、左删失和跨洲探索。限制：2015 年夏季、欧洲湖泊、零值/LOD 含义需确认，不能代表东湖或五大湖长期泛化。 | **是（本地 raw）** |
| Lake Erie v2 / NCEI 0276941（3,074 行） | 总 MC 主训练/时间外推展示，环境特征较完整、工程菌场景相近。限制：同湖重复测量、总 MC 非 MC-LR、`<0.15` 等检测限必须单独处理。 | **是（raw + external_raw）** |
| HABs Training（3,664 行） | 全国水质—MICX 关系和总 MC 风险分类；可与 NLA 环境特征对齐。限制：约 66% MICX 缺失，跨源字段转换和空间泄漏风险高。 | **是（本地 raw）** |
| EPA NLA 2012/2017/2022 toxin + water chemistry | 全国湖泊、跨轮次外部验证和风险分类；可用于 GroupKFold/leave-one-survey-out。限制：非面板同湖数据，检测限和轮次字段不一致，不能把统计行数当作独立样本数。 | **是（本地 raw；2017 另有 external 副本）** |
| EPA NCCA 2015 Great Lakes LC/MS/MS | 五大湖 LC/MS/MS 多毒素，含明确 MCLR 字段；适合 MC-LR 测量学验证和检测限敏感性分析。限制：环境协变量需与水质表拼接，不能直接作完整特征训练集。 | **是（external_raw）** |
| WLE Weekly 2025 / NOAA Saginaw Bay | 提供最新周尺度环境与颗粒/溶解态 MC，适合外部验证和时序展示。限制：时间短、检测比例不高、颗粒/溶解态与 total MC 定义不同。 | **是（raw + external_raw）** |
| NCEI Lake Pontchartrain 2020 | 大量现场附件和水质记录，可补充监测流程、元数据和多仪器数据。限制：附件/照片占比高，需先筛选可建模表；地点单一且不一定有 MC-LR。 | **是（external_raw）** |
| France cyanobacteria/cyanotoxins 2021–2025 | 跨年度公共浴场蓝藻/毒素监测，适合分类阈值和地域迁移。限制：法规监测字段、方法和单位与美国科研数据不同，不能直接拼接回归。 | **是（external_raw）** |
| Cheney Reservoir 2003–2022 | 长期单湖环境—总 MC/浮游植物关系，适合滞后特征和时间外推演示。限制：单湖容易过拟合；2022/2015 发布存在不可下载对象，WQP 与 phytoplankton 需按日期对齐。 | **是（替代/主体已下载，官方发布为部分）** |
| USGS Great Lakes/MS River ELISA | 总 MC 的 ELISA 实验/野外数据，提供跨水体测量参考。限制：两个 ScienceBase CSV 对象 404，现有主体仍需检查站点字段和实验设计。 | **部分** |
| USGS Raritan River Basin 2020–2021 | 新泽西河流/水库的营养盐、叶绿素、浮游植物、qPCR 与 discrete MC，适合跨区域协变量测试。限制：4 个官方表对象 404，不能声称完成原发布全量。 | **部分** |
| USGS North Atlantic Appalachian 2020 | 毒素、藻类、基因和 sonde 的区域外推/机制辅助集。限制：单季节、小样本，基因丰度不是毒素浓度。 | **是** |
| USGS SE Wadeable Streams 2014 | 现场 MC、水质与历史藻类表，适合 leave-one-region-out 验证。限制：河流单年样本，不适合作湖泊主训练。 | **是** |
| NESDC 东湖 2002–2006 物化/生物、2005–2006 气象 | 中国本地 covariate-shift、特征分布对齐和后续东湖验证准备；已含水温、DO、pH、营养盐、叶绿素、生物群落和气象。限制：公开包无 MC 标签，不能独立训练毒素监督模型。 | **是（3 个压缩包并已解包）** |
| Figshare 中国长期水质（DOI 10.6084/m9.figshare.22584742） | 可为中国湖库协变量分布提供更广覆盖。限制：当前 Figshare API/下载端点持续 403，未取得文件；需换网络或人工下载后再验哈希。 | **否（受限）** |
| Dryad Uruguay、Figshare Global Buley、Alberta bloom surveillance | 分别可提供南美河口、全球汇编、加拿大监测数据，作为可选迁移/敏感性分析集。限制：当前 WAF/Cloudflare 阻断，且方法异质性较大。 | **否（受限）** |

## 4. 最终本地库存

最终清单：[`full_download_manifest_2026-08-06_final_inventory_rerun_2026-08-06.json`](../data/external_raw/_manifests/full_download_manifest_2026-08-06_final_inventory_rerun_2026-08-06.json)、[`CSV 清单`](../data/external_raw/_manifests/full_download_manifest_2026-08-06_final_inventory_rerun_2026-08-06.csv)。

| 范围 | 数据集目录 | 文件数 | 总字节 | 约容量 |
|---|---:|---:|---:|---:|
| `model_redo/data/external_raw/` | 39 | 1,768 | 2,218,267,116 | 2.06 GiB |
| `model_redo/data/raw/`（原有本地原始数据） | — | 1,266 | 2,291,345,893 | 2.13 GiB |

最终 external_raw 中没有 `.part` 临时文件；ZIP、XLSX、DOCX 归档检查通过；所有 1,768 个库存文件均有 SHA-256 记录。WQP 的 `result.csv` 同时保留了原始 ZIP 和解包副本，统计容量会计入两份物理文件，但建模时应只选择一份。

## 5. 本轮重试与结果

| 批次 | 结果 |
|---|---|
| 直接源重试（data.gov、Figshare、Dryad、Alberta、USGS NLA 2007） | EPA/USGS 已存在；Georgia Figshare 4 个文件仍 403；Dryad 5 个文件仍 WAF；Alberta 4 个 XLSX 仍 Cloudflare 403。 |
| ScienceBase 原有清单重试 | 已存在对象全部复用；原有 404 对象仍失败；`Phytoplankton_Tally.xlsx` 官方报告约 837.6 MB，服务器忽略 Range 并重置传输，未保存不完整文件。 |
| NOAA NCEI accession 0276941 | 成功新增 13 个文件，0 失败。 |
| Cheney 旧版及 WQP | 成功取得 USGS Cheney 2020 版、站点全量结果、Microcystin 子集和站点表；2022/2015 ScienceBase 缺失对象由 WQP/旧版数据补足主体。 |
| USGS 新增区域源 | North Atlantic 2020（9）、SE Wadeable 2014（5）、NC Drinking Water Reservoirs（5）成功；Great Lakes/MS River ELISA 成功 5/7；Raritan 成功 8/12。 |
| Zenodo Clear Lake 70-year | 成功取得 35,589,186 bytes 的单 CSV。 |
| NESDC 东湖 | 物理化学、生物、气象三个公开压缩包成功下载并解包；压缩包内含 XLS 数据与关联 PDF/JPG。 |
| Figshare 中国长期水质、Buley Global Microcystin | API/下载端点持续 HTTP 403，未伪造成功状态。 |

## 6. 仍需人工或换网络处理的项目

1. Figshare/T&F 文章 16574963（Buley global microcystin）、Figshare 中国水质 22584742、USDA Georgia：需要可通过其 WAF 的浏览器会话或人工下载。
2. Dryad Uruguay、Alberta：需要通过其挑战页后再下载，下载后应按 API 提供的文件大小和 SHA-256 复核。
3. ScienceBase 返回 404 的对象：Lake Ontario 2023 3 个浮游植物 CSV、Ohio 3 个模型 ZIP、Clinch 1 个 CSV、Large Rivers 2019 1 个 CSV、Oregon 1 个 CSV、Great Lakes/MS River 2 个 CSV、Raritan 4 个 TXT，以及 Cheney 2015/2022 的部分 CSV/XLSX。它们不是重试次数不足，而是当前官方对象本身失效或被下架。
4. `USGS_CyAN_FIELD` DOI 解析到 USGS GitLab 登录页，属于软件/交互工具入口，不应当作为独立观测数据集计数。

## 7. 对建模的直接结论

当前数据已足以完整演示“环境特征 → 总 MC 风险/浓度 → 分组外部验证 → 东湖协变量迁移”的闭环；新增的 NCEI、WQP、Cheney、North Atlantic、SE Wadeable 和 NESDC 东湖数据提高了展示完整性。 但它仍**不足以支撑严格的 MC-LR 专属高泛化回归**：明确 MC-LR 标签仍主要来自 EMLS 与 EPA NCCA，东湖数据没有毒素标签。后续验证时可替换同目录文件并复训，但必须保持任务标签、检测限处理和按湖泊/站点/年份分组的评估协议不变。

## 8. 官方入口（可复核）

- [EPA/USGS Water Quality Portal 下载说明](https://www.epa.gov/waterdata/water-quality-data-download)
- [NOAA NCEI accession 0276941](https://www.ncei.noaa.gov/archive/accession/0276941)
- [GLERL-CIGLR Western Lake Erie 数据目录](https://catalog.data.gov/dataset/physical-chemical-and-biological-water-quality-monitoring-data-to-support-detection-of-har-2012)
- [USGS Cheney Reservoir 浮游植物数据（ver. 4.0）](https://www.usgs.gov/data/phytoplankton-data-cheney-reservoir-near-cheney-kansas-june-2001-through-october-2022-ver-40)
- [USGS Cheney 14 年建模论文/数据背景](https://pubs.usgs.gov/publication/70181018)
- [USGS SE Wadeable Streams 2014 数据目录](https://catalog.data.gov/dataset/periphyton-1993-2011-and-water-quality-2014-data-for-etampc-article-entitled-spatial-and-t)
- [NESDC 湖北东湖站资源页](https://www.nesdc.org.cn/otherProject/index?menuId=station&pageIndex=1&pageSize=15&projectId=1009)
- [NESDC 东湖 2002–2006 水物理水化学资源](https://www.nesdc.org.cn/sdo/detail?id=5fa5418f042ebb70d0c83471&subjectCode=1009)
- [Zenodo Clear Lake 70 年数据](https://zenodo.org/records/8352065)
- [Dryad Uruguay 数据集](https://datadryad.org/dataset/doi%3A10.5061/dryad.9w0vt4bpz)
- [Alberta cyanobacteria bloom surveillance](https://open.canada.ca/data/en/dataset/76a54113-1381-4824-b39c-2b32d2dfc652)
- [Buley et al. Global Microcystin Figshare 文章](https://tandf.figshare.com/articles/dataset/Predicting_microcystin_occurrence_in_freshwater_lakes_and_reservoirs_assessing_environmental_variables/16574963)
- [中国长期水质 Figshare DOI](https://doi.org/10.6084/m9.figshare.22584742)
