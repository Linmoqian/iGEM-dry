# model_redo_v2：模型重构设计基线

本目录保存新一轮模型重构的目标、证据、架构迭代和实施路线。`model/` 与 `model_redo/` 只作为历史经验和当前数据来源；这里不继承旧模型的指标结论，也尚未宣称已经训练出最终模型。

## 当前结论

- 最终部署目标是武汉东湖场景下的 MC-LR 风险估计，但现有强标签主要是美国/加拿大的 total microcystins；二者必须分任务建模。
- 当前数据可以较好支撑 total MC 的跨来源建模研究，能够有限支撑 MC-LR 建模，但还不能证明东湖本地精度。
- 现有浓度标签含大量未检出/左删失值。最终模型必须使用检测区间，而不是把未检出简单改成 0、LOD/2，或在回归中删除。
- 当前数据大多是异构的横截面或同日观测，第一阶段应定义为**当前状态估计/风险映射**；只有获得严格滞后的连续气象、水文、遥感和历史毒素序列后，才升级为真正的未来预报。
- 推荐最终路线是“删失感知 + 分析物多任务 + 跨来源稳健 + 概率集成”，不是押注单一排行榜模型。

## 文档导航

1. [MODEL_OBJECTIVE_SPEC.md](MODEL_OBJECTIVE_SPEC.md)：模型目标说明书、任务边界、输入输出和验收标准。
2. [CURRENT_DATA_ASSESSMENT.md](CURRENT_DATA_ASSESSMENT.md)：当前数据画像、可用程度和决定架构的约束。
3. [LITERATURE_AND_MODEL_REVIEW.md](LITERATURE_AND_MODEL_REVIEW.md)：论文检索范围、候选架构、许可和适配判断。
4. [ARCHITECTURE_ITERATIONS.md](ARCHITECTURE_ITERATIONS.md)：八轮架构设计迭代和最终架构决策。
5. [MODELING_ROADMAP.md](MODELING_ROADMAP.md)：数据冻结、切分、训练、评估、消融和交付路线。
6. [references/PAPER_INDEX.md](references/PAPER_INDEX.md)：论文索引、下载结果和本地文件。

## 可复现证据

- `references/current_data_profile.json`：当前模型表的程序化画像。
- `references/literature_search_results.csv/json`：20 组检索式、240 条候选文献记录。
- `references/paper_download_manifest.csv/json`：精选论文下载状态、文件大小和 SHA-256。
- `references/papers/`：成功下载并验证为 PDF 的 16 篇论文。
- `tmp_code/profile_current_data.py`：只读数据画像脚本。
- `tmp_code/literature_search.py`：文献元数据检索与开放 PDF 下载脚本。

## 当前阶段

模型工程代码已经实现，当前仍不包含正式训练结果。主要入口：

```bash
python -m pip install -e ".[dev]"
python run_validate.py
pytest -q
python run_train.py --models xgb_aft --smoke --run-name smoke_xgb_aft
```

支持的模型包括 XGBoost AFT、CatBoost/LightGBM quantile、CatBoost Hurdle、删失感知 TabM MiniEnsemble，以及可选 TabICLv2 挑战者。流水线会生成来源/湖泊/时间非 IID 切分、折外 stacking、CQR 校准、来源宏平均与最差来源指标和完整运行制品。服务器使用见 [SERVER_TRAINING_GUIDE.md](SERVER_TRAINING_GUIDE.md)。

任何“最强”“最佳”结论仍必须由服务器上的跨来源、跨湖泊和时间外推实验决定。

## 已实现的训练与推理闭环

当前实现不是只有架构说明，而是可以直接上传服务器运行的完整工程：

- 区间标签保留未检出/低于检出限观测，XGBoost AFT 与 TabM 删失似然不会把它们硬改为 0；
- 支持来源、水体和时间非 IID 切分，内部 stacking 折只从训练集生成；
- 支持 XGBoost AFT、CatBoost/LightGBM 分位数、CatBoost hurdle、删失感知 TabM MiniEnsemble，以及可选 TabICLv2 挑战者；
- 输出非负 stacking、CQR 校准区间、来源宏平均/最差来源指标和训练域 OOD 标记；
- 每次运行保存配置、数据 SHA-256、切分清单、模型、校准器、预测表、依赖版本和状态；
- 完成的运行可重新加载并对 CSV/Parquet 批量推理，无需重新训练。

```bash
python run_train.py --config configs/server_gpu.json --run-name total_mc_source_ood
cmadre predict \
  --run-dir runs/total_mc_source_ood \
  --input path/to/new_samples.csv \
  --output runs/total_mc_source_ood/new_predictions.parquet
```

本地实现与三轮检查证据见 [CHECK_REPORT.md](CHECK_REPORT.md)。冒烟运行只验证工程正确性，不用于比较模型优劣；正式结论必须使用服务器完整轮次结果。
