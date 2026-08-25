# 模型重构数据集

本目录由 `../ANY2CSV/` 的 4,133 个 CSV 与原始目录中的 MAT、GeoTIFF、Shapefile、RAR/XLSX 等高价值非 CSV 资产共同构建。除用户明确要求删除的、已经完整校验并成功解压的 ZIP 外，原始数据均保留。所有派生表都能由 `../tmp_code/` 中脚本重建。

## 模型与数据边界

阅读 `model/` 与 `model_redo/` 后，重构模型应拆成三个任务：

1. **任务 A（主模型）**：以水体总微囊藻毒素（total microcystins / MICX，统一为 µg/L）为标签，进行浓度回归和由浓度派生的风险分级。
2. **任务 B（独立子模型）**：以 MC-LR 单一异构体（µg/L）为标签。MC-LR 与 ELISA 总 MC 的分析物定义、方法响应和分布不同，严禁混合成同一标签。
3. **任务 C（中国/东湖域适配）**：使用国内水温、DO、pH、浊度、营养盐、叶绿素 a 等无毒素标签数据做分布校准、预训练或外部情境分析；不能把叶绿素或藻密度伪造为毒素真值。

推荐先用基础特征训练：水温、DO、pH、浊度、电导率、TN、TP、氨氮、硝酸盐/亚硝酸盐、DOC、TSS、透明度和水深。`chlorophyll_a_ug_l`、`cyanobacteria_cells_ml` 与同样本 qPCR/荧光指标可能形成标签近端泄漏，应仅在单独的增强特征实验中使用。

## 主要输出

| 路径 | 内容 | 建议用途 |
|---|---|---|
| `model_tables/total_microcystins_model_ready.csv` | 总 MC、日期及至少 2 个基础环境特征均可用的记录 | 任务 A 默认训练入口 |
| `model_tables/total_microcystins_enriched_dynamic_ready.csv` | 总 MC + 实测/GLAST 动态特征 + CHELSA/HydroBASINS/HydroLAKES/WorldCover | 任务 A 推荐重构入口 |
| `model_tables/total_microcystins_enriched_static_baseline_ready.csv` | 允许只有静态环境背景的记录 | 仅静态基线，不与动态主模型混作同一性能结论 |
| `model_tables/total_microcystins_all_observations.csv` | 总 MC 全部观测，包括缺特征、缺标签及删失记录 | 审计、重新插补、外部连接 |
| `model_tables/mc_lr_model_ready.csv` | MC-LR 且具备可训练协变量的记录 | 任务 B 训练/验证 |
| `model_tables/mc_lr_enriched_dynamic_ready.csv` | MC-LR 的动态增强入口 | 任务 B 推荐入口 |
| `model_tables/mc_lr_all_observations.csv` | MC-LR 全部观测，包含 WQP 等仅标签记录 | 后续按站点和日期补充协变量 |
| `model_tables/microcystin_detection_from_concentration.csv` | 从浓度与 ND 标记得到的检出分类 | 检出/未检出分类实验 |
| `model_tables/microcystin_detection_iowa_annual.csv` | Iowa 湖泊年度检出标签与年度平均水质 | 独立分类任务；仅有年份，无伪造日/月 |
| `model_tables/china_covariates.csv` | 长江湖库、滇池和全国湖泊年度 TSI | 任务 C；无毒素标签 |
| `model_tables/taihu_multimodal_covariates.csv` | 太湖分区水质 + 同日气象/水位 + 年度遥感摘要 | 中国域预训练/分布适配，无毒素标签 |
| `model_tables/taihu_quarterly_multimodal_covariates.csv` | 太湖 14 站季度营养盐/Chla + 季度气象 + 年度遥感 | 中国域季度尺度预训练 |
| `model_tables/broad_microcystins_nodularins_auxiliary.csv` | 明确标注为“microcystins plus nodularins”的宽谱结果 | 辅助/迁移学习，不混入严格总 MC |
| `standardized/toxin_observations.csv` | 总 MC 与 MC-LR 的统一长表，保留 `target_kind` | 总审计表，不应忽略 `target_kind` 直接混训 |
| `standardized/site_registry.csv` | 来源内站点、湖泊名、地区与坐标去重表 | 空间分组和后续地理连接 |
| `source_tables/` | 每个已纳入来源的标准化结果 | 来源级核对与 leave-one-dataset-out 验证 |
| `catalog/dataset_manifest.csv` | 118 个数据集的用途、时间/地点/标签提示 | 全体数据资产索引 |
| `catalog/duplicate_groups.csv` | 内容哈希重复文件及推荐 canonical 顺序 | 防止重复采样进入训练/测试 |
| `reports/` | 连接率、完整率、处理摘要及 28 项校验 | 质量审计 |
| `reports/non_csv_format_assessment.csv` | 50 类非 CSV 资产的数量、体积、处置与理由 | 文件格式全量审计 |
| `FILE_FORMAT_ASSESSMENT.md` | ZIP/MAT/RData/RAR/7z/栅格/矢量处置说明 | 人工复核 |
| `DATA_GAPS_AND_AGENT_PROMPTS.md` | 当前关键数据缺口与搜索 Agent 提示词 | 下一轮数据扩张 |

## 关键处理规则

- 所有毒素目标统一为 `µg/L`；ppb 等同于 µg/L，ng/L 除以 1,000，mg/L 乘以 1,000。
- NARS 宽表/长表按来源提供的 `UID`（必要时 `UNIQUE_ID` 或 `SITE_ID`）连接毒素、水化学和站点信息。连接后行数不得膨胀。
- `sample_date` 只保存来源提供的真实日期。只有年份的数据保存在 `year`，并标记 `time_precision=year_only`，不伪造月份或日期。
- 经纬度只从同一来源的样本表或站点表回填；无坐标时保留站点/水体名称并在 `location_precision` 中说明精度。
- 未检出不删除：`target_raw` 保存原始表示，`is_censored=1`，检出限保存于 `censor_limit_ug_l`，`target_model_ug_l` 默认使用半检出限。训练时应对半检出限方案做敏感性分析或使用删失回归。
- `target_ug_l` 是解析后的原始数值；`target_model_ug_l` 是供默认训练的值。任何负分析值保留在全观测表并标记 `negative_excluded`，不进入 model-ready 表。
- 大于 1,000 µg/L 的值不擅自删除，标记为 `extreme_review_gt_1000`；建模前应按来源方法复核并做稳健变换。
- 总 MC、MC-LR、组织浓度、SPATT 树脂通量、每细胞毒素和 qPCR 拷贝数不会强行合并。
- Buffalo Pound 的总水体 MC/MC-LR 由同日期同深度的胞内与胞外组分相加，并由 ng/L 转为 µg/L；Saginaw Bay 由颗粒态与溶解态相加，含未检出组分时保留区间删失上界与中点估计。
- CHELSA 是 1981–2010 气候常年值，HydroBASINS/HydroLAKES/WorldCover 是静态背景；只有 GLAST LSWT 是按采样日期抽取的动态外部特征。静态值不能冒充采样日天气。
- 组织毒素保持 µg/g 并放在独立辅助表；Georgia 数据的匿名化坐标不会作为真实经纬度使用。
- 年月周期特征为 `sin(2π·month/12)` 与 `cos(2π·month/12)`。

## 单位字典

| 字段 | 含义 | 统一单位 |
|---|---|---|
| `target_ug_l`, `target_model_ug_l` | 毒素浓度 | µg/L |
| `water_temp_c` | 水温 | °C |
| `do_mg_l` | 溶解氧 | mg/L |
| `ph` | 酸碱度 | 无量纲 |
| `turbidity_ntu` | 浊度 | NTU/FNU（来源方法保留在来源文档） |
| `conductivity_us_cm` | 电导率 | µS/cm |
| `tn_mg_l`, `tp_mg_l` | 总氮、总磷 | mg/L |
| `ammonia_n_mg_l`, `nitrate_n_mg_l`, `nitrite_n_mg_l` | 无机氮形态 | mg N/L |
| `doc_mg_l`, `toc_mg_l`, `tss_mg_l` | DOC、TOC、悬浮物 | mg/L |
| `chlorophyll_a_ug_l` | 叶绿素 a | µg/L |
| `secchi_m`, `sample_depth_m`, `max_depth_m` | 透明度、采样深度、最大深度 | m |
| `cyanobacteria_cells_ml` | 蓝藻细胞密度 | cells/mL |

## 训练切分要求

随机逐行切分会把同一湖泊、站点或相邻日期泄漏到训练集和测试集。至少使用 `site_id`/`waterbody_name` 的 GroupKFold，并增加时间外推切分和 leave-one-dataset-out 验证。方法差异应通过 `dataset_id`、`method` 和 `target_kind` 保持可追溯，而不是在清洗阶段抹平。

## 复现

在仓库根目录执行：

```powershell
python model_redo/data/tmp_code/build_data_processed.py
python model_redo/data/tmp_code/extend_toxin_sources.py
python model_redo/data/tmp_code/extract_glast_lswt.py
python model_redo/data/tmp_code/extract_chelsa_features.py
python model_redo/data/tmp_code/extract_hydrobasins_features.py
python model_redo/data/tmp_code/extract_remote_sensing_features.py
python model_redo/data/tmp_code/process_china_context.py
python model_redo/data/tmp_code/build_enriched_model_tables.py
python model_redo/data/tmp_code/audit_non_csv_assets.py
python model_redo/data/tmp_code/validate_data_processed.py
```

成功时 `reports/validation_summary.json` 中 `failed` 为 0。
