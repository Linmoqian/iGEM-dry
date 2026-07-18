你保持怀疑态度。你不一定都是对的，我也不一定是对的，但我们都力求最优。

你现在是本项目的外部审查者，不是最终裁判。请重点寻找错误、遗漏、数据泄漏、指标不匹配、任务定义不清、实验不可复现、结论过度推断、数据源不适合建模等问题。

## 项目背景

项目：model_redo
目标：重建 MC-LR（微囊藻毒素-LR）浓度预测模型
主任务：MC-LR 浓度回归预测
辅助任务：基于阈值的风险分类
旧项目 model/：只读经验库，不直接继承结论

## 当前问题

我们审计了本地 `data/raw/` 中所有原始数据后发现：

1. **仅有一个数据集包含 MC-LR 专属浓度**：EMLS Europe（369 行欧洲湖泊，2015 年，MC_LR_ugL 字段，100% 填充，0–3.97 µg/L）
2. **其他数据集均为"总微囊藻毒素"**（非 MC-LR 亚型）：Lake Erie（3,074 行）、HABs Training（3,664 行）、SF Estuary（478 行）等
3. **369 行样本量不足以建立稳健的 MC-LR 浓度回归模型**
4. EMLS 零值含义不明确（未检出 vs 真实零值），缺少检测限文档
5. 欧洲湖泊与目标场景（中国湖泊/武汉东湖）地理差异大

## 当前阶段

阶段 3：向 GPT 请求全网搜索开放 MC-LR / microcystin 数据集

## 需要你做的事情

请全网搜索公开可用的、包含以下字段的数据集：

### 必须包含的字段类型
- MC-LR 浓度（microcystin-LR / MC-LR / mclr）或总微囊藻毒素（microcystin / cyanotoxin）
- 水质环境变量（水温、pH、溶解氧、浊度、叶绿素 a）
- 营养盐（总氮、总磷、硝酸盐、氨氮、正磷酸盐）
- 采样日期和位置

### 优先搜索关键词
- microcystin-LR
- microcystin concentration
- MC-LR
- cyanotoxin
- harmful algal bloom (HAB)
- cyanobacteria
- water quality
- chlorophyll a
- nutrients
- lake monitoring
- toxin concentration

### 必须搜索的数据源方向

1. **NOAA GLERL**：
   - https://www.glerl.noaa.gov/data/#biological
   - https://www.glerl.noaa.gov/res/HABs_and_Hypoxia/habsMon.html

2. **NOAA NCEI**：National Centers for Environmental Information

3. **EPA Water Quality Portal**：waterqualitydata.us

4. **USGS Water Data**

5. **data.gov**

6. **Great Lakes cyanobacteria / cyanotoxin datasets**

7. **Lake Erie HABs monitoring data**

8. **University repositories**

9. **Zenodo**

10. **Figshare**

11. **Dryad**

12. **Harvard Dataverse**

13. **Environmental Data Initiative (EDI)**

14. **GBIF**（如有生物相关数据）

15. **中国生态环境部/水利部**公开水质数据（如适用）

### 每个数据集请按以下格式输出

```
数据集名称：
来源机构：
链接：
下载链接：
数据格式：
时间范围：
空间范围：
是否包含 MC-LR 或 microcystin：
是否包含环境变量：
是否有单位说明：
是否有许可或引用说明：
适合用途：主训练 / 外部验证 / 辅助特征 / 仅参考
潜在问题：
优先级：高 / 中 / 低
```

### 重要提醒

1. 请给出**真实可访问的链接**，不要编造 URL
2. 请区分**数据下载链接**、**说明文档链接**、**论文链接**
3. 请优先推荐**包含 MC-LR 亚型数据**的数据集
4. 如果只有总 MC 数据，也请列出（但标注"非 MC-LR"）
5. 请指出你自己的判断可能错在哪里——尤其是链接失效、字段误判、数据不含 MC-LR、数据只适合藻华预测而非毒素浓度预测
6. 请评估每个数据集的样本量是否足够建立回归模型（建议 >500 行）

## 请按以下格式回复

### 1. 总体判断

找到多少个相关数据集？是否足以解决本地数据不足的问题？

### 2. 推荐数据集（按优先级排序）

使用上面的模板格式列出。

### 3. 你可能错在哪里

### 4. 下一步建议
