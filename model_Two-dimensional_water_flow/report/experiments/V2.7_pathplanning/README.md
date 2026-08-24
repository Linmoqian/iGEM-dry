# V2.7_pathplanning — 路径规划 V2.6/V2.7 轮实验输出归档（2026-08-25 统一整理）

> 自 `model_path_planning/code/out|outA|outB|outC|outC2/` 统一移入。对应报告：`model_path_planning/report/07_优化实验流程记录.md`（过程与数字）、`03`（架构报告，图片引用本目录）、`05`（质量审查，证物位置已同步）。

## 目录

| 子目录 | 内容 |
|---|---|
| `results/` | V2.6/V2.7 全部评测数据：eval_results / ood_results / replan_results / ablation_results / strong_wind_ablation / train_curve（V2.6）+ exp27_* 系列（A/B/C 训练对照、3 种子、flow 基线、汇总 exp_v27.json） |
| `figures/` | 报告插图 fig1–fig9（03/06 报告引用本目录） |
| `trainings/` | 四轮训练产物（ckpt.pt + ckpt_config.json + train_curve.json）：`A`（V2.7 独立时钟基线）、`B`（+边特征+解码先验，**V2.7 交付基线**）、`C`（v3.0 flow 首次，冻结平台记录）、`C2`（锚定+β截断修复）；`ckpt_v26_baseline.pt` = V2.6 旧权重（共享时钟时代） |
| `logs/` | 四份训练日志 |

## 关键模型定位

| 模型 | 路径 | 用途 |
|---|---|---|
| **B（交付基线）** | `trainings/B/ckpt.pt` | 东湖 10 任务最优策略（obj 16.31±0.014、makespan 20.04）；文档默认引用 |
| D（规模） | `…/V3_pathplanning/trainings/outD/ckpt.pt` | n=50 规模（M5 证据模型，+9.1%/+13.2%） |
| V2.6 旧权重 | `trainings/ckpt_v26_baseline.pt` | 历史对照（F3 共享时钟时代） |

## 复现提示

- 代码默认参数（evaluate/ablation/ood/replan 的 `--ckpt out/ckpt.pt`）与 plots 输入输出已随本整理同步：`plots.py` 现读本目录 `results/` 并写 `figures/`；
- 训练复现：`train.py --out <本目录>/trainings/<名>`（见 `model_path_planning/README.md` 快速复现段）；
- 运行评测类脚本若不显式传 `--ckpt`，会在 `code/out/` 重建运行期副产物——按"跑完即归档"约定处理。

## git 溯源

本目录与 `code/` 下删除构成同一提交（git 重命名识别）；pre-move 提交位于 `feature/pathplanning-v3` / `feature/swflow-optimization`（关键字：V2.7 优化轮 / M2 / M3 / M4 / M5 / M6 / M7）。
