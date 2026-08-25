# 武汉东湖（Wuhan East Lake）二维浅水流模型基础调研报告

> 面向 iGEM 干实验「无人机投放点推演 & 单次覆盖面积」二维浅水流建模。
> 目标区：湖北省武汉市武昌区/洪山区，约 30.55°N, 114.37°E（用户提供参考值；东湖主体中心约 30.57°N, 114.40°E，待用行政/矢量边界核实）。
> 调研日期：本会话进行时。所有数字均标注**来源 URL**；**已核实**=可从所引 URL 直接读取；**待核实/猜测**=存在但我未能从 URL 直接验证或数值存疑。

---

## 1. 东湖湖泊基本特征

### 1.1 湖面面积 / 容积 / 集水面积

| 指标 | 数值 | 状态 | 来源 URL |
|---|---|---|---|
| 湖面面积（正常高水位 19.78 m） | **31.75 km²** | 已核实 | https://wapbaike.baidu.com/item/%E4%B8%9C%E6%B9%96/6055 （转引《湖北省地方志编纂委员会/湖北省湖泊志》） |
| 湖面面积（水位 21.0 m） | **32.8 km²** | 已核实 | 同上 |
| 表面积（维基百科） | **33.7 km²** | 已核实（同源志书数据） | https://zh.wikipedia.org/zh-cn/%E4%B8%9C%E6%B9%96_(%E6%AD%A6%E6%B1%89) |
| 湖泊容积（19.78 m 水位） | **8150 万 m³（0.815 亿 m³）** | 已核实 | 百度百科东湖词条（同 URL） |
| 最大湖容（21.0 m 水位） | **1.241 亿 m³** | 已核实 | 同上 |
| 本湖集水面积 | **约 119 km²**（另见 126 km²） | 已核实 | 百度百科东湖词条（119）；东沙湖水系段（126） |
| 集水面积（维基百科 infobox） | **127.5 km²** | 已核实 | 维基百科东湖词条 |
| 全流域（含沙湖、杨春湖、戴家湖等）面积 | **约 190 km²** | 已核实 | 百度百科东湖词条 |
| 东湖水系（东沙湖水系）汇水面积 | **204 km²**（东湖126、沙湖54、杨春湖24） | 已核实 | 百度百科东湖词条（东沙湖水系段） |

> 备注：志书文本亦出现`最宽处 28 公里`，但与 32 km² 面积、115.5 km 岸线明显不协调（或指景区/水系最大跨度而非湖面宽度），**列为待核实**。

### 1.2 水深

| 指标 | 数值 | 状态 | 来源 URL |
|---|---|---|---|
| 湖底高程 | **15.12 m**（黄海基面） | 已核实 | 百度百科东湖词条 |
| 历年实测最高水位 | **20.06 m**（黄海基面） | 已核实 | 同上 |
| 最大水深 | **近 6 m（最深 6 m）** | 已核实 | 百度百科东湖词条 |
| 平均水深（7 月中旬） | **2.46 m** | 已核实 | 同上 |
| 平均水深（10 月） | **2.11 m** | 已核实 | 同上 |
| 湖盆形态 | 北浅南深，东西差别较小；属浅水湖 | 已核实 | 同上 |

> 相关论文（可提供东湖等深图/水下地形）：《武汉东湖水下地形测量方法研究》（地矿测绘 2004）https://wap.cnki.net/touch/web/Journal/Article/DKCH200401006.html ；《长江经济带湖泊水下地形的热红外遥感反演——以武汉市东湖为例》（华中师范大学学报 2019）https://wap.cnki.net/touch/web/Journal/Article/HZSZ201905016.html 。

### 1.3 湖岸线长度 & 岸线系数

| 指标 | 数值 | 状态 | 来源 URL |
|---|---|---|---|
| 湖岸线总长 | **115.5 km** | 已核实 | 百度百科东湖词条 |
| 湖岸曲折系数（岸线系数）K | **5.03**（约为洪湖 K 值的 2 倍以上） | 已核实 | 同上 |
| 大小湖湾数量 | **120 多个**（“九十九道湾”） | 已核实 | 同上 |
| 岸线系数自洽校验 | K≈5.0 与 A≈32 km²、L≈115.5 km 基本吻合 | 公式校验（非直接来源） | https://zh.wikipedia.org/zh-cn/%E4%B8%9C%E6%B9%96_(%E6%AD%A6%E6%B1%89) |

### 1.4 湖区划分（子湖）

已核实（百度百科/湖北省湖泊志文本中明确提及的子湖）：**郭郑湖、汤菱湖、后湖、水果湖、筲箕湖**。富营养化程度排序（同来源）：筲箕湖 > 水果湖 > 郭郑湖 > 汤菱湖 > 后湖。
来源：https://wapbaike.baidu.com/item/%E4%B8%9C%E6%B9%96/6055

已核实（东湖国家湿地公园段）：**团湖、后湖、喻家湖**（湿地公园水域，总面积 10.2 km²，水域 6.5 km²）。来源同上。

任务提及的 **庙湖、小谭湖（小潭湖）**：属东湖常见子湖划分，官方页《东湖风景区 2019 年 1 月各子湖水质情况》对应列出各子湖水质，但该页为 JS 渲染，我未能直接解析点名；**庙湖/小谭湖的面积区间、边界待核实**。
来源：https://www.whdonghu.gov.cn/zwgk_6255/xxgkml/gysyjs/hjxx/201902/t20190201_144748.shtml

> 建模建议：二维模型分湖区可先按「郭郑湖、团湖、后湖、庙湖、汤菱湖、小潭湖、筲箕湖、水果湖、喻家湖」作为子湖单元，具体边界与面积需从《武汉湖泊志》或官方矢量湖界获取（**待核实**）。

### 1.5 入湖/出湖通道、水系连通与调水工程

- 东湖通过 **沙湖港、青山港** 与 **沙湖、杨春湖、戴家湖** 相连，构成小型湖泊水系（全流域约 190 km²）。——已核实，https://wapbaike.baidu.com/item/%E4%B8%9C%E6%B9%96/6055
- 东湖为**长江右岸湖泊**；历史上湖水夏涨冬枯，受长江水位制约；**青山港武丰闸建成后**东湖成为**人工控制的内陆水体**，水位变化平缓。——已核实，同上
- **引江济湖 / 大东湖水网连通**：《武汉市大东湖水网连通治理工程浅析》（《人民长江》2010 年第 11 期）https://wap.cnki.net/touch/web/Journal/Article/RIVE201011024.html ；湖北省水利水电规划勘测设计院版 https://cms.hubwd.com/kjrc/kjcx/2993902.shtml （该站 SSL 证书在本环境不可信，正文细节**待核实**）。
- 大东湖水网引水线路（“大东湖”生态水网、六湖连通）——已核实（报道存在），http://news.cjn.cn/tbbd/200910/t1011970.html ；http://www.whcjwzb.com/ssxw/201010/t20101009_32526.htm
- **武丰闸泵站**（东沙湖水系引排“动力心脏”）——已核实（报道存在），http://www.whshmgs.cn/news_detail/54.html ；http://www.whshmgs.cn/service_info/71.html
- **沿湖水厂（含余家头水厂）**：沿湖建有大小 **8 个水厂**，原设计最大供水能力 **35.0 万 m³/天**；1980 年代中期后因富营养化供水职能下降、转用长江水。余家头水厂属武昌段主要水厂之一（**余家头具体取水口/与东湖关系待核实**，水厂本身存在）。——已核实（8 厂 / 35.0 万 m³/天），https://wapbaike.baidu.com/item/%E4%B8%9C%E6%B9%96/6055
- 水量平衡（1979 年实测，来源同上）：入汇总量 11989.4 万 m³，其中沿湖 10 个主要排污口年排 6254 万 m³（占 52%），流域降雨径流 5000.4 万 m³，湖面净雨 735 万 m³；沿湖 13 个农用泵站抽水；1980 年代中期前需引长江水补充，其后转为向长江排水。

### 1.6 湖泊水位监测站与历年水位数据

- **东湖水文站**：站码 **61601200**，属“长江水文高频长序列监测数据集”，含**水位、流量**字段。该站确为“东湖 水文站”。——已核实（站名+站码），https://www.moonapi.com/YangtzeRiver/detail/index/id/1354.html （该平台为商业 API 汇总页，字段可参考）
- **武汉市公共数据开放平台**：存在“东湖水位”**数据接口详情**（serviceCode=opens0000001230）。——已核实（接口页存在），https://data.wuhan.gov.cn/page/data/data_interface_details.html?cataId=37a7e913e2fb4767aec803e2bd0fa4a9&serviceCode=opens0000001230 （页面 JS 渲染，需登录/API 读取）
- 监测站建设：武汉市为多个湖泊新建**水文监测站**（2014 年报道：20 个湖泊 24 小时实时监控水位），东湖为其中之一。——已核实（报道），http://news.cjn.cn/sywh/201401/t2419062.htm
- **历年水位特征值**（水文结论，来源志书）：历年实测最高水位 **20.06 m**、湖底高程 **15.12 m**、最高控制水位限定、水位年较差一般 **0.6~0.8 m**（个别 >1 m，历年最大 2.5 m）、月变幅 20~30 cm。——已核实，https://wapbaike.baidu.com/item/%E4%B8%9C%E6%B9%96/6055
- **公开历年水位长序列**：未找到官方开放可直接下载的东湖逐年/逐日水位长序列；入口（武汉市公共数据开放平台接口、长江水文数据集）多为“需访问/注册”性质，**历史长序列数据本体待核实**。
- 历史警示：2003 年报道《监测水位数据名不符实 武汉东湖深浅无人知》指出东湖水位/水深监测曾存在数据不足问题。——已核实（报道存在，历史情况），https://news.sina.com.cn/c/2003-05-10/13101043484.shtml

### 1.7 武汉年均风速 / 盛行风向 与东湖湖风小气候

- **武汉市基本气象资料**（环境气象数据服务平台）：**主导风向为北风**；**静风发生概率 21.8%**；**扣除静风年平均风速 2.3 m/s**；**含静风年平均风速 1.8 m/s**；春、夏、秋、冬均盛行北风，平均风速 1.7~1.8 m/s。——已核实（按该站数据），http://eia-data.com/%e6%ad%a6%e6%b1%89%e5%b8%82%e5%9f%ba%e6%9c%ac%e6%b0%94%e8%b1%a1%e8%b5%84%e6%96%99/
  - ⚠️ **待核实提示**：该平台“四季均盛行北风”与长江中下游夏季受东南季风影响的普遍规律存在张力，可能反映特定站点/近地面风场统计口径；二维模型若用风场，建议以气象部门武汉站（或东湖附近站）逐时风资料复核。
- **湖/水陆风小气候**：《武汉城市区域水陆风环流的形成与转化特征研究》（《南京信息工程大学学报》2018 年第 10 卷第 5 期）研究武汉城市**水陆风（湖陆风）环流**形成与转化特征，可作东湖湖风/日变化环流建模依据。——已核实（论文存在），https://d.wanfangdata.com.cn/periodical/njxxgcdxxb201805002 ；https://aipub.cn/1AA1DaL
- **湖水/湖区温度**：东湖多年平均水温 **17.7 ℃**，湖区多年平均气温 **16.7 ℃**（水温约高 1 ℃）；最高月均 29.7 ℃、最低月均 4.8 ℃，年较差 24.9 ℃。——已核实，https://wapbaike.baidu.com/item/%E4%B8%9C%E6%B9%96/6055

---

## 2. 中国相关湖库数据集（名称 / 内容 / 适配度 / 链接 / 是否需注册）

| # | 数据集名称 | 内容 | 对二维模型适配度 | 链接 | 是否需注册 |
|---|---|---|---|---|---|
| 1 | 中国湖泊营养状态时空观测数据集（1984–2023 年） | 全国尺度湖泊营养状态（TSI）长时序观测 | **高**（富营养化/水质时空数据，可作养分边界与校核） | http://www.geodata.cn/data/datadetails.html?dataguid=197408932112662&docId=51 ；https://lake.geodata.cn/data/datadetails.html?dataguid=197408932112662&docid=32 | **需注册**（geodata.cn 登录/注册/分级授权） |
| 2 | 国家地球系统科学数据中心（geodata.cn）其他湖泊/流域数据 | 湖泊、流域、土壤、气象等地球系统科学数据 | **中—高** | https://geodata.cn ；https://www.geodata.cn/data/index.html | 需注册；部分需申请 |
| 3 | 中科院南京地理与湖泊研究所科学数据中心（data.niglas.ac.cn）中国湖泊数据库/湖泊水深/大型湖泊数据集 | 中国湖泊基础数据、湖泊水深、太湖等湖泊-流域一体化全要素数据产品库（**114 指标要素、175 数据集、27.7 GB**） | **高**（湖泊水深/形态/流域） | https://data.niglas.ac.cn ；太湖产品库报道 https://cms.casdc.cn/article/450 | 需注册/登录（太湖产品库页含登录/注册） |
| 4 | 中科院水生生物研究所——湖北东湖湖泊生态系统国家野外科学观测研究站（CERN 东湖站） | 东湖长期生态监测：水物理要素（透明度、水深、电导率、盐度、温度、浊度）、水化学要素（阴/阳离子）等 | **高**（东湖本地实测，最贴合模型） | https://dhl.cern.ac.cn/ ；https://ihb.cas.cn/jgsz_1/kybm/ywtz/hbdhxtxt/ | 站内“数据资源/数据服务”页可浏览；详细下载/申请**待核实** |
| 5 | GLOBathy 全球湖泊水深数据集 | 由 HydroLAKES 派生、地形插值的全球湖深/等深（Khazaei 等） | **中**（全球、分辨率较粗，对 32 km² 东湖精度有限，可作近似参考） | https://springernature.figshare.com/collections/_/5243309 | 无需注册（公开）；本环境 HEAD=202、GET 超时 |
| 6 | HydroLAKES（HydroSHEDS）全球湖库数据集 | 全球 >140 万湖泊的形态与属性 | **中**（东湖具体水深精度不足，可交叉验证） | https://www.hydrosheds.org/products/hydrolakes | 无需注册 |
| 7 | McGill HydroLAKES 站点 | HydroLAKES 源码/文档镜像 | 参考 | https://wp.geog.mcgill.ca/hydrolakes/ | 无需注册；**本环境访问超时** |
| 8 | 全球湖泊营养状态指数（TSI）数据集（2003–2023 年） | 全球湖泊 TSI 数据集 | **中**（与 geodata.cn 中国营养状态数据交叉） | https://escience.org.cn/metadata/detail?cstrId=CSTR%3A17099.11.G122705413858085.20250929.v1 | 需注册（escience 元数据平台） |
| 9 | 《武汉湖泊志》（武汉市水务局主编） | 武汉市湖泊志书，含东湖及各子湖基础信息 | **高**（权威文字/湖界） | https://baike.baidu.com/item/%E6%AD%A6%E6%B1%89%E6%B9%96%E6%B3%8A%E5%BF%97 （本环境 403，需其他入口）；湖北省湖泊志系列《东湖》 https://book.qq.com/book-read/23312733/7 | 无需注册（公开出版/会员阅读） |
| 10 | 武汉市志·城市建设志（武汉地方志数字方志馆） | 武汉城市建设/湖泊治理志书 | **中—高** | https://szfzg.wuhan.gov.cn/book/dfz/bookall/id/1024/category_id/384632.html ；https://whfzg.org.cn/book/dfz/bookall/id/971/category_id/346411.html | 无需注册 |
| 11 | 湖北省生态环境厅/地表水水质监测 | 湖北省地表水国控/省控断面水质数据 | **中**（东湖常设监测断面；公开入口待确认） | https://m.hbtv.com.cn/p/4436372.html ；湖北省生态环境厅 https://sthjt.hubei.gov.cn/ | 部分公开；**东湖具体断面/逐期数据待核实** |
| 12 | 东湖水下地形/等深图（公开论文） | 东湖水下地形测量、热红外遥感反演水深 | **高**（可直接用于湖底高程/等深建模） | https://wap.cnki.net/touch/web/Journal/Article/DKCH200401006.html ；https://wap.cnki.net/touch/web/Journal/Article/HZSZ201905016.html ；https://openir.whu.edu.cn/AchievementDetail/degree_fe6ba783-fe3a-432a-bd50-3f9f48f462ef | 需知网/万方/机构库权限 |

---

## 3. URL 可达性测试（Invoke-WebRequest -Method Head）

> 测试环境：Windows PowerShell + Invoke-WebRequest，User-Agent=Mozilla/5.0。

| URL | 方法/结果 | HTTP 状态码 | 备注 |
|---|---|---|---|
| https://geodata.cn （裸域名） | 连接失败 | 无（基础连接被关闭/发送时错误） | 裸域名存在连接/TLS 问题；**改用 https://www.geodata.cn** |
| https://www.geodata.cn | GET | **200** | 主站可访问（JS 渲染）；数据需注册/登录 |
| https://data.niglas.ac.cn | HEAD | **200** | 可访问；页面为 JS 轻量页（len≈1512），数据需登录 |
| https://wp.geog.mcgill.ca/hydrolakes/ | HEAD/GET | **无（超时 timeout）** | 本环境多次访问均超时（>25s / >45s），**暂判不可达/受限**；建议本地或浏览器直接访问 |
| https://springernature.figshare.com/collections/_/5243309 （GLOBathy） | HEAD | **202** | 服务器已响应（Accepted）；GET 在本环境超时，资源存在但访问较慢 |
| https://www.hydrosheds.org/products/hydrolakes | HEAD | **200** | 可访问，公开下载 |

---

## 4. 关键结论与建模建议

1. **湖盆参数（可直接入模）**：面积 31.75–33.7 km²；平均水深 2.11–2.46 m；最大水深近 6 m；湖底高程 15.12 m；岸线 115.5 km、岸线系数 K≈5.03（岸线高度曲折，二维网格需加密）；最大容积 1.24 亿 m³。——已核实（百度百科/湖北省湖泊志、维基百科）。
2. **水位（边界条件）**：实测最高 20.06 m（黄海基面）、正常高水位 19.78 m、年较差 0.6–0.8 m、月变幅 20–30 cm。**未找到可直接下载的官方多年逐时/逐日水位长序列**，需通过武汉市公共数据开放平台接口/长江水文数据集申请（含东湖水文站 61601200）。
3. **水系连通（流量边界）**：东湖经沙湖港、青山港连沙湖/杨春湖/戴家湖；青山港武丰闸使东湖成为人工控制水体；大东湖水网引江济湖＋武丰闸泵站提供引排动力；沿湖 8 水厂（35 万 m³/天）＋13 农用泵站。二维模型入/出流边界应结合闸站与管网调度，**具体调度运行规则待核实**。
4. **风场（驱动项）**：武汉主导北风，年均风速 1.8（含静风）–2.3（扣静风）m/s，静风概率 21.8%；东湖湖/水陆风环流显著（见文献），建议叠加**湖陆风日变化**风场。
5. **数据最优组合**：底层湖盆用《武汉湖泊志》/公开论文等深图或 GLOBathy（参考）；水质/营养边界用 geodata.cn 中国湖泊营养状态数据集（1984–2023）＋水生所东湖站长期监测；全球湖库属性用 HydroLAKES 交叉验证。

## 5. 引用来源（含经检索确认、但未直接抓取正文者）

- 百度百科「东湖」（转引湖北省地方志编纂委员会）：https://wapbaike.baidu.com/item/%E4%B8%9C%E6%B9%96/6055
- 维基百科「東湖 (武漢)」：https://zh.wikipedia.org/zh-cn/%E4%B8%9C%E6%B9%96_(%E6%AD%A6%E6%B1%89)
- 湖北省湖泊志系列《东湖》（QQ 阅读）：https://book.qq.com/book-read/23312733/7
- 东湖风景区各子湖水质（2019-01）：https://www.whdonghu.gov.cn/zwgk_6255/xxgkml/gysyjs/hjxx/201902/t20190201_144748.shtml
- 武汉市大东湖水网连通治理工程浅析：https://cms.hubwd.com/kjrc/kjcx/2993902.shtml ；人民长江版 https://wap.cnki.net/touch/web/Journal/Article/RIVE201011024.html
- 大东湖水网引水线路：http://news.cjn.cn/tbbd/200910/t1011970.html ；http://www.whcjwzb.com/ssxw/201010/t20101009_32526.htm
- 武丰闸泵站：http://www.whshmgs.cn/news_detail/54.html ；http://www.whshmgs.cn/service_info/71.html
- 东湖水文站（长江水文数据集）：https://www.moonapi.com/YangtzeRiver/detail/index/id/1354.html
- 武汉市公共数据开放平台（东湖水位接口）：https://data.wuhan.gov.cn/page/data/data_interface_details.html?cataId=37a7e913e2fb4767aec803e2bd0fa4a9&serviceCode=opens0000001230
- 武汉 20 个湖泊新建水文监测站：http://news.cjn.cn/sywh/201401/t2419062.htm
- 东湖深浅监测历史报道：https://news.sina.com.cn/c/2003-05-10/13101043484.shtml
- 武汉市基本气象资料（风）：http://eia-data.com/%e6%ad%a6%e6%b1%89%e5%b8%82%e5%9f%ba%e6%9c%ac%e6%b0%94%e8%b1%a1%e8%b5%84%e6%96%99/
- 武汉城市区域水陆风环流研究：https://d.wanfangdata.com.cn/periodical/njxxgcdxxb201805002 ；https://aipub.cn/1AA1DaL
- geodata.cn 中国湖泊营养状态时空观测数据集（1984–2023）：http://www.geodata.cn/data/datadetails.html?dataguid=197408932112662&docId=51 ；https://lake.geodata.cn/data/datadetails.html?dataguid=197408932112662&docid=32
- 南京地理与湖泊研究所科学数据中心（太湖产品库）：https://data.niglas.ac.cn ；https://cms.casdc.cn/article/450
- 湖北东湖湖泊生态系统国家野外科学观测研究站（CERN）：https://dhl.cern.ac.cn/ ；https://ihb.cas.cn/jgsz_1/kybm/ywtz/hbdhxtxt/
- 全球湖泊 TSI 数据集：https://escience.org.cn/metadata/detail?cstrId=CSTR%3A17099.11.G122705413858085.20250929.v1
- 武汉湖泊志：https://baike.baidu.com/item/%E6%AD%A6%E6%B1%89%E6%B9%96%E6%B3%8A%E5%BF%97
- 武汉市地方志数字方志馆：https://szfzg.wuhan.gov.cn/book/dfz/bookall/id/1024/category_id/384632.html ；https://whfzg.org.cn/book/dfz/bookall/id/971/category_id/346411.html
- 东湖水下地形论文：https://wap.cnki.net/touch/web/Journal/Article/DKCH200401006.html ；https://wap.cnki.net/touch/web/Journal/Article/HZSZ201905016.html ；https://openir.whu.edu.cn/AchievementDetail/degree_fe6ba783-fe3a-432a-bd50-3f9f48f462ef
- 湖北省环境质量：https://m.hbtv.com.cn/p/4436372.html

> 说明：cms.hubwd.com 与 baike.baidu.com/item/武汉湖泊志 在本环境分别因 SSL 证书不可信与 403 未能抓取正文，其内容为检索结果标题/摘要级别确认，相关细节已列为“待核实”。