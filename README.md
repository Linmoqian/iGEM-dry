# iGEM Dry Lab — 蓝藻水华智能监测系统

构建无人机投放工程菌检测节点的闭环系统，实时监测与预警水体藻毒素风险。

## 项目结构

| 目录 | 说明 |
|------|------|
| `web/` | 前端 — Vite + React 18 + Tailwind CSS 4，浅色青蓝水体实验风 |
| `model/` | 数学建模 — 藻毒素浓度预测（XGBoost/LightGBM） |
| `hardware/` | 硬件 — ESP32 检测节点设计 |
| `docs/` | 项目文档与实施计划 |
| `design-assets/` | 设计资产 — 页面目标图、组件参考、prompt |

## 快速启动

```bash
# 前端
cd web && npm install && npm run dev    # localhost:5173

# 数学建模
cd model && conda activate igem-cyanohab && python run_train.py
```

## Git 工作流

```
main        ← 稳定代码
feature/*   ← 功能开发分支
```

提交格式：`<type>: <中文描述>`
