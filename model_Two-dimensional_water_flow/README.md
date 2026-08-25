# model_Two-dimensional_water_flow — 二维浅水流模型（武汉东湖）

> iGEM 干实验板块：通过对东湖水流的推演，计算**无人机投放降解菌的投放地点**与**单次有效覆盖面积**。
> 隶属系统："监测（工程菌 MC-LR 传感器）→ 预警 → 无人机投放降解菌 → 回收"闭环。

## 目录

| 路径 | 内容 |
|---|---|
| `MODEL_ARCHITECTURE.md` | **最终模型架构文档**（图文并茂：方程、图件、选择理由、验证、局限、未来方向） |
| `ARCHITECTURE_ITERATIONS.md` | **30 轮架构审查/改进日志**（≥20 轮要求） |
| `report/文献综述.md` | 全网权威文献考察（10 主题，含 DOI/方法/借鉴点）与下载状态 |
| `report/lit_notes.md` | 文献调研底稿（含【待核实】诚实标注） |
| `report/references/` | 已下载文献 PDF（开放获取） |
| `data/DATASETS.md` | 数据集清单/适配度/链接/**实际下载情况**（含失败记录） |
| `data/research_eastlake.md` | 东湖基础调研（面积/水深/水系/风/数据源，全部带来源 URL） |
| `data/raw/` | 原始数据（OSM 矢量、Open-Meteo 风场、DEM、HydroLAKES 等） |
| `data/processed/` | 域/流场/优化结果（npz） |
| `src/swflow/` | 模型代码（domain / swe_si / particles / deployment / viz） |
| `scripts/` | 可复现管线（01…06） |
| `figures/` | 全部图件（PNG） |

## 核心结论速览

- **流场**：SE 季风 2.5 m/s → 东湖风生流峰值 **0.068** m/s、均值 0.015 m/s（N 3.0 m/s 达 0.081 峰值；W 2.0 m/s 0.043/0.010）；50 m 网格 31.2 km²（OSM 掩膜，官方 31.75 km² 吻合 98%）；水深按东湖 42 个实测点标定（**B3 幂指数**：场均 2.48 m、标定目标最大 4.66 m、场上实际最大 3.70 m，2026-08-24 起生产）；风应力默认湖面 Cd 式（`cd_lake`，Zhang 2024 Fig.4b 拟合）+ 粒子默认表层风漂移 2%（详见 report/优化方案与不足）。
- **单次覆盖**：一次投放（σ0=25 m 菌团）2 h 有效覆盖 **0.038–0.080 km²**（阈值 5% 峰值浓度，随阈值/风况/时段变化）→ 结论：**精准点治**而非面覆盖是设计使命；建议处置单元按 0.05–0.3 km² 热点设计。
- **投放点**：最优投放点位于风险斑块中心偏上风侧（漂移预补偿自动实现）；5 成员风况系综下保护比例区间 [0.050, 0.057]（±7%），**决策稳健**（阈值重抽样 bug 已修复并多种子复核）；多点（3–4 个、600 m 间距）累计期望保护 ≈15–19%（上限估计）。
- **难度结论**：物理模型无训练环节；升级 PINN/代理模型的最大成本是离线训练数据生成（详见架构文档 §17）。
- **验证**：驻波周期误差 0.16%、体积守恒 <1e-15、解析风生环流平衡对齐。
- **诚实声明**：水深为**形态学重建**（用东湖 MIKE21 论文公布的实测均值/最大值做标定，无实测等深网格）；无东湖实测流速比对（论文给出新沟验证点误差口径 <15%/<25%，待数据复现）；覆盖阈值为演示值（待降解模块 C_req 标定）。

## 快速复现

```
cd model_Two-dimensional_water_flow
python src/swflow/domain.py              # 域+水深（需已抓取 OSM 数据）
python scripts/02_run_circulation.py     # 3 个风况场景自旋（~20 分钟）
python scripts/03_run_particles.py       # 单次投放/覆盖实验（~5 分钟）
python scripts/04_run_optimization.py    # 投放点优化（~10 分钟，需系综数据）
python scripts/05_run_sensitivity.py     # 敏感性（~15 分钟）
```
依赖：Python 3.12，numpy / scipy / matplotlib（无需 GDAL/地理库）。
