# model_path_planning — 无人机任务级路径规划模型

> **定位**：五模型管线（浓度标定 → total MC/MC-LR 预测 → 二维浅水流 → 降解动力学 → **本模块**）中的决策链。输入为物理推演的**任务库**（投放点/剂量/窗口/时滞），输出为每架无人机的访问序列——目标是使**风险加权治理生效时间**最短。
> **版本**：V2.6 基线（26 轮审查）+ V2.7 优化轮（质量审查修复 + 20 篇文献驱动改进 + v3.0 任务契约落地）。详见 `report/02` 与 `report/07`。

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
| `data/数据调研与下载记录.md` | 数据集调研与下载状态（2026-08-24 更正 3 处失实）；`data/raw/` 已被 `.gitignore` 排除 |

## 快速复现

安装：`pip install torch numpy ortools matplotlib pypdf`（CPU 即可，全部实验 CPU 完成）。

```powershell
cd model_path_planning/code
python scenario.py                    # 东湖场景自检
python flow_tasks.py                  # v3.0 水流任务生成器自检 (需上游 SWF/降解数据)
python train.py --steps 1200 --d 128 --out outA          # V2.7 基线 (独立时钟) ~25 min
python train.py --steps 1200 --d 128 --use-edge --tanh-prior --out outB   # 边特征+解码先验
python train.py --steps 1200 --d 128 --use-edge --tanh-prior --mode flow --n-task 10 --out outC  # v3.0 水流任务
python evaluate.py --ckpt outA/ckpt.pt          # 主对比 (可加 --augment *8 增广)
python evaluate.py --ckpt outC/ckpt.pt --mode flow   # v3.0 任务对比
python exp_v27.py --ckpts A=outA/ckpt.pt,B=outB/ckpt.pt,C=outC/ckpt.pt > out/exp_v27_report.txt
python ablation.py --ckpt outB/ckpt.pt    # 风/λ/采样数 (λ 敏感性 2026-08-24 实现)
python replan_demo.py --ckpt outB/ckpt.pt # 动态重规划
python ood_bench.py --ckpt outB/ckpt.pt   # 分布外压力测试 (含 OR-Tools 状态披露)
python plots.py                           # 报告插图
```

实验产物对照：V2.6 实验结果在 `code/out/`（train_curve/eval_results/…）；V2.7 重训结果在 `code/outA|outB|outC/`，汇总在 `code/out/exp_v27.json`。
