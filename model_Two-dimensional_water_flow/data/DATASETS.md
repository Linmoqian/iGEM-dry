# 数据资源与数据使用报告（二维浅水流模型 · 武汉东湖）

> 本目录承担"数据获取报告"职能：数据集清单、内容说明、适配度评估、下载链接与实际下载情况。
> 关联文档：`../report/文献综述.md`（方法来源）、`../MODEL_ARCHITECTURE.md`（模型架构）。
> 下载状态如实记录（含失败/受限项）。注意：仓库根 .gitignore 已忽略 `**/data/`、`**/raw/`，本目录原始数据（含 820 MB HydroLAKES zip）**不入库**，随工作区保留；提交到 git 的只是报告文档与提取产物。

---

## 1. 数据集清单与适配度评估

### 1.1 水下地形 / 湖盆形态（核心）

| 数据集 | 内容 | 适配度 | 链接 | 下载情况 |
|---|---|---|---|---|
| **HydroLAKES v1.0（HydroSHEDS 全球湖库）** | 全球 >140 万湖泊多边形矢量（shp）与形态属性（面积、海拔、平均深度估值、Hylak_id 等） | 高：给出东湖权威矢量边界与官方深度估值，用于掩膜构建与交叉验证；水深为估值，非实测等深 | https://www.hydrosheds.org/products/hydrolakes （直链 https://data.hydrosheds.org/file/hydrolakes/HydroLAKES_polys_v10_shp.zip） | ✅ **已下载并校验**（zip 820,295,132 B，Python 流式下载后 zipfile 校验通过；已解压至 `data/raw/hydrolakes/`。**过程记录**：首次 Invoke-WebRequest 下载被截断为 580 MB（zip 校验失败），改用 Python urllib 流式下载 + zipfile.is_zipfile 校验成功。见 §2.1） |
| **GLOBathy（全球湖泊水深数据集, Khazaei et al. 2022, Scientific Data）** | 由 HydroLAKES 派生、基于地形代理插值的全球湖泊等深栅格（GeoTIFF） | 中：覆盖全球但分辨率粗（约 500 m），对 32 km² 东湖精度有限，可作为水深形态近似参考 | https://springernature.figshare.com/collections/_/5243309 | ⚠️ **未完整下载**：本环境 HEAD 202 / GET 超时；以链接与说明记录，建议后续网络环境重试（数据集较大、按湖分块） |
| **Copernicus DEM GLO-30（30 m 全球 DSM）** | 30 m 数字高程（陆地），片段 N30E114 覆盖东湖区 | 中高：用于湖岸线周边地形、湖盆周边环境与图件底图；**不能**提供湖内水深（水体本身无 DEM 信号） | AWS 公开桶：https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N30_00_E114_00_DEM/Copernicus_DSM_COG_10_N30_00_E114_00_DEM.tif | ✅ **已下载**（44,979,640 B ≈ 43 MB，`data/raw/Copernicus_DEM_GLO30_N30E114.tif`），见 §2.2 |
| OSM 水域多边形（东湖水系矢量） | 东湖及各子湖矢量多边形（郭郑湖、汤菱湖、后湖、水果湖、筲箕湖、庙湖等若干） | 高：本项目湖面掩膜的主数据源（Overpass API 实时抓取，含 31.2 km² 效果，与官方 31.75 km² 吻合） | Overpass API：https://overpass-api.de/api/interpreter （脚本 `../scripts/fetch_osm_*.py`） | ✅ **已下载**（`data/raw/osm_rings.json`、`osm_all_polys.json` 等原始 JSON），见 §2.3 |
| 东湖水下地形论文图 | 《武汉东湖水下地形测量方法研究》(地矿测绘 2004)；《长江经济带湖泊水下地形的热红外遥感反演——以武汉市东湖为例》(华中师大学报 2019) | 高（理想）：实测等深数据/等深图；但论文库需权限 | https://wap.cnki.net/touch/web/Journal/Article/DKCH200401006.html ；https://wap.cnki.net/touch/web/Journal/Article/HZSZ201905016.html | ❌ **未获取**（知网/万方付费权限）；已记录为待补数据 |

### 1.2 风场强迫（驱动力核心）

| 数据集 | 内容 | 适配度 | 链接 | 下载情况 |
|---|---|---|---|---|
| **Open-Meteo Historical Weather API（ERA5 备份再分析）** | 逐小时 10 m 风速/风向/气温（0.25° 网格插值到站点；**单位 km/h，使用须除以 3.6 转 m/s**） | 高：免费、无需注册；东湖中心 2023–2024 全年 17,544 个时次。**实测统计（已复核）**：年均 2.87 m/s、中位 2.50、P90 5.19；静风(小于0.5 m/s)占 1.5%，小于1 m/s占 6.9%；主导扇区 N 26.6%（年均圆形均值 59.3°=ENE）；夏季(6-8月)均值 2.75 m/s、圆形均值 142°（SE）；冬季(12-2月) 2.82 m/s、28.5° | https://open-meteo.com/en/docs/historical-weather-api ；接口示例 https://archive-api.open-meteo.com/v1/archive?latitude=30.557&longitude=114.404&start_date=2023-01-01&hourly=wind_speed_10m,wind_direction_10m | ✅ **已下载**（openmeteo_wind_enghu_2023_2024.json，17,544 小时；单位 km/h 已在统计脚本中换算），见 §2.4 |
| ERA5 原始数据（ECMWF CDS） | 0.25° 逐小时再分析（官方权威） | 高 | https://cds.climate.copernicus.eu | ⏳ 需注册 API key，**未下载**（记录为后续升级项） |
| 武汉市基本气象资料（站点统计口径，与再分析对照） | 主导北风、年均风速 1.8（含静风）/2.3（扣静风）m/s、静风概率 21.8% | 中（**站点口径**；与 ERA5 再分析口径不同，差异已在架构文档 §6 显式说明：静风概率 21.8% vs 1.5% 属口径差异，不再作为本模型的静风论据） | http://eia-data.com/武汉市基本气象资料/ | 记录为**对照源**（research_eastlake.md） |
| 《武汉城市区域水陆风环流的形成与转化特征研究》 | 湖陆风环流形成/转化（论文） | 中高：提供"日变化湖陆风"建模依据 | https://d.wanfangdata.com.cn/periodical/njxxgcdxxb201805002 | 文献记录，未下载（付费库） |

### 1.3 水位 / 水文边界

| 数据集 | 内容 | 适配度 | 链接 | 下载情况 |
|---|---|---|---|---|
| 东湖水文站（站码 61601200，长江水文长序列数据集） | 东湖水位、流量 | 高 | https://www.moonapi.com/YangtzeRiver/detail/index/id/1354.html （商业 API 汇总页） | ⏳ 长序列需申请/接口权限，**未下载** |
| 武汉市公共数据开放平台（东湖水位接口 opens0000001230） | 东湖水位公开接口 | 高 | https://data.wuhan.gov.cn/page/data/data_interface_details.html?cataId=37a7e913e2fb4767aec803e2bd0fa4a9&serviceCode=opens0000001230 | ⏳ 需登录/API 权限，**未下载** |
| 湖泊形态统计（湖底高程 15.12 m、正常高水位 19.78 m、历年最高 20.06 m、年较差 0.6–0.8 m） | 东湖水位特征值 | 高（作为水位边界先验） | https://wapbaike.baidu.com/item/东湖/6055 （转引《湖北省湖泊志》） | 已核实（不涉及下载） |

### 1.4 水质 / 蓝藻（关联模块）

| 数据集 | 内容 | 适配度 | 链接 | 下载情况 |
|---|---|---|---|---|
| CERN 湖北东湖湖泊生态系统国家野外科学观测研究站 | 东湖长期生态监测（水物理/水化学要素） | 高（本地实测，最贴合） | https://dhl.cern.ac.cn/ | ⏳ 平台公开浏览；下载/申请方式待核实，**未下载** |
| 中国湖泊营养状态时空观测数据集（1984–2023） | 全国湖泊营养状态（TSI）长时序 | 中高 | http://www.geodata.cn/data/datadetails.html?dataguid=197408932112662&docId=51 | ⏳ 需注册/分级授权，**未下载** |
| 中科院南京地湖所科学数据中心（太湖产品库 114 指标/175 集/27.7 GB） | 湖泊-流域一体化全要素 | 中高 | https://data.niglas.ac.cn | ⏳ 需注册，**未下载** |

### 1.5 本仓库既有数据（复用）

| 数据 | 说明 |
|---|---|
| `../model_redo/data/`、`../model/` | 项目既有美国湖泊（伊利湖/休伦湖）实测与模型模拟数据、USGS 蓝藻毒素数据、NHDPlus 流域数据——用于 ML 水质模型；本模块需求不同，仅作为跨湖参数化参照（如外推 Manning/扩散系数范围）。 |
| `../model_MC-LR_degradation_kinetics/` | 降解动力学模块参数（降解速率、菌浓度-时间关系）——**覆盖阈值（有效菌浓度 C_req）的取值来源**（本模块以相对阈值 `thr_rel` 预留接口，待标定）。 |

---

## 2. 实际下载明细

### 2.1 HydroLAKES（已完成并校验）
- 文件：`data/raw/HydroLAKES_polys_v10_shp.zip`（**820,295,132 B**；zipfile 校验 `is_zipfile=True`）
- 下载源：`https://data.hydrosheds.org/file/hydrolakes/HydroLAKES_polys_v10_shp.zip`（HTTP 200，公开直链，免注册）
- **过程记录（诚实的排错）**：初版经 PowerShell Invoke-WebRequest 下载得到 580,569,995 B（被截断，`End of Central Directory record` 缺失）；HEAD 显示真实 Content-Length=820,295,132；改用 Python urllib 流式下载成功并通过 zip 校验。
- 解压：`data/raw/hydrolakes/HydroLAKES_polys_v10_shp/`（HydroLAKES_polys_v10.shp 1.11 GB / .dbf 377 MB / .shx / .prj / TechDoc.pdf）
- **东湖记录提取**（geopandas+pyogrio 空间查询，见 `scripts/extract_hydrolakes.py`，结果 `data/raw/hydrolakes_eastlake_records.json`）：东湖主体在 HydroLAKES 中被划分为多块——主体 **Hylak_id=15287：24.28 km²、Depth_avg=5.80 m、Elevation=20 m、Vol_total=1.42×10⁸ m³**（114.3991, 30.5511）；北块 **175928：7.84 km²、Depth_avg=2.20 m**（114.4018, 30.5842）；东南块 15285（12.44 km²）；沙湖 175939（4.63 km²）；南湖 175975（9.21 km²）等。
- **交叉验证结论**：HydroLAKES 东湖主体+北块 ≈ **32.1 km²**，与 OSM 掩膜 **31.2 km²**、官方 **31.75 km²** 三方吻合（±3%）；Depth_avg 为统计模型估计（与实测 2.11–2.46 m 差异较大，特别 15287 给出 5.8 m），**故不作为正式水深场**——仅作形态交叉验证。
- 用途：① 东湖矢量边界交叉验证；② 湖盆形态属性对照。⚠️ 官方水深为估计值，精度不足，不用作正式水深场。

### 2.2 Copernicus DEM GLO-30（已完成）
- 文件：`data/raw/Copernicus_DEM_GLO30_N30E114.tif`（44,979,640 B）
- 下载源：AWS S3 公开桶直链（HTTP 200，免注册）
- 用途：周边地形底图、湖岸线环境评估、图件。

### 2.3 OSM 东湖水系矢量（已完成，本模型主数据源）
- 文件：`data/raw/osm_rings.json`（关系-成员-节点三层拓扑）、`data/raw/osm_lakes_bbox.json`、`osm_all_polys.json`、`osm_lakes_body.json` 等。
- 获取方式：Overpass API（POST query，递归 `>;` + out body + 节点坐标分块拉取）。
- 结果：东湖主体及子湖 18 个多边形，**OH** 掩膜面积 31.2 km²（官方 31.75 km² @ 正常高水位，吻合度 98%），网格 `data/processed/domain.npz`。
- 注意：OSM 中有少量重复映射（同一湖域 multipolygon 与 子湖 way 并存），已按"关系优先 + 并集栅格化"处理。

### 2.4 Open-Meteo 风场（已完成）
- 文件：`data/raw/openmeteo_wind_enghu_2023_2024.json`（2023-01-01 00:00 至 2024-12-31 23:00，共 17,544 个小时次：wind_speed_10m、wind_direction_10m、temperature_2m；Asia/Shanghai 时区）
- API：`https://archive-api.open-meteo.com/v1/archive?latitude=30.557&longitude=114.404&start_date=2023-01-01&end_date=2024-12-31&hourly=wind_speed_10m,wind_direction_10m,temperature_2m&timezone=Asia%2FShanghai`
- 用途：真实风场统计（季节变化、日均风速、湖陆风日变化）；场景驱动与不确定性分析。

### 2.5 未下载/受限数据（如实说明）
| 数据 | 原因 | 后续方案 |
|---|---|---|
| GLOBathy 等深栅格 | figshare GET 超时/大数据量 | 换网络重试；或以 GEE 在线 API 取东湖区块 |
| 东湖水下地形实测等深（论文） | CNKI/万方付费 | 校园网/机构权限下载；联系课题组成员 |
| 东湖逐时水位长序列 | 开放平台需登录/接口权限 | 申请接口；或退而用"水位年较差 0.6–0.8 m"作先验区间 |
| ERA5 官方数据 | 需 CDS 注册 API key | 申请 key 后替换 Open-Meteo |
| CERN 东湖站数据 | 平台下载流程待确认 | 邮件申请（cern 站开放数据服务） |
| 中国湖泊营养状态数据集 | geodata.cn 需注册授权 | 注册后申请；作为水质边界与校核 |

---

## 3. 数据使用决策（模型影响）

1. **湖面掩膜 = OSM 矢量**（31.2 km²，解析完善、免费、可复现）；**水深 = 形态学重建**（见 ARCHITECTURE 文档 §6：距离岸线指数深度剖面，均值 2.30 m / 最大 5.8 m 校准，文献参数：平均水深 2.11–2.46 m、最大近 6 m、湖底高程 15.12 m）。HydroLAKES/GLOBathy 作为交叉验证与后续升级源。
2. **风场 = Open-Meteo 逐时**（2023–2024）+ 武汉气候统计（主导北风、夏季东南风）设定场景；湖陆风日变化参数化列为待办。
3. **边界条件 = 闭湖（默认）** + 武丰闸/青山港入出流接口预留（数据未获取，接口保留）。
4. **阈值/耦合接口 = 降解动力学模块**（`../model_MC-LR_degradation_kinetics/`）提供 C_req；当前以相对阈值 thr_rel=5% 演示管线。

---

## 4. 数据引用（格式）

- HydroLAKES: Messager, M. L., Lehner, B., Grill, G., Nedeva, I., & Schmitt, O. (2016). Estimating the volume and age of water stored in global lakes using a geo-statistical approach. *Nature Communications*, 7, 13603. https://doi.org/10.1038/ncomms13603 （数据集：https://www.hydrosheds.org/products/hydrolakes ）
- Copernicus DEM GLO-30: Copernicus DEM (2022), ESA. https://doi.org/10.5270/ESA-c5d3d65 (30 m Global Digital Elevation Model).
- Open-Meteo: Zippenfenig, P. (2023). Open-Meteo.com weather API. Zenodo. https://doi.org/10.5281/zenodo.7970649
- GLOBathy: Khazaei, B., et al. (2022). GLOBathy, the global lakes bathymetry dataset. *Scientific Data*, 9, 36. https://doi.org/10.1038/s41597-022-01132-9
- OSM: © OpenStreetMap contributors (ODbL). East Lake (Wuhan) multipolygon data via Overpass API.
