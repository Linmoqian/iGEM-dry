# 重构模型的数据规格

## 预测目标

- 主目标：`log1p(total_microcystins_ug_l)` 连续回归；风险等级应在预测后依据明确采用的法规阈值派生，阈值版本需要进入配置和模型卡。
- 子目标：`log1p(MC_LR_ug_l)`，只使用明确标注为 MC-LR 的水体浓度。
- 辅助目标：毒素检出概率。它可帮助处理大量非检出，但不能替代浓度回归。

## 建议特征组

- `core_environment`：水温、DO、pH、浊度、电导率、TN、TP、氨氮、硝酸盐/亚硝酸盐、DOC、TSS、Secchi、水深和季节项。
- `bloom_proxy`：叶绿素 a、藻蓝蛋白、蓝藻密度、遥感 CyAN。单独实验并报告相对 core-only 的增益。
- `static_context`：经纬度、湖泊面积/深度、流域土地利用、地形和营养收支。只在可靠空间键连接时使用。
- `dynamic_external`：GLAST 同日及前 3/7/14/30 天湖表温度；允许在实测水温缺失时作为替代，但必须保留 `water_temp_source`。
- `forbidden_as_predictor`：同一样本的毒素变体总和、由目标直接派生的风险级别、实验室检出标志、MDL/RL、同样本毒素 qPCR/生物传感器输出（除非任务明确是传感器标定）。

## 训练前必做

1. 按 `target_kind` 选择单一任务。
2. 按 `dataset_id` 检查单位、方法和极端值；处理 `target_quality_flag`。
3. 对删失值比较半检出限、二部模型和删失回归三种方案。
4. 先做 core-only 基线，再添加 bloom proxies，禁止自动把所有列喂入模型。
5. 使用站点/湖泊分组切分、时间外推切分和来源外验证；报告 MAE、RMSE、R²、Spearman、风险阈值召回率与校准。
6. 中国/东湖无标签数据只用于协变量分布对齐；最终 MC-LR 传感器模型仍需工程菌 GFP/RFP 与标准 MC-LR 的湿实验标定数据。

## 推荐训练入口与分层

- `*_enriched_dynamic_ready.csv`：主模型入口；`training_tier` 为 `field_monitoring`、`hybrid_dynamic` 或 `remote_dynamic`。
- `*_enriched_static_baseline_ready.csv`：静态基线入口；允许 `static_context_only`，用于测量“只靠地点/气候背景能预测多少”，不得与动态模型混报。
- `broad_microcystins_nodularins_auxiliary.csv`：宽谱免疫辅助任务；其分析物边界不同于严格 total MC。
- `taihu_*_multimodal_covariates.csv`：中国域自监督预训练、协变量分布估计或 representation learning；没有毒素标签。

任何训练脚本必须显式列出特征白名单。禁止把 `record_id`、`source_row`、`target_raw`、删失/检出字段、同样本毒素组分、`target_quality_flag` 或任何由标签派生的列交给模型。
