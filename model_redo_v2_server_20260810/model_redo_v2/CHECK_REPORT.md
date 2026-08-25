# 建模工程三轮检查报告

检查日期：2026-08-10。所有检查均在复制后的真实 `model_redo_v2/data` 上执行；冒烟训练使用缩减迭代数，只验证流程和制品，不代表正式精度。

## 结论

工程已通过语法/单元、真实端到端、独立数据与泄漏审计三轮检查，可以整体上传服务器进行正式训练。当前最重要的科学限制仍是东湖本地 MC-LR 标签不足；代码通过非 IID 测试与 OOD 标记显式暴露该限制，不会把外域性能冒充为东湖性能。

## 第一轮：静态、数据契约与单元检查

- `python -m compileall`：通过；
- Ruff lint：`All checks passed`；
- Ruff format：33 个目标文件全部符合格式；
- Pytest：`12 passed`；
- 覆盖标签区间、泄漏特征拒绝、确定性切分、stacking、CQR、指标、真实数据契约、删失 Gaussian NLL、OOD 检测器保存/回载；
- JSON/TOML 配置可解析，非法目标、折号、校准参数和 OOD 分位数会在训练前失败。

## 第二轮：真实数据端到端与制品回载

完成以下真实表全流程：数据载入 → 非 IID 切分 → OOF 基模型 → 非负 stacking → 最终基模型 → CQR → OOD → 指标与 Parquet 制品。

| 运行 | 数据规模 | 结果 |
|---|---:|---|
| total MC / XGBoost AFT | 20,852 | 通过 |
| total MC / CatBoost quantile | 20,852 | 通过 |
| total MC / LightGBM quantile | 20,852 | 通过 |
| total MC / CatBoost hurdle | 20,852 | 通过 |
| total MC / TabM censored | 20,852 | 通过 |
| total MC / XGB + CatBoost + TabM ensemble | 20,852 | 通过 |
| MC-LR static / source OOD / XGBoost AFT | 6,409 | 通过 |
| MC-LR core / waterbody OOD / XGBoost AFT | 2,837 | 通过 |

完整集成运行保存后重新加载，对 4,298 个测试记录复算：q10 最大差为 0，median 最大差约 `2.35e-7 µg/L`，q90 最大差约 `1.17e-6 µg/L`，OOD 标记完全一致。差异属于序列化/浮点精度范围。

## 第三轮：数据完整性、泄漏与复现性

- 数据复制：源和目标均为 98 个文件、375,009,091 字节；逐文件 SHA-256 无缺失、无不一致；
- total MC 来源 OOD：训练 12,394、验证 4,160、测试 4,298，来源组跨角色交集为 0；
- MC-LR static 来源 OOD：训练 2,506、验证 352、测试 3,551，来源组跨角色交集为 0；
- MC-LR core 水体 OOD：训练 1,702、验证 567、测试 568，水体组跨角色交集为 0；
- 同配置独立生成两次 total MC 切分，CSV 字节级一致，SHA-256 均为 `9cdf105dea50a2f1d0cb754fc0cd8885e26a9a765c56c19273c447d013667f69`；
- 所有切分中的 `record_id` 唯一，训练/验证/测试不重复；
- 模型、stacker、calibrator 和 OOD detector 均验证可回载推理。
- 第一次 XGBoost 端到端检查捕获 pandas 只读权重数组问题；修复为显式可写副本后，其后 10 个冒烟运行全部完成。初始失败目录保留为诊断证据，不是待训练任务。

## 已知边界与服务器验收

- MC-LR core 当前全部是精确值，删失目标在该表上自然退化为普通回归；MC-LR static 含 3,417 条删失观测，可验证删失建模价值；
- 静态表的 WorldCover 5 km 特征当前全缺失，加载器会明确警告并删除这些列；不能把它们列为已使用特征；
- 冒烟集成的权重和指标没有科学解释价值，正式服务器训练后才根据重复非 IID 实验选择架构；
- TabICLv2 是可选的精确值/点预测挑战者，本机核对了 2.1.1 包的保存/加载 API，但未下载其模型权重；服务器仅在安装 `.[foundation]` 后单独运行，不能当作删失感知核心；
- Windows 检查机没有 Bash，三个服务器脚本未在本机执行 `bash -n`；脚本采用 `set -euo pipefail` 和标准 Conda 命令，上传 Linux 后首先运行 `bash -n scripts/*.sh`，再运行 `bash scripts/bootstrap_server.sh`。
