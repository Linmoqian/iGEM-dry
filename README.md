# iGEM Dry Lab — 蓝藻水华智能监测系统

构建无人机投放工程菌检测节点的闭环系统，实时监测与预警水体藻毒素风险.

## 项目结构

| 目录 | 说明 |
|------|------|
| `viewweb/` | **旧版** — Next.js 16 + React 19，暗色科技风 |
| `web_redo/` | **新版（重建中）** — Vite + React 18，浅色青蓝水体实验风 |
| `model/` | 数学建模 — 藻毒素浓度预测 |
| `hardware/` | 硬件 — ESP32 检测节点设计 |
| `docs/` | 项目文档与实施计划 |

### viewweb vs web_redo

| | `viewweb/` | `web_redo/` |
|---|---|---|
| 状态 | 旧版，功能完整 | 新版，重建中 |
| 构建工具 | Next.js 16 (Turbopack) | Vite |
| React 版本 | 19 | 18 |
| 路由 | App Router (SSR) | react-router-dom (SPA) |
| UI 风格 | 暗色科技风 | 浅色青蓝水体实验风 |
| 启动 | `npm run dev` → localhost:3000 | `npm run dev` → localhost:5173 |
| 优势 | 功能齐全，已上线可用 | 无 SSR 水合问题，纯静态产物，便于迁移 Tauri/移动端 |

## 快速启动

```bash
# 旧版
cd viewweb && npm install && npm run dev

# 新版
cd web_redo && npm install && npm run dev
```

## Git 工作流

```
main        ← 稳定代码
feature/*   ← 功能开发分支
```

提交格式：`<type>: <中文描述>`
