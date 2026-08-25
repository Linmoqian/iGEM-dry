# RTX 4090 服务器部署与正式训练报告

执行日期：2026-08-10。服务器项目目录：`/home/linux/igem-cmadre`。本文不记录密码、私钥或访问令牌。

## 部署状态

- Ubuntu 22.04，16 CPU 核，47 GiB 内存；
- NVIDIA GeForce RTX 4090，24,564 MiB，驱动 550.107.02；
- Conda 环境：`/home/linux/anaconda3/envs/igem-cmadre`；
- Python 3.11.15，PyTorch 2.5.1 + CUDA 12.1；
- 数据：98 个文件逐项对照 `data_snapshot_manifest.csv`，缺失 0、哈希不一致 0；
- 测试：13 passed；
- GPU 正式训练观测峰值：100% utilization、约 16,070 MiB 显存；
- 项目使用本地 Git `main` 分支管理，数据、论文 PDF 与运行制品保留在目录但不进入 Git 对象库。

服务器原有 `isaac-sim` Docker 容器占用 GPU。经用户明确授权后已执行 `docker stop isaac-sim`；容器未删除，状态为 stopped，可由用户需要时重新启动。

## 架构迭代

v1 使用水体级内部 OOF 和原始浓度尺度 NNLS stacking。正式结果显示三项任务的 stacking 均过度偏向 TabM。v2 在不读取测试标签的前提下作以下修改：

1. 外层为 source OOD 时，内部 OOF 同样整来源留出；
2. stacking 在 `log1p` 浓度尺度拟合；
3. stacking 样本权重按来源均衡，并继续下调删失区间代理值；
4. 水体 OOD 任务仍使用完整水体组内部 OOF。

## 锁定测试结果

下表为校准后 ensemble。v2 是当前候选；v1 制品完整保留用于审计。

| 任务 | 版本 | log1p MAE | Spearman | 来源宏平均 log1p MAE | 最差来源 | 区间距离 MAE (µg/L) | q10–q90 覆盖率 | OOD 比例 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| total MC / source OOD | v1 | 0.3746 | 0.3085 | 0.3249 | 0.4787 | 0.6463 | 0.8060 | 0.9930 |
| total MC / source OOD | v2 | **0.3488** | **0.3190** | **0.2931** | **0.4656** | **0.5988** | **0.8321** | 0.9930 |
| MC-LR static / source OOD | v1 | 0.1744 | -0.1487 | 0.1744 | 0.1744 | 0.5339 | 0.7537 | 1.0000 |
| MC-LR static / source OOD | v2 | **0.1318** | **0.0831** | **0.1318** | **0.1318** | **0.1633** | **1.0000** | 1.0000 |
| MC-LR core / waterbody OOD | v1 | 0.3385 | 0.4299 | 0.2675 | 0.3886 | 32.2092 | **0.8169** | 0.1620 |
| MC-LR core / waterbody OOD | v2 | **0.2972** | **0.5091** | **0.2403** | **0.3339** | **32.0704** | 0.7905 | 0.1620 |

v2 stacking 权重：

- total MC：XGBoost 0，CatBoost 0.8304，TabM 0.1696；
- MC-LR static：XGBoost 0，CatBoost 1.0，TabM 0；
- MC-LR core：XGBoost 0.6848，CatBoost 0.0846，TabM 0.2306。

## 制品与回载检查

三项 v2 运行均包含 config、数据摘要/哈希、split manifest、三个基模型、stacking、CQR、OOD detector、验证/测试预测和 metrics。重新加载全部制品并重新预测后：

- total MC：4,298 行，最大绝对差约 `2.99e-4 µg/L`；
- MC-LR static：3,551 行，最大绝对差 0；
- MC-LR core：568 行，最大绝对差约 `1.77e-4 µg/L`；
- 三项 OOD 标记均逐行完全一致。

GPU 浮点差异远小于数据测量与模型误差量级。

## 科学结论与限制

- v2 在三个锁定测试的 log1p MAE、来源宏平均与最差来源指标上均优于 v1，因此可作为当前候选架构；
- total MC 测试 99.3% OOD，MC-LR static 测试 100% OOD，表明跨数据源特征分布差异极大；
- MC-LR static 的 R² 仍为负，不能声称外部来源绝对浓度预测已经达到部署精度；
- MC-LR core 的 RMSE 被极端高值主导，稳健 log 指标改善但仍需更多高浓度 MC-LR 标签；
- 当前结果不能替代东湖本地、时间滞后且覆盖未检出/常规/高值范围的验证集。

当前候选运行目录：

- `runs/total_mc_source_ood_v2/`；
- `runs/mc_lr_static_source_ood_v2/`；
- `runs/mc_lr_core_waterbody_ood_v2/`。
