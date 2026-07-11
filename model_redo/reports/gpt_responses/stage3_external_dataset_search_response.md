# GPT 审查回复：阶段 3 外部数据源检索

> 日期：2026-06-04
> 对话 URL：https://chatgpt.com/c/6a20ae60-8b24-83a7-b63c-077e09532321
> 模型思考时间：3 分 57 秒

---

## 1. 总体判断

GPT 不建议继续定义为"稳健的 MC-LR 浓度回归预测"。建议拆成两层：

- **任务 A**：总 microcystins 回归/风险分类（公开数据充足）
- **任务 B**：MC-LR 专属小样本验证/案例分析（数据不足，仅适合探索）
- **任务 C**：中国/东湖场景迁移（用环境变量做 covariate shift 分析，不用于 toxin 标签训练）

**核心意见**：不要把总微囊藻毒素模型包装成 MC-LR 模型；先构建"总 MC 风险模型"，再用 EMLS MC-LR 做受限验证。

## 2. 推荐数据集（12 个）

### 高优先级

| # | 数据集 | MC-LR? | 样本量 | 来源 |
|---|--------|--------|--------|------|
| 1 | EPA NLA 2007/2012/2017/2022 | 总 MC | 3,027+ | EPA NARS |
| 2 | NOAA NCEI 0276941 Lake Erie | 总 MC | >500 | NOAA NCEI |
| 3 | GLERL-CIGLR Western Lake Erie HAB | 总 MC | >500 | NOAA GLERL |
| 4 | EPA Water Quality Portal | 可能含 MC-LR | 未确认 | EPA/USGS |

### 中优先级

| # | 数据集 | MC-LR? | 样本量 | 来源 |
|---|--------|--------|--------|------|
| 5 | Figshare Global Microcystin (Buley et al.) | 总 MC | >500 | Figshare |
| 6 | data.gov 20 Reservoirs 1987-2018 | 不确定 | 未知 | EPA ORD |
| 7 | USGS Tennessee Reservoirs 2022-2024 | 总 MC | <500 | USGS |
| 11 | Cheney Reservoir 14-year | 总 MC | 可能>500 | USGS/Figshare |

### 低优先级

| # | 数据集 | MC-LR? | 样本量 | 来源 |
|---|--------|--------|--------|------|
| 8 | USGS Large Rivers 2017-2019 | 总 MC | <500 | USGS |
| 9 | USGS North Atlantic 2020 | 总 MC | <500 | USGS |
| 10 | USGS SE Wadeable Streams 2014 | 总 MC | <500 | USGS |

### 中国数据（辅助特征，无 MC 标签）

| # | 数据集 | MC-LR? | 用途 |
|---|--------|--------|------|
| 12 | CNEMC / NESDC 东湖站 / Figshare 中国湖库 | 无 | 辅助特征/covariate shift |

## 3. GPT 自认可能错的地方

1. 样本量判断基于推断，未逐行计数
2. 某些 LC/MS/MS 数据可能隐藏 MC-LR 列，标"非明确 MC-LR"可能偏保守
3. WQP 字段命名不统一，按单一 characteristicName 搜索会漏数据
4. 中国 MC-LR 数据可能在论文附录中但无机器可读格式
5. Figshare/Zenodo 对自动访问有限制

## 4. GPT 建议的下一步

1. **任务拆分**：A（总 MC）+ B（MC-LR 小样本）+ C（中国场景迁移）
2. **优先下载**：EPA NLA → NOAA NCEI → GLERL-CIGLR → WQP → USGS → 中国环境数据
3. **严禁随机切分**：GroupKFold by waterbody/site、leave-one-lake-out、leave-one-year-out
4. **检测限单独建模**：Tobit、左删失回归、sensitivity analysis（0、LOD/2、LOD）
5. **报告措辞**："公开数据不足以支持稳健 MC-LR 专属回归。当前路径是先建立总 MC 风险模型，再用 EMLS MC-LR 做受限验证。"
