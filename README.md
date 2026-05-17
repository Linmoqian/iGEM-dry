# iGEM Dry Lab — 蓝藻水华智能监测系统

构建无人机投放工程菌检测节点的闭环系统，实时监测与预警水体藻毒素风险。

## 项目结构

```
iGEM-dry/
├── model/          数学建模 — 藻毒素浓度预测
├── viewweb/        Web 平台 — 态势展示与设备管理
├── hardware/       硬件 — ESP32 检测节点设计
└── docs/           项目文档与实施计划
```

---

## 环境准备

### Python（模型训练）

```bash
cd model
conda env create -f environment.yml
conda activate igem-cyanohab
```

### Node.js（Web 平台）

需要 Node.js >= 18。

```bash
cd viewweb
npm install
```

---

## 快速启动

### 模型训练

```bash
cd model
conda activate igem-cyanohab

# 数据清洗（14 个数据集并行处理）
python run_clean.py

# 模型训练（分类 + 回归 + 集成）
python run_train.py

# 仅训练分类任务
python run_train.py --task classification

# 启用 Optuna 超参搜索
python run_train.py --tune --n-trials 100
```

训练完成后，模型保存在 `model/models/`，评估图表在 `model/figures/`。

### Web 平台

```bash
cd viewweb
npm run dev    # 开发服务器 http://localhost:3000
npm run build  # 生产构建
npm run lint   # 代码检查
```

四个页面：

| 路由 | 功能 |
|------|------|
| `/` | 总览仪表盘 |
| `/map` | 地图监视（Leaflet） |
| `/data` | 数据分析（Recharts） |
| `/device` | 设备配对与管理 |

---

## 模块详情

### model/ — 蓝藻水华预测模型

双任务集成模型：分类（MICX 检出概率）+ 回归（MICX 浓度预测）。

**数据流：**

```
data/原始数据 → run_clean.py → data/cleaned/*.parquet
                                    ↓
              run_train.py → features.py → train.py → models/*.joblib
                                                    → figures/*.webp
                                                    → reports/*.md
```

**核心模块：**

| 文件 | 职责 |
|------|------|
| `src/config.py` | 路径常量、特征分组列名、数据集注册表 |
| `src/clean.py` | 数据清洗原语（IQR 裁剪、检测限替换等） |
| `src/features.py` | 特征工程统一入口 |
| `src/train.py` | XGBoost/LightGBM 训练 + 5-fold CV + 集成 |
| `src/evaluate.py` | 分类/回归指标、混淆矩阵、ROC/PR 曲线 |
| `src/interpret.py` | SHAP 解释（蜂群图、依赖图、瀑布图） |
| `src/datasets/` | 每个数据集一个清洗模块 |

**已建模数据集：**

| 数据集 | 来源 | 样本数 | 特征数 |
|--------|------|--------|--------|
| HABs Training | EPA NLA 全国湖泊调查 | 3,663 | 45 |
| Lake Erie | 伊利湖长期监测 | 2,659 | 23 |
| SF Estuary | 旧金山河口监测 | 437 | 25 |

**新增数据集：** 在 `src/datasets/` 下创建模块实现 `clean()` 函数，在 `config.py` 的 `get_v2_configs()` 中注册。

### viewweb/ — Web 可视化平台

- Next.js 16 (App Router) + React 19 + TypeScript
- Tailwind CSS v4，暗色科技风主题
- Leaflet 地图 + Recharts 图表
- dnd-kit 设备卡片拖拽排序

### hardware/ — ESP32 检测节点

- 3D 结构设计 + 面包板 Demo 验证完成
- PCB 版本待开发

### docs/ — 项目文档

- `docs/plan/plan.md` — 项目实施计划（主文档）
- `docs/tex/` — LaTeX 源码，可编译为 PDF
- `docs/md/` — Markdown 版本文档

---

## 代码规范

- **Python**：PEP 8，`ruff check` + `ruff format`
- **TypeScript**：ESLint + Prettier，Airbnb 风格
- **Git 提交**：Conventional Commits，中文描述

## Git 工作流

```
main        ← 稳定代码
feature/*   ← 功能开发分支
```

提交格式：`<type>: <中文描述>`

type 可选：`feat` / `fix` / `refactor` / `docs` / `test` / `chore` / `perf`
