# MCLR 检测体系综合分析报告：pmcy、pmlrA 与 tiggerRNA trigger0\-7

推荐使用电脑浏览本文档，全文共3个部分：

1\.摘要 2\.结论 3\.图与结果

## **摘要**



本报告整合四组 MCLR 响应实验：**pmcy\-GFP**、**pmlrA\-GFP**、**tig0123 tiggerRNA 适配体体系**和 **tig4567 tiggerRNA 适配体体系**。其中 pmcy 与 tig4567 有 0h 基线，采用 0h 校正后的响应量作为主指标；pmlrA 与 tig0123 本批没有 0h，采用原始有效信号作为主指标。



综合判断如下：

|体系|核心统计结果|当前判断|
|---|---|---|
|pmcy\-GFP|MCLR 浓度 `p = 1.43e-7 (***)`；时间 `p < 1e-12 (***)`；浓度×时间 `p = 8.61e-4 (***)`|有响应，但处理组后期多低于 0 μg/L 对照，不适合作为当前版本定量检测器|
|pmlrA\-GFP|MCLR 浓度 `p = 7.01e-11 (***)`；时间 `p < 1e-12 (***)`；浓度×时间 `p = 0.9992 (ns)`|有显著浓度和时间效应，但缺少 0h，且交互不显著；需补 0h 与 OD 归一化后复核|
|tig0123|MCLR 浓度 `p = 0.5392 (ns)`；trigger 类型 `p < 1e-12 (***)`；浓度×trigger `p = 0.5876 (ns)`|目前只有 0\.5h，主要体现 trigger 间基础信号差异，未见 MCLR 浓度响应|
|tig4567|trigger6 浓度效应 `p = 6.78e-8 (***)`；trigger5 浓度效应 `p = 0.0102 (*)`|trigger6 最强，trigger5 次之；是目前最值得推进的 tiggerRNA 候选|

总体优先级建议：

```Plain Text
trigger6 > trigger5 > pmlrA-GFP > pmcy-GFP > trigger4 ≈ trigger7 > trigger0/1/2/3 当前数据
```

更具体地说，**trigger6** 是信号幅度和统计证据最强的候选，但需要排查异常孔位和重复一致性；**trigger5** 响应较温和，可作为第二候选；**pmlrA\-GFP** 比 pmcy\-GFP 更有进一步比较价值，但目前缺少 0h 和 OD 归一化；**pmcy\-GFP** 有响应但方向不理想；**tig0123 当前只有 0\.5h 数据，不能用于判断动态检测性能**。



显著性规则：

```Plain Text
ns: p >= 0.05
*:  p < 0.05
**: p < 0.01
***: p < 0.001
```



## **实验结论**

### **1\. pmcy**



pmcy\-GFP 的双因素 ANOVA 显示，MCLR 浓度、时间和二者交互均显著：



- MCLR 浓度效应：`p = 1.43e-7 (***)`

- 时间效应：`p < 1e-12 (***)`

- MCLR 浓度×时间交互：`p = 8.61e-4 (***)`

但是，pmcy\-GFP 的响应方向不符合一个理想诱导型传感器。5h、6h、12h 时多个 MCLR 处理组的 0h 校正响应低于 0 μg/L 对照。换句话说，当前数据支持 “MCLR 改变 pmcy\-GFP 动态”，但不支持 “MCLR 随浓度升高诱导 GFP 增强”。



### **2\. pmlrA**



pmlrA\-GFP 本批没有 0h 基线，只能分析原始有效信号。双因素 ANOVA 显示：



- MCLR 浓度效应：`p = 7.01e-11 (***)`

- 时间效应：`p < 1e-12 (***)`

- MCLR 浓度×时间交互：`p = 0.9992 (ns)`

这说明 pmlrA 的读数随浓度和时间变化，但浓度效应没有明显随时间改变。单时间点 one\-way ANOVA 中，0\.5h `p = 0.0959 (ns)`，1h `p = 0.0673 (ns)`，1\.5h `p = 0.0493 (*)`，2h `p = 0.0354 (*)`，2\.5h `p = 0.0159 (*)`。修正 pmlrA 表格后，1\.5h、2h 和 2\.5h 均达到显著，但由于没有 0h 和 OD 归一化，仍应视为需要下一轮验证的启动子响应证据。



### **3\. trigger0/1/2/3**



tig0123 当前文件夹中只有 0\.5h 图像，因此只能做横向比较，不能判断时间动态。0\.5h 双因素 ANOVA 显示：



- MCLR 浓度效应：`p = 0.5392 (ns)`

- trigger 类型效应：`p < 1e-12 (***)`

- MCLR 浓度×trigger 交互：`p = 0.5876 (ns)`

trigger 类型差异极显著，说明 trigger0\-3 的基础信号水平不同；但当前没有证据表明 0\.5h 时这些 trigger 对 MCLR 浓度有显著响应。



### **4\. trigger4/5/6/7**



tig4567 是目前 tiggerRNA 系列中信息最完整的一组，具有 0h 基线和多个时间点。以 0h 校正后的 Δsignal 分析：



|trigger|MCLR 浓度|时间|MCLR×时间|判断|
|---|---|---|---|---|
|trigger4|`p = 0.0891 (ns)`|`p < 1e-12 (***)`|`p = 0.4269 (ns)`|主要随时间变化，MCLR 特异性弱|
|trigger5|`p = 0.0102 (*)`|`p < 1e-12 (***)`|`p = 1.22e-9 (***)`|有浓度响应，适合作为第二候选|
|trigger6|`p = 6.78e-8 (***)`|`p < 1e-12 (***)`|`p = 3.81e-4 (***)`|信号最强，当前首选候选|
|trigger7|`p = 0.6593 (ns)`|`p = 5.57e-6 (***)`|`p = 8.99e-6 (***)`|浓度主效应不显著，波动较大|



trigger6 的响应最强，但存在异常点和 0 μg/L 对照波动；trigger5 的响应较温和，可能更容易优化成稳定检测模块。



## **图与结果解读**



### **图 1\. pmcy\-GFP 的 0h 校正响应**

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZWZjYTkzYmU1NzgyYWJiYWI4MmY0NTEwOTM5NWQwMjFfYjAwZDU1OWE1M2UyYTYwMzY4NTQ1MTAxOTAzZTQ4NjBfSUQ6NzY0OTYwMjg1MDIyMjE4MTMxMl8xNzg3MzMzNTE4OjE3ODc0MTk5MThfVjM)

图中显示 pmcy\-GFP 的 ΔGFP 时间响应、12h 终点剂量响应和相对 0 μg/L 对照的显著性。pmcy\-GFP 在后期确实出现组间差异，但 0 μg/L 对照的 ΔGFP 最高，多个 MCLR 处理组低于对照。因此该体系有响应，但不是理想的浓度递增型检测器。



### **图 2\. pmcy\-GFP 热图**

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MTkxYzM5YWY3YjBkNGI4NGUzOGM2ODJhZTVhNjNkNDBfNDlhMzc2ZjFiYTNlMzI2N2Q2YjMyYmI2Yjk4NmRhMWRfSUQ6NzY0OTYwMjgyMTkyNjg2NTg5NF8xNzg3MzMzNTE4OjE3ODc0MTk5MThfVjM)

热图显示，原始 GFP 在 0h 就存在组间差异，因此使用 0h 校正后的 ΔGFP 是必要的。即使校正后，pmcy\-GFP 的剂量梯度仍不够单调。



### **图 3\. pmcy\-GFP 统计摘要**

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MjExNjgzNDIzOWNkN2E5YmE1NzdiNGU3ODk0NmJiYzBfMWEzY2NhY2U3MGJjNGEyMDhjY2JkZjRlZjZkM2Y3NTVfSUQ6NzY0OTYwMjc5NTM5NzY2Mzk0NF8xNzg3MzMzNTE4OjE3ODc0MTk5MThfVjM)

统计摘要显示，pmcy\-GFP 的浓度、时间和交互项均显著，但单时间点显著性主要出现在 4h 之后。该结果说明 pmcy 受处理影响，但不等于具备稳定定量检测能力。



### **图 4\. pmlrA\-GFP 时间响应与 2\.5h 终点响应**

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NDRmYzI5OWUyMzZkZmY5M2JhZDVmNmU2MjVmY2ZkNTRfZTRkNDM4ZGM1NDIwZWVmMmEzYzZkZjUyN2RkYjAyZmRfSUQ6NzY0OTYwMjc2Nzc3MzkxMjAwOV8xNzg3MzMzNTE4OjE3ODc0MTk5MThfVjM)

图 4a 显示 pmlrA 原始信号在 0\.5h 到 2\.5h 的变化。多数浓度组随时间上升。图 4b 显示 2\.5h 终点剂量响应；修正后单时间点 ANOVA 中，1\.5h `p = 0.0493 (*)`、2h `p = 0.0354 (*)`、2\.5h `p = 0.0159 (*)` 均达到显著。但由于没有 0h 和 OD 归一化，不能直接判断为稳定 MCLR 定量响应。



### **图 5\. pmlrA 热图与 tig0123 0\.5h trigger 比较**

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ODQ5Zjg0NzNjYTQ2MTU4ZmZiNzU3NmFiZjk1N2FjODlfYzkyNGYyNjcwOGJlY2IwMDc4MzU2OWY4MzI2N2JkNjlfSUQ6NzY0OTYwMjczNzk0NDYxMjA4MV8xNzg3MzMzNTE4OjE3ODc0MTk5MThfVjM)

图 5a 显示 pmlrA 在不同浓度和时间点的平均信号，整体随时间增强。图 5b 显示 tig0123 在 0\.5h 的 trigger0\-3 比较：trigger1 基础信号最高，trigger0 最低，但随 MCLR 浓度变化不明显。



### **图 6\. pmlrA 与 tig0123 统计摘要**

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NzQwMTY0ZGNjYTAxNjY3OTgzMWFmZjgxYTBhYjliODhfM2FmZmE2ZjI3ZjYwZTNhMjYyN2MxNGMwOWJiOWNjOWJfSUQ6NzY0OTYwMjcwOTc4ODY3NTI1MV8xNzg3MzMzNTE4OjE3ODc0MTk5MThfVjM)

图 6a 显示 pmlrA 各时间点 one\-way ANOVA：0\.5h `p = 0.0959 (ns)`，1h `p = 0.0673 (ns)`，1\.5h `p = 0.0493 (*)`，2h `p = 0.0354 (*)`，2\.5h `p = 0.0159 (*)`。图 6b 显示 tig0123 各 trigger 在 0\.5h 下不同浓度之间的 one\-way ANOVA，trigger0 `p = 0.8481 (ns)`，trigger1 `p = 0.0896 (ns)`，trigger2 `p = 0.1568 (ns)`，trigger3 `p = 0.6951 (ns)`，均未达到显著。



### **图 7\. tig4567 时间响应曲线**

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZTY4ODYxYjMyZDZlODE0MzFiYzcwMTNiZDFhZjhmNzVfNTY2MjUyMTFmMDNiOWJhNzQwNDBkZGQ4M2QzYTY3NjZfSUQ6NzY0OTYwMjY4MDY1NDAyMzYyOF8xNzg3MzMzNTE4OjE3ODc0MTk5MThfVjM)

图 7 展示 trigger4\-7 的 0h 校正 Δsignal 时间曲线。横轴按真实时间比例显示。trigger6 的信号幅度最大，trigger5 次之；trigger4 主要随时间变化，trigger7 波动较大。该图支持 trigger6/5 是当前 tiggerRNA 系列中最值得继续推进的候选。



### **图 8\. tig4567 Δsignal 热图**

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MjBkZmIwMzdjZDgzZjc1MjAxZGJkOGE4ZTc5OGExYzJfMGExY2Q3YTY3ZDY5MmI2ZDk3ZGE3YmQ5NjBhYmM4NTFfSUQ6NzY0OTYwMjYzMzQyNjQwNjYwNF8xNzg3MzMzNTE4OjE3ODc0MTk5MThfVjM)

热图显示 trigger6 的整体响应最强，但也显示部分异常区域，尤其与 0 μg/L 对照和 A 行波动有关。强响应不等于稳定定量检测，后续需要复核异常点并做归一化。



### **图 9\. tig4567 24h 终点剂量响应**

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MzhlMDFhYmFlNGZmNTMyZDEzODM1NmQxMmM5MDhkZjBfNmNiNjQxMDExNzAzYTdkNjNkNzhhY2E0MDRjYzFkMDhfSUQ6NzY0OTYwMjU5Mzk1MzY2NDIxMl8xNzg3MzMzNTE4OjE3ODc0MTk5MThfVjM)

24h 终点图显示 trigger6 仍保持较高信号，但剂量关系并非完全单调；trigger5 在 24h 可能不是最佳检测窗口。后续应重点比较 4h、6h、12h 等窗口，而不是只看 24h。



### **图 10\. tig4567 统计显著性摘要**

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NzZmM2U1MTIyOTYxZjkzZTA1YTliMTkyNDZiOTg0ODRfMzRjZWMwOWRhNGM0OWZlY2UxNzdiM2I3MzY4M2VhYzhfSUQ6NzY0OTYwMjU2NjU3MjQ2MTI1MF8xNzg3MzMzNTE4OjE3ODc0MTk5MThfVjM)

统计摘要显示 trigger6 的 MCLR 浓度效应最强，trigger5 也显著；trigger4 和 trigger7 的浓度主效应不显著。综合统计和曲线形态，trigger6 是首选，trigger5 是第二候选。



## **总结**



目前最有开发潜力的是 **tiggerRNA trigger6**，其次是 **trigger5**。**pmlrA\-GFP** 有进一步验证价值，但数据还不完整。**pmcy\-GFP** 可作为响应参考，但不适合作为当前定量检测方案。**tig0123 trigger0\-3** 目前只有 0\.5h，尚不能判断其真实检测潜力。



---

原始数据：

\[pmcy酶标仪数据提取\.xlsx\]

\[pmcy\_GFP\_MCLR\_statistical\_analysis\.xlsx\]

\[pmlra\_tig123\_extracted\_FOR\_REVIEW\.xlsx\]

\[pmlra\_tig123\_statistical\_analysis\.xlsx\]

\[tig4567\_extracted\_data\.xlsx\]

\[tig4567\_statistical\_analysis\.xlsx\]

参考：

\[pmcy\_GFP\_MCLR\_分析报告\.md\]

\[pmlra\_tig123\_integrated\_analysis\_report\.md\]

\[tig4567\_分析报告\.md\]



