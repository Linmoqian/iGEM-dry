# V3_pathplanning — 路径规划 V3 轮实验归档（2026-08-24/25）

> 归档自 `model_path_planning/code/`（2026-08-25 统一移动）。对应报告：`model_path_planning/report/09_模块级优化验证报告.md`（逐模块判定）、`07_优化实验流程记录.md` 第三轮（过程与数字）、`03`（§5.6 规模外推 / §5.5 管线级修正）。
> 全部实验在 CPU 上串行完成（每轮训练 ~20-25 min）；机器：Windows 11 / Python 3.12 / torch 2.13.0+cpu / ortools 9.15。

## 目录

| 子目录 | 内容 |
|---|---|
| `scripts/` | 3 个实验驱动脚本（exp_v3_eval_env / exp_v3_m4_validation / exp_v3_m5_scale） |
| `results/` | 全部实验结果 JSON/TXT（M1 敏感性、M2/M2b/M3 环境评测、M4 LS 验证、M5 规模、M7 λ、OOD 全表、M6 高priority 重规划副本） |
| `trainings/` | 4 组训练产物（ckpt.pt + ckpt_config.json + train_curve.json）：outE(M2 载荷)、outE2(M2b 载荷+强风增强)、outF(M3 κ)、outD(M5 n=50 规模) |
| `logs/` | 4 份训练运行日志（`*_train.log`） |

## 逐项来源与判定（详见 report/09）

| 文件 | 对应模块 | 判定 |
|---|---|---|
| `results/exp_v3_m1_hover_sens.json` | M1 t_service 四档敏感性 | ✅ 交付（默认 1.0 min） |
| `results/exp_v3_m2_eval.txt` / `exp_v3_env_eval.json` | M2 载荷耦合世界（B/E） | ❌ 不通过 |
| `results/exp_v3_m2b_eval.txt` | M2b 载荷+强风增强（B/E/E2） | ❌ 不通过（载荷语义保留可选审计，default OFF） |
| `results/exp_v3_m3_eval.txt` | M3 κ=1.15 世界（B/F） | ⚠️ 条件通过 → 交付默认（κ=1.15/E_res=2.0） |
| `results/exp_v3_m4_ls_validation*` | M4 约束感知 LS | ✅ 交付（默认开启） |
| `results/exp_v3_m5.txt` / `exp_v3_m5_scale.json` | M5 规模外推（n=50/100） | ✅ 通过（+9.1% / +13.2%） |
| `results/exp_v3_m6_replan_highprio.json` | M6 高优先级穿插流 | ⚠️ 条件通过（+7% 均值/3 种子） |
| `results/exp_v3_m7_lambda_flow.json` | M7 λ 敏感性（紧窗） | ✅ 通过（决策排序稳健） |
| `results/exp_v3_ood_rl_ls.json` / `exp_v3_ood_rl_vs_greedy_ls.json` | OOD 全表（裸/RL+LS/贪心+LS 公平对照） | 结论：LS 是均衡器（0/9 RL 胜、全部可行） |

## 复现说明（重要）

脚本原位于 `model_path_planning/code/`，其 `out/` 输出路径为相对路径。归档后正式复现请：
1. 把需要的脚本拷回 `model_path_planning/code/`（与 env/model/train 同目录）；
2. 训练产物按需拷回（示例：`cp trainings/outD/ckpt.pt ../../model_path_planning/code/outD/ckpt.pt`）；
3. 训练命令（各产物对应）：见 `ckpt_config.json` 内记录的超参（`--steps/--d/--use-edge/--tanh-prior/--payload-w?/--kappa?/--wind-aug?/--n-task?`）。

## git 状态

归档前进度的 git 提交编号（分支 feature/pathplanning-v3 → 已合并 feature/swflow-optimization）：M1 之后各模块实验提交见 `git log --oneline feature/swflow-optimization`（关键字 M2/M3/M4/M5/M6/M7）。本目录文件随当次提交一并纳入版本管理（.pt 权重按 .gitignore 不入库——训练曲线/配置/日志均已入库）。
