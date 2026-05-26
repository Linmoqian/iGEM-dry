# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

iGEM Dry Lab — 蓝藻水华智能监测系统。构建无人机投放工程菌检测节点的闭环系统，实时监测与预警水体藻毒素风险。武汉东湖为模拟监测区域。

## 项目结构

- **web/** — 前端（Vite + React 18 + react-router-dom + Tailwind CSS 4），纯 SPA，计划迁移 Tauri
- **model/** — 数学建模（Python 3.11，XGBoost/LightGBM），已完成
- **hardware/** — 硬件设计（ESP32 检测节点）
- **design-assets/** — 设计资产（页面目标图、组件参考、prompt）
- **docs/** — 项目文档与计划

## 常用命令

### 前端（Vite）
```bash
cd web
npm run dev       # 开发服务器 localhost:5173
npm run build     # tsc && vite build
npm run preview   # 预览生产构建
npm run lint      # ESLint 检查
```

### 数学建模（Python）
```bash
cd model
conda activate igem-cyanohab
python run_train.py    # 模型训练
python run_clean.py    # 数据清洗
```

## 架构要点

### 前端路由（react-router-dom SPA）
- `/` → OverviewPage — KPI 卡片、最新读数表、趋势图、告警摘要
- `/map` → MapMonitorPage — Leaflet 地图 + IDW 热力图 + 设备标记 + 详情面板
- `/data` → DataAnalysisPage — 多轴趋势图、设备对比、AI 预测曲线
- `/device` → DevicePairingPage — 设备 CRUD、蓝牙/WiFi 配对模拟、拖拽排序

### 代码组织
- `src/pages/` — 页面组件（PascalCase）
- `src/layouts/` — AppShell、AppHeader、SidebarNav 布局
- `src/components/common/` — 通用 UI 组件（AquaCard、RiskBadge、StatusBadge）
- `src/data/` — mock 数据层（demoReadings.ts、mockPredictions.ts），14 个模拟设备
- `src/types/` — TypeScript 类型定义（domain.ts、leaflet-heat.d.ts）
- 路径别名：`@/*` → `src/*`

### 技术约束
- React 18（非 19），因 react-leaflet 等库兼容性
- Tailwind CSS 4 语法：`@import "tailwindcss"` + `@theme inline {}`
- 使用 React 18 时 Leaflet 可直接导入，无需 SSR 动态加载

### Python 建模管线
```
raw datasets → clean.py → features.py → train.py → evaluate.py → interpret.py
```
特征维度：水质（温度、DO、pH、浊度、营养盐）、气候、土地利用、地形、营养收支。

## Git 工作流

- 主分支：`main`（稳定），功能分支：`feature/*`
- 提交格式：`<type>: <中文描述>`，如 `feat(web): 添加地图页`

## 注意事项

- 项目为 iGEM 竞赛原型，无自动化测试
- 所有 UI 文案为中文
- Conda 环境名：`igem-cyanohab`，环境定义在 `model/environment.yml`
- 设计稿参考：`design-assets/page-objectives/`
