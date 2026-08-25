# 非 CSV 数据处置与建模利用审计

## 结论

已审计 `external_raw/`、`raw/`、`nars/` 中 14,875 个非 CSV 文件（约 27.98 GiB，50 种扩展名）。“转换”采用信息保持原则：表格转为规范 CSV；栅格和矢量保留原文件，只抽取模型需要的时空特征；既有模型预测、SHAP、工程文件不进入训练。

完整机器可读清单见：

- `reports/non_csv_format_assessment.csv`
- `reports/non_csv_asset_decisions.csv`
- `reports/non_csv_assessment_summary.json`

## 压缩文件

- ZIP：原始 63 个 ZIP 中，62 个经 CRC、路径安全和文件完整性核验后解压并删除；另发现并处理 1 个嵌套 ZIP。仅 `external_raw/USGL_WQP_MicrocystinLR/state_subsets/state_26.zip` 保留，因为它是 0 字节，无法解压或验证。
- RAR：4 个 RAR 全部安全解压，共得到 236 个文件、2,885,831,210 字节；RAR 原包保留，可恢复。太湖 THQBCA、中国湖泊清单、太湖水质、太湖/巢湖食物网均已查看和利用。
- 7z：两个 NHDPlus 包保留。WBD 包与已存在的 `WBD_snapshot` Shapefile 重复；NationalCat 仅为 ArcInfo catchment-ID 栅格，不含建模属性，现有 HydroBASINS level-12 已提供更完整且全球一致的流域特征。
- tar.gz：Lake Erie 包内容与已解压并入池的 NOAA Lake Erie 数据相同，因此不制造第二份副本。

## MAT 与 RData

- `daily_LSWT_data.mat`（MATLAB 7.3/HDF5，14,610 日 × 92,245 湖泊）具有高价值。已按可靠湖泊匹配和真实采样日期稀疏抽取同日及前 3/7/14/30 天 LSWT，单位由 K 转为 °C。没有展开成十多亿行 CSV。
- `daily_LSWT_lakeinfo.mat`、`daily_LSWT_dateinfo.mat` 用作湖泊和日期轴。
- Rider `mc_shap_results*.mat` 是旧模型 SHAP 解释结果；EMS `ModObs*.mat` 含 `MOD/OBS/PreD` 旧模型数组。两类均属于泄漏源，只保留审计。
- Lake Erie `.RData` 是保存的 GAM/贝叶斯模型及作图对象。Python 的两套 RData 解析器均不能安全解析其复杂对象；其原始 2012–2021 现场 CSV 已存在并入池，因此不为读取派生模型对象额外引入 R 运行时。

## 栅格与空间数据

| 资产 | 已完成利用 | 语义限制 |
|---|---|---|
| CHELSA | 19 个气候常年特征按毒素坐标采样 | 1981–2010 静态气候，不是采样日天气 |
| GLAST LSWT | 1,346 条记录获得同日湖表温度 | 仅接受高可信湖泊匹配；覆盖至 2020 |
| HydroBASINS | 97.1% 有坐标记录匹配 level-12 流域 | 静态流域属性 |
| HydroLAKES | 湖面积、深度、体积、停留时间等 | 湖心匹配不等于采样点匹配，已保留距离/质量 |
| ESA WorldCover | 对下载瓦片覆盖坐标计算约 5 km 邻域类别占比 | 2020 静态土地覆盖；瓦片边缘会裁剪 |
| Taihu THQBCA | 220 幅 FAC/SDD/Chla/TSI/植被/土地覆盖/人口/夜光栅格年度摘要 | 湖区/栅格范围统计，不伪装成站点值 |
| Erhai PC | 3,167 天原始与处理版藻蓝蛋白摘要 | 单位来源未明确，跨数据集缩放前必须标定 |
| Yunnan Chla | 滇池、洱海、抚仙湖 2013–2022 平均 Chla 摘要 | 多年平均背景，不是单日值 |
| China lake inventory | 40,973 个湖泊代表点和面积 | 原数据无湖名，仅有 ID |

GeoTIFF 不适合逐像元转 CSV：那会重复坐标、放大至数十亿行并破坏投影、nodata 与空间邻接信息。当前做法保留原始 TIF，同时生成可训练的点特征或时序摘要。

## 不进入训练的其他文件

- `.vb3m/.vb3p`、SHAP、旧预测：派生模型产物，存在直接泄漏。
- JPG/PNG/BMP、无地理参考的显微 TIFF、论文图：没有校准后的数值标签。
- PDF/DOC/DOCX/MD/TXT/XML/JSON：用于单位、方法、许可证和来源审计。
- `.m/.r/.rmd/.ipynb/.sas/.sh`：用于复现和理解处理流程，不是观测行。
- `.gdbtable/.dbf/.shx/.prj/.sbn` 等：必须与所属 geodatabase/Shapefile 共同解释，不能拆成失去空间键的“独立 CSV”。

## 关键防泄漏决定

- MC-LR 与 total microcystins 分池。
- `microcystins plus nodularins` 独立为辅助表。
- 组织浓度 µg/g 与水体浓度 µg/L 分离。
- Buffalo Pound 胞内+胞外、Saginaw Bay 颗粒+溶解采用显式组分重建，并保留删失语义。
- 静态气候/流域/土地覆盖与动态测量分层，分别建立动态主模型和静态基线。
