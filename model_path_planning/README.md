# model_path_planning — 无人机任务级路径规划模型

> **定位**：五模型管线（浓度标定 → total MC/MC-LR 预测 → 二维浅水流 → 降解动力学 → **本模块**）中的决策链。输入为物理推演的**任务库**（投放点/剂量/窗口/时滞），输出为每架无人机的访问序列——目标是使**风险加权治理生效时间**最短。
> **版本**：V2.6 基线（26 轮审查）+ V2.7 优化轮（修复+文献驱动+v3.0 契约）+ **V3 模块验证轮（M1–M7，见 `report/09`）**。

## 报告速查

| 文档 | 内容 |
|---|---|
| `report/01_文献调研综述.md` | 22 篇文献逐条评述（**2026-08-24 已修正 12 处引用错误**；20 个 PDF 全部在 `report/references/`，附录 A 为实时下载清单） |
| `report/02_架构迭代审查日志.md` | RV-01→RV-26（V0.1→V2.6）+ **RV-27→RV-34（2026-08-24 V2.7 优化轮）** |
| `report/03_无人机任务级路径规划模型架构报告.md` | 最终架构报告 v2.7（图文并茂；§5 实验表为 2026-08-24 复测/重跑数字） |
| `report/04_模型教学讲解.md` | 教学文档（全流程、选型原因、真实数据走查、零基础补课；§12 缺陷清单带修复状态横幅） |
| `report/05_质量审查报告.md` | 独立质量审查（12 项缺陷，附复现证据；顶部横幅记录修复进展） |
| `report/06_五模型联动适配性审查与路径规划改进方向.md` | 五模块上下游接口契约、6 个失配点、v3.0 改进方向 |
| `report/07_优化实验流程记录.md` | **2026-08-24 全部优化实验的流程记录**（修复验证、三组重训、强风压力测试、×8 增广、λ 敏感性、OOD 重测、v3.0 水流任务） |
| `report/08_优化方案_不足与解决方案.md` | 最终优化方案；当前不足（诚实分级）；解决方案与优先级路线图 |
| `report/09_模块级优化验证报告.md` | **V3 模块级验证**：8 项优化（M1–M7）逐一"改动→验收→实验→判定→交付决定"；4 通过/2 条件通过/2 不通过（M2 载荷训练驳回但保留可选审计） |
| `data/数据调研与下载记录.md` | 数据集调研与下载状态（2026-08-24 更正 3 处失实）；`data/raw/` 已被 `.gitignore` 排除 |

## 快速复现

安装：`pip install torch numpy ortools matplotlib pypdf`（CPU 即可，全部实验 CPU 完成）。

```powershell
cd model_path_planning/code
python scenario.py                    # 东湖场景自检
python flow_tasks.py                  # v3.0 水流任务生成器自检 (需上游 SWF/降解数据)
# 训练产物统一输出至归档目录 (2026-08-25 起 code/ 不再保留输出, 保持整洁)
TRAIN_OUT="../../model_Two-dimensional_water_flow/report/experiments/V2.7_pathplanning/trainings"
python train.py --steps 1200 --d 128 --out "$TRAIN_OUT/A2"    # V2.7 基线 (独立时钟)
python train.py --steps 1200 --d 128 --use-edge --tanh-prior --out "$TRAIN_OUT/B2"   # 边特征+解码先验
python train.py --steps 1000 --d 128 --use-edge --tanh-prior --n-task 50 --batch 8 --out "$TRAIN_OUT/D2"  # n=50 规模 (M5)
python train.py --steps 1200 --d 128 --use-edge --tanh-prior --mode flow --n-task 10 --out "$TRAIN_OUT/C2"  # v3.0 水流任务
CKPT_B="$TRAIN_OUT/B/ckpt.pt"                # V2.7 交付基线 (B) 已存于归档
python evaluate.py --ckpt "$CKPT_B"          # 主对比 (可加 --augment *8 增广)
python exp_v27.py --ckpts B=$CKPT_B          # 汇总评测 (新运行会重建 code/out, 属运行期副产物, 跑完可再归档)
python ablation.py --ckpt "$CKPT_B"          # 风/λ/采样数
python replan_demo.py --ckpt "$CKPT_B"       # 动态重规划
python ood_bench.py --ckpt "$CKPT_B"         # 分布外压力测试 (含 OR-Tools 状态披露)
python plots.py                              # 报告插图 (读归档 results/ 写归档 figures/)
```

实验产物对照（2026-08-25 整理后）：V2.6/V2.7 全部输出归档于 `model_Two-dimensional_water_flow/report/experiments/V2.7_pathplanning/`——`results/`（评测 JSON/文本）、`figures/`（报告插图）、`trainings/`（A/B/C/C2 训练产物 + ckpt_v26_baseline.pt 旧权重）、`logs/`（训练日志）；V3 轮归 `…/experiments/V3_pathplanning/`。`code/` 不再保留任何输出目录。
