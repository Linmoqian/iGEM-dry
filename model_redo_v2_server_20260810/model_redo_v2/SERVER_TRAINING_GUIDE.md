# 服务器训练说明

## 1. 上传后目录要求

整个 `model_redo_v2/` 原样上传。至少应包含：

- `data/model_tables/`；
- `src/cmadre/`；
- `configs/`；
- `environment.yml`、`pyproject.toml`；
- `run_train.py`、`run_validate.py`、`tests/`。

不要只上传代码而漏掉 `data/`，也不要把旧 `model_redo/data/data_processed` 与本目录数据混合覆盖。

## 2. 环境创建

Linux + Conda：

```bash
cd model_redo_v2
bash scripts/bootstrap_server.sh
```

脚本会创建/更新 `igem-cmadre`，以 editable 方式安装项目，运行数据契约检查和测试。`environment.yml` 默认 CUDA 12.1；如果服务器驱动不兼容，应先根据 `nvidia-smi` 调整 `pytorch-cuda`，不要盲目安装。

仅使用 pip：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python run_validate.py
pytest -q
```

TabICLv2 是可选挑战者，确认 GPU 显存和下载权限后安装：

```bash
python -m pip install -e ".[foundation]"
```

它首次运行会下载 checkpoint。默认正式流水线不依赖 TabICLv2。

## 3. 训练前检查

```bash
cmadre inspect-env
python run_validate.py
cmadre make-splits --split-protocol source_ood --output runs/split_preview
pytest -q
```

检查 `split_summary.json`，确认训练、验证和测试来源符合预期。locked test 的 fold 选择一旦用于最终验收就不能重新调参。

## 4. 烟雾训练

烟雾模式使用完整数据和完整切分，但大幅降低模型迭代次数，只验证端到端代码：

```bash
python run_train.py \
  --models xgb_aft \
  --smoke \
  --run-name smoke_xgb_aft
```

它不产生可报告的模型性能。成功后应看到：

- `runs/smoke_xgb_aft/run_status.json` 为 `complete`；
- 模型文件、折外 stacking 权重、calibrator；
- validation/test Parquet 预测；
- `metrics.json`。

## 5. 正式训练顺序

建议依次运行：

```bash
# total MC 来源外主实验
bash scripts/train_total_mc.sh

# total MC 时间外实验
python run_train.py --config configs/total_mc_temporal.json --run-name total_mc_temporal

# MC-LR 含删失静态模型
bash scripts/train_mc_lr.sh

# MC-LR 动态检出条件模型；该表没有删失样本，不能与总体 MC-LR 混报
python run_train.py --config configs/mc_lr_core.json --run-name mc_lr_core_detected_only
```

正式结果必须比较来源外、湖泊外和时间外协议。建议复制配置并改变 `test_fold` 进行重复外层折，但每个 fold 的结果目录必须独立，不能覆盖。

## 6. 后台运行

推荐 `tmux`：

```bash
tmux new -s cmadre
bash scripts/train_total_mc.sh 2>&1 | tee train_total_mc.log
```

不要把服务器 token、SSH 私钥或数据访问密钥写入配置、日志或仓库。

## 7. GPU 和复现注意事项

- TabM 默认自动使用 CUDA；OOM 时先减小 `batch_size` 和 `ensemble_size`。
- `server_gpu.json` 让 XGBoost 使用 CUDA，CatBoost 默认仍使用 CPU，以降低 GPU 非确定性差异。
- 所有运行保存 Python/依赖版本、主机、Git commit、配置和数据 SHA-256。
- 不同 CUDA/库版本可能有细微数值差异；最终模型应在固定镜像或 Conda lock 中复跑。
- 风险阈值默认留空。只有确认用途和阈值版本后才通过 `--risk-thresholds` 显式传入。

## 8. 训练完成后的回传文件

至少回传完整 `runs/<run_name>/`：

- `run_status.json`；
- `config.json`、`data_summary.json`、`split_manifest.csv`；
- `models/`、`stacking_weights.json`、`calibrator.json`、`ood_detector.pkl`；
- `validation_predictions.parquet`、`test_predictions.parquet`；
- `metrics.json` 和控制台日志。

不要只回传一个最优指标或单个模型权重，否则无法审计和复现。

## 9. 训练后批量推理

输入 CSV/Parquet 必须含该运行 `data_summary.json` 中列出的全部特征；允许含额外元数据列。输出保留原列，并添加各基模型、集成和校准后的 q10/median/q90，以及 `ood_score`、`ood_flag`。

```bash
conda run -n igem-cmadre cmadre predict \
  --run-dir runs/total_mc_source_ood \
  --input /path/to/new_samples.csv \
  --output runs/total_mc_source_ood/new_predictions.parquet
```

若东湖样本被标记为 OOD，这不是程序错误，而是说明它超出训练特征分布。此时应报告 OOD 比例并优先补充东湖实测标签，不应把域外结果描述为已验证的本地精度。
