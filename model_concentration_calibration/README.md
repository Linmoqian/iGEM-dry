# 浓度标定模型（model_concentration_calibration）

干实验板块：将工程菌检测节点的光信号（sfGFP/TurboRFP 比值荧光）转换为 MC-LR 浓度估计与预警决策的标定模型。

## 目录结构

```
model_concentration_calibration/
├── report/                      # 交付文档（4 份）
│   ├── 01_文献综述_浓度标定模型.md      # 17 篇文献：标题/链接/简介/方法/借鉴点/下载状态
│   ├── 02_数据集调研与下载.md          # 数据集：内容/适配度/链接/下载情况 + 最小数据契约
│   ├── 03_模型架构设计报告_终版.md      # 最终报告：架构(图文)/理由/实验结果(含真实数据§5.5)/未尝试/优缺点/未来方向
│   ├── 04_架构审查迭代记录.md          # 26 轮全量审查记录（含 3 位外部评审员独立审查）
│   └── 07_系统级衔接与集成报告.md      # 五模型闭环：接口契约/真实数据审计/先例调研/调整方向
├── references/                  # 16 篇已下载 OA 论文 PDF（约 43MB）
├── datasets/                    # 已下载数据集（FPbase、文献标定 CSV、qPCR 标准曲线）
├── src/                         # 参考实现（Python 3.11+，numpy/scipy）
│   ├── forward.py                #   前向模型：时变 Hill/折合比/噪声/先验
│   ├── calibrate.py              #   拟合(MAP+Laplace)/反演(网格)/LOD/决策
│   ├── synth.py                  #   合成数据（trigger 剖面）
│   ├── qs_ode.py                 #   机理先验模拟器（QS-ODE）
│   ├── device.py                 #   光电读数链+装置仿射校准(含暗电流偏置/暗基线扣除)
│   ├── loader.py                 #   真实湿实验数据加载+QC+逐时间fold(33h工作簿)
│   ├── deploy.py                 #   部署产物（参数+反演查找表）
│   └── evaluate.py               #   LOBO 交叉验证+指标
├── scripts/                     # 实验与作图脚本（_run*.py、_fig*.py）
├── figures/                     # 7 张图（架构/剂量族/拟合/融合/LOD决策/装置/触发子对比）
└── architecture_v1.md            # v1 草稿（审查输入，历史存档）
```

## 快速复现

```bash
cd model_concentration_calibration
python scripts/_run3.py   # 四 trigger 拟合+参数恢复+LOD（已修复 LOQ=None 格式化）
python scripts/_run5.py   # LOBO 交叉验证（环境先验 vs 平先验）
python scripts/_run6.py   # 多时间点融合实验
python scripts/_real_fit3.py   # 真实湿实验数据逐 trigger 拟合+fig8
python scripts/_deploy_check.py # 部署产物(LUT/解析反演)往返校验 + QS-ODE 先验敏感性
python scripts/_fig1.py   # 依次生成 figures/ 全部图表
```

## 核心结论（30 秒版）

1. **方案**：逐 trigger 的时变 Hill 标定（11 参数/构型）→ MAP+Laplace 参数后验 → 对数网格浓度后验积分 → 多时间点融合 → P(C≥1 μg/L) 成本最小化决策；装置端仿射+串扰+暗基线标定；边缘用查找表+解析反演。
2. **能力边界**：LOD 0.28–1.34 μg/L（trigger 依赖），LOQ 量程内不可达 → 1 μg/L 预警判别（AUC 0.95–0.98）是现实目标，全域定量是长期目标；预警决策与项目定位一致。
3. **数据现状**：公开数据集中不存在工程菌体系（荧光×浓度×时间）成对数据；已用 16 篇 OA 文献 + FPbase + 文献数字化标定 CSV 建立先验体系；真实湿实验数据按 02 报告数据契约接入后即可切换训练（契约/QC 已就绪）。
4. **真实数据已接入**：docs/Introduction 33h 工作簿 → loader.py → 逐 trigger 拟合（详见 03 报告 §5.5 与 07 报告 §4）；灵敏度结论：正响应单点检出 1 μg/L 不可靠，多通道融合（fuse，见 07 报告 §2B）为必需接口。
5. **下一迭代入口**：fuse() 多节点融合接口、板位随机化数据修复、redo_v2 风险图作为 p_env、HMC/AR(1) 不确定性改进。

## 备注

- Zenodo/figshare 部分数据集因平台 IP 限流未下载成功，记录见 02 报告第 2、5 节（人工浏览器下载即可补全）；
- 本板路径建议以仓库根目录相对路径引用：model_concentration_calibration/report/…；
- 所有实验结果基于合成数据（seeds 固定），结论以方法学论证为主；真实数据到位后需重新标定验证。