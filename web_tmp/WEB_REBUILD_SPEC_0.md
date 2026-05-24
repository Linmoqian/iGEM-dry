# 网页重构有效信息文档 / Web Rebuild Specification

## 文档元信息

- **项目名称**：水体藻毒素监测平台 / Water Algal Toxin Monitoring Platform
- **目标输出目录**：`/iGEM-dry/web_tmp`
- **素材目录**：`/iGEM-dry/web_tmp/Materials`
- **文档版本**：1.0.0
- **最后更新**：2026-05-21
- **目标读者**：后续网页编写 Agent（将在空白工作目录中根据本文档重新构建网页）

---

## 目录

1. [项目目标摘要](#1-项目目标摘要)
2. [信息来源与优先级](#2-信息来源与优先级)
3. [技术路线](#3-技术路线)
4. [整体视觉设计系统](#4-整体视觉设计系统)
5. [全局布局规范](#5-全局布局规范)
6. [页面元素级规格总表](#6-页面元素级规格总表)
7. [图片与图标占位符总表](#7-图片与图标占位符总表)
8. [页面 1：总览页详细规格](#8-页面-1总览页详细规格)
9. [页面 2：地图监视页详细规格](#9-页面-2地图监视页详细规格)
10. [页面 3：数据分析页详细规格](#10-页面-3数据分析页详细规格)
11. [页面 4：设备配对页详细规格](#11-页面-4设备配对页详细规格)
12. [数据模型与字段规范](#12-数据模型与字段规范)
13. [风险规则与状态规则](#13-风险规则与状态规则)
14. [交互流程](#14-交互流程)
15. [组件拆分方案](#15-组件拆分方案)
16. [素材占位符实现规范](#16-素材占位符实现规范)
17. [Vite 重构迁移步骤](#17-vite-重构迁移步骤)
18. [验收标准](#18-验收标准)
19. [缺失信息与待确认问题](#19-缺失信息与待确认问题)

---

## 1. 项目目标摘要

### 项目是什么

水体藻毒素监测平台是一个面向 **iGEM 干实验团队** 的水体藻毒素监测 Dashboard。它是一个可操作的数据监控平台，不是宣传落地页或营销网站。

系统通过模拟数据展示水体采样设备状态、湖泊风险热力图、藻毒素趋势分析和设备配对管理。

### 面向谁使用

- iGEM 干实验团队成员
- 项目演示和答辩观众
- 设备管理和数据分析人员

### 为什么要重构

当前项目基于 Next.js App Router，页面结构偏通用后台管理系统风格，与 iGEM 展示型监控面板的设计目标存在差距。四张目标设计蓝图提供了更接近 iGEM 水体实验风格的视觉方向：

- 顶部品牌导航更完整
- 左侧边栏带水体装饰
- 卡片更紧凑、信息密度更高
- 图表和地图更具视觉表达
- 统一浅色青蓝水体实验风

### 为什么从 Next.js 迁移到 Vite

1. **部署简化**：本项目当前阶段不需要 SSR/SSG，纯客户端 SPA 即可满足所有需求。Vite 构建的纯静态文件可部署到任意静态服务器，无需 Node.js 运行环境。
2. **构建速度**：Vite 开发服务器基于 ESM，冷启动和 HMR 速度远快于 Next.js 的 Webpack/Turbopack 编译链路。
3. **复杂度降低**：Next.js App Router 的 Server Component / Client Component 边界、SSR 相关配置（如 Leaflet 必须用 dynamic import 禁用 SSR）增加了不必要的复杂度。
4. **Leaflet 天然兼容**：Leaflet 需要浏览器 DOM API，在 Vite 纯客户端环境下无需 `next/dynamic` 的 SSR 禁用处理，代码更直观。
5. **本项目无 SEO 需求**：Dashboard 类应用无需搜索引擎索引，SSR 无实际收益。
6. **PROJECT.md 技术栈约束已更新**：本次重构要求技术路线以 React + Vite 为准，PROJECT.md 中的 Next.js 约束仅作为旧项目状态记录。

### 新网页需要保留的核心功能

1. 4 个路由页面：`/`（总览）、`/map`（地图监视）、`/data`（数据分析）、`/device`（设备配对）
2. 设备状态三态：`online` / `idle` / `offline`
3. 设备卡片展示：名称、位置、连接方式、电量、信号、藻毒素、水温、pH、更新时间
4. 设备页拖拽排序（@dnd-kit）
5. 地图页 Leaflet 真实地图、设备点位、热力图
6. 数据分析和预测图表（Recharts）
7. 模拟数据来源（demoReadings 迁移）
8. 所有交互均为前端本地 state 模拟

### 新网页视觉上要达到的效果

- 浅色青蓝水体实验风（近白背景、浅青蓝渐变、薄荷绿、柔和珊瑚红）
- 统一全局布局：顶部品牌栏 + 左侧垂直导航 + 主内容区
- 卡片紧凑、信息密度高
- 水波、气泡、实验器材等装饰元素占位
- 萌物/吉祥物占位符融入页面
- 桌面端 1280px - 1600px 为最佳体验

### 当前阶段不做的事情

- 真实后端 API、数据库、WebSocket 或硬件通信
- 登录、鉴权、多用户权限
- 本地持久化（刷新后模拟状态可重置）
- 真实邮件、短信、推送告警
- 正式萌物、插画、图标资产（仅占位）
- 暗色模式切换
- 引入大型 UI 组件库（如 Ant Design、MUI）

---

## 2. 信息来源与优先级

### 已读取和分析的文件

**文档文件：**
- `planning/PROJECT.md` — 项目说明、功能范围、验收标准、组件规划
- `TODO.md` — 详细的任务分解和视觉改造要求
- `package.json` — 当前依赖清单

**设计蓝图（目标图）：**
- `designe-figure/Page_design_objective/总览页目标.png` — 总览页设计蓝图
- `designe-figure/Page_design_objective/地图监视页目标.png` — 地图监视页设计蓝图
- `designe-figure/Page_design_objective/数据分析页目标.png` — 数据分析页设计蓝图
- `designe-figure/Page_design_objective/设备配对页目标.png` — 设备配对页设计蓝图

**当前项目页面文件：**
- `app/page.tsx` — 总览页
- `app/layout.tsx` — 全局布局
- `app/map/page.tsx` — 地图页入口
- `app/map/MapDashboard.tsx` — 地图页主组件
- `app/map/MonitoringMap.tsx` — Leaflet 地图核心组件
- `app/map/MapClientLoader.tsx` — Next.js 动态加载包装
- `app/data/page.tsx` — 数据分析页
- `app/device/page.tsx` — 设备配对页

**当前项目组件文件：**
- `app/components/TopNav.tsx` — 顶部导航栏
- `app/components/SidebarNav.tsx` — 侧边导航栏
- `app/components/Navbar.tsx` — 旧版窄侧边导航
- `app/components/PageHeader.tsx` — 页面标题组件
- `app/components/MetricCard.tsx` — 指标卡组件
- `app/components/SectionPanel.tsx` — 通用面板组件
- `app/components/StatusBadge.tsx` — 状态标签
- `app/components/RiskBadge.tsx` — 风险标签
- `app/components/MiniSparkline.tsx` — 迷你趋势图
- `app/components/EmptyAssetSlot.tsx` — 空资源占位组件
- `app/components/DeviceStatus.tsx` — 设备状态卡片
- `app/components/FilterBar.tsx` — 数据筛选栏
- `app/components/OverviewTrendChart.tsx` — 总览趋势图
- `app/components/ToxinPredictionModel.tsx` — AI 预测模块

**数据与样式文件：**
- `app/lib/demoReadings.ts` — 核心模拟数据与风险计算
- `app/globals.css` — 全局样式与设计 token
- `app/types/leaflet-heat.d.ts` — Leaflet.heat 类型声明

### 信息优先级

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | 用户当前新增要求 | 技术路线变更为 Vite + React，文档格式和内容要求 |
| 2 | 四张目标设计蓝图 | 页面布局、元素位置、视觉风格的权威参考 |
| 3 | PROJECT.md 功能范围 | 核心功能、页面范围、数据来源、交互能力、验收标准 |
| 4 | 当前项目源代码 | 数据模型、组件逻辑、样式 token、mock data 结构 |
| 5 | 前端最佳实践 | 项目结构、命名规范、可维护性建议 |

### 冲突处理原则

- 如果 PROJECT.md 与本次重构要求冲突：**功能保留参考 PROJECT.md，技术路线以 React + Vite 为准**
- 如果设计蓝图与 PROJECT.md 功能描述冲突：**以设计蓝图的布局和信息层级为准**
- 如果旧代码逻辑与设计蓝图冲突：**以设计蓝图为视觉目标，保留旧代码中的核心功能逻辑**

---

## 3. 技术路线

### 3.1 目标技术栈

| 类别 | 技术 | 用途 | 是否必须 | 备注 |
|------|------|------|----------|------|
| 构建工具 | Vite 5.x | 开发服务器 + 生产构建 | 是 | 替代 Next.js |
| UI 框架 | React 19.x | 组件化 UI | 是 | 保持与旧项目相同的 React 大版本 |
| 类型系统 | TypeScript 5.x | 静态类型检查 | 是 | 保持与旧项目一致 |
| 路由 | react-router-dom 7.x | 客户端路由 | 是 | 替代 Next.js App Router |
| 样式 | Tailwind CSS 4.x + CSS tokens | 原子化样式 + 设计变量 | 是 | 保持 Tailwind v4，移除 `tailwind.config.js` |
| 图表 | Recharts 2.x | 折线图、面积图、预测图 | 是 | 保持与旧项目一致 |
| 地图 | Leaflet 1.9.x + React Leaflet 5.x | 真实地图底图 + 设备点位 | 是 | 保持与旧项目一致 |
| 热力图 | leaflet.heat 0.2.x | 湖泊藻毒素热力分布 | 是 | 保持与旧项目一致 |
| 拖拽 | @dnd-kit 6.x | 设备卡片拖拽排序 | 是 | 保持与旧项目一致 |
| 状态管理 | React useState / useReducer | 本地状态管理 | 是 | 不引入 Redux/Zustand 等外部状态库 |
| 数据来源 | Mock data（src/data/） | 模拟采样数据 | 是 | 从旧项目 demoReadings.ts 迁移 |
| 未来 API 层 | Service 层预留（src/services/） | 未来替换为真实 API | 是 | 当前返回 mock data |
| 构建部署 | vite build → 静态文件 | 生产部署 | 是 | 输出到 dist/ 目录 |

### 3.2 Next.js 到 Vite 迁移说明

| 对比维度 | 旧技术（Next.js） | 新技术（Vite + React） | 替换原因 |
|----------|-------------------|----------------------|----------|
| 构建工具 | Next.js 16.2.3 | Vite 5.x | 纯 SPA 不需要 SSR，Vite 构建更快更简单 |
| 路由系统 | Next.js App Router（文件系统路由） | react-router-dom（编程式路由） | 显式路由配置更清晰，不依赖文件约定 |
| 链接组件 | next/link | react-router-dom Link | 路由库变更连带替换 |
| 图片组件 | next/image | 标准 `<img>` 标签 | 移除 Next.js 专属优化依赖 |
| API 路由 | Next.js API Routes | 无（当前阶段无后端） | 当前阶段不需要后端 |
| SSR/Server Component | `"use client"` 指令 / Server Component | 全客户端渲染 | 不需要 SSR |
| 动态加载 | next/dynamic | React.lazy + Suspense | 标准 React API |
| 页面结构 | app/page.tsx, app/layout.tsx | src/pages/*, src/layouts/* | 标准 Vite React 项目结构 |
| 元数据 | next/Metadata | react-helmet-async 或手动 document.title | 简化实现 |
| 路径别名 | 默认 @/ | vite.config.ts 中配置 resolve.alias | Vite 标准配置 |

### 3.3 推荐依赖清单

**dependencies：**

```json
{
  "react": "^19.0.0",
  "react-dom": "^19.0.0",
  "react-router-dom": "^7.0.0",
  "recharts": "^2.15.0",
  "leaflet": "^1.9.4",
  "react-leaflet": "^5.0.0",
  "leaflet.heat": "^0.2.0",
  "@dnd-kit/core": "^6.3.1",
  "@dnd-kit/sortable": "^10.0.0",
  "@dnd-kit/utilities": "^3.2.2"
}
```

**devDependencies：**

```json
{
  "@types/react": "^19.0.0",
  "@types/react-dom": "^19.0.0",
  "@types/leaflet": "^1.9.21",
  "typescript": "^5.7.0",
  "tailwindcss": "^4.0.0",
  "@tailwindcss/postcss": "^4.0.0",
  "vite": "^6.0.0",
  "@vitejs/plugin-react": "^4.4.0",
  "eslint": "^9.0.0",
  "@eslint/js": "^9.0.0",
  "typescript-eslint": "^8.0.0",
  "eslint-plugin-react-hooks": "^5.0.0",
  "eslint-plugin-react-refresh": "^0.4.0",
  "globals": "^15.0.0"
}
```

**需要移除的 Next.js 专属依赖：**
- `next`
- `eslint-config-next`
- `@types/node`（如仅用于 Next.js 配置）

**保留并继续使用的依赖：**
- `react`, `react-dom`
- `recharts`
- `leaflet`, `react-leaflet`, `leaflet.heat`
- `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities`
- `@types/leaflet`
- `tailwindcss`, `@tailwindcss/postcss`
- `typescript`

### 3.4 推荐脚本命令

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint ."
  }
}
```

### 3.5 推荐项目结构

```
/iGEM-dry/web_tmp/
├── package.json
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── postcss.config.mjs
├── eslint.config.mjs
├── public/
│   └── favicon.svg
├── Materials/                          # 未来素材目录（当前为空）
│   ├── General/
│   ├── Overview/
│   ├── Map/
│   ├── Data/
│   └── Drive/
└── src/
    ├── main.tsx                         # Vite 入口
    ├── App.tsx                          # 根组件，路由挂载
    ├── vite-env.d.ts                    # Vite 类型声明
    ├── router/
    │   └── routes.tsx                   # 路由配置
    ├── layouts/
    │   ├── AppShell.tsx                 # 全局布局壳：Header + Sidebar + MainContent
    │   ├── AppHeader.tsx               # 顶部品牌导航栏
    │   └── SidebarNav.tsx              # 左侧垂直导航栏
    ├── pages/
    │   ├── OverviewPage.tsx            # 总览页 /
    │   ├── MapMonitorPage.tsx          # 地图监视页 /map
    │   ├── DataAnalysisPage.tsx        # 数据分析页 /data
    │   └── DevicePairingPage.tsx       # 设备配对页 /device
    ├── components/
    │   ├── common/
    │   │   ├── AquaPanel.tsx           # 通用白色半透明面板
    │   │   ├── AquaCard.tsx            # 通用数据卡片
    │   │   ├── ImagePlaceholder.tsx    # 图片占位符组件
    │   │   ├── IconPlaceholder.tsx     # 图标占位符组件
    │   │   ├── EmptyAssetSlot.tsx      # 通用资源占位
    │   │   ├── StatusBadge.tsx         # 设备状态标签
    │   │   ├── RiskBadge.tsx           # 风险等级标签
    │   │   ├── AppButton.tsx           # 通用按钮（主/次/危险）
    │   │   └── AppSelect.tsx           # 通用下拉选择器
    │   ├── overview/
    │   │   ├── MetricSummaryCard.tsx    # 顶部指标卡
    │   │   ├── SystemStatusPanel.tsx   # 系统状态面板
    │   │   ├── AlertSummaryPanel.tsx   # 告警摘要面板
    │   │   ├── OverviewTrendChart.tsx  # 7 天趋势图
    │   │   └── LatestReadingsTable.tsx # 最新采样表格
    │   ├── map/
    │   │   ├── LakeRiskMap.tsx         # 湖泊风险地图主组件
    │   │   ├── RiskLegend.tsx          # 风险等级图例
    │   │   ├── SelectedDevicePanel.tsx # 选中设备详情面板
    │   │   ├── MapLayerToggle.tsx      # 图层切换按钮组
    │   │   └── MapMarkerIcon.tsx       # 地图设备点标记（CSS 实现）
    │   ├── data/
    │   │   ├── DataFilterBar.tsx       # 数据分析筛选栏
    │   │   ├── MultiMetricTrendChart.tsx # 多指标趋势图
    │   │   ├── SensorComparisonPanel.tsx # 传感器对比面板
    │   │   └── ToxinPredictionPanel.tsx  # AI 预测模块
    │   └── device/
    │       ├── DeviceToolbar.tsx        # 设备页顶部工具栏
    │       ├── DeviceCardGrid.tsx       # 设备卡片网格（含 DndContext）
    │       ├── DeviceCard.tsx           # 单张设备卡片
    │       ├── DeviceSortDropZone.tsx   # 拖拽排序提示区
    │       ├── PairingPanel.tsx         # 右侧扫描配对面板
    │       ├── DeviceFormModal.tsx      # 添加/编辑设备模态框
    │       └── DiscoveredDeviceItem.tsx # 发现设备列表项
    ├── data/
    │   ├── demoReadings.ts             # 从旧项目迁移的模拟数据
    │   └── mockDevices.ts              # 设备静态配置数据（如有需要）
    ├── services/
    │   ├── readingsService.ts          # 采样数据 service（当前返回 mock）
    │   └── deviceService.ts            # 设备操作 service（当前返回 mock）
    ├── types/
    │   └── domain.ts                   # 所有 TypeScript 类型定义
    ├── utils/
    │   ├── risk.ts                     # 风险等级计算工具
    │   ├── format.ts                   # 数据格式化工具
    │   └── chart.ts                    # 图表数据转换工具
    ├── styles/
    │   ├── tokens.css                  # CSS 设计变量 / 主题 token
    │   ├── globals.css                 # 全局样式 + Tailwind 导入
    │   └── layout.css                  # 布局相关样式
    └── assets/
        └── assetMap.ts                 # 集中管理所有图片/图标路径映射
```

---

## 4. 整体视觉设计系统

### 4.1 色彩 token

以下 CSS 变量定义在 `src/styles/tokens.css` 中，是全局设计变量的唯一来源。

```css
:root {
  /* 背景 */
  --color-bg: #F8FEFF;                      /* 页面主背景，近白 */
  --color-bg-soft: #EAF8FF;                 /* 柔和浅蓝绿背景层 */
  --color-bg-gradient-start: #F8FEFF;       /* 背景渐变起点 */
  --color-bg-gradient-mid: #EAF8FF;         /* 背景渐变中点 */
  --color-bg-gradient-end: #EDFBF7;         /* 背景渐变终点 */

  /* 面板 / 表面 */
  --color-surface: rgba(255, 255, 255, 0.92);    /* 半透明白色面板 */
  --color-surface-strong: rgba(255, 255, 255, 0.97); /* 更实的卡片表面 */

  /* 边框 */
  --color-border: rgba(88, 190, 210, 0.22);       /* 青色低透明边框 */
  --color-border-strong: rgba(88, 190, 210, 0.40); /* 强调边框 */

  /* 主色调 */
  --color-primary: #0D7DF2;                       /* 青蓝主强调 */
  --color-primary-strong: #0966D6;                /* 强调按钮、选中态 */
  --color-primary-light: rgba(13, 125, 242, 0.08); /* 主色浅底 */

  /* 辅助色 */
  --color-cyan: #16B8D8;                          /* 青色辅助 */
  --color-mint: #08A65A;                          /* 正常/成功状态绿 */
  --color-warning: #F7B500;                       /* 关注/空闲状态黄 */
  --color-orange: #FF7A00;                        /* 警戒状态橙 */
  --color-danger: #F5222D;                        /* 高风险告警红 */

  /* 文字 */
  --color-text: #0B2540;                          /* 深海青黑正文 */
  --color-muted: #5A7184;                         /* 灰蓝次级文字 */

  /* 阴影 */
  --color-card-shadow: rgba(13, 125, 242, 0.06);  /* 卡片阴影 */
  --color-card-shadow-hover: rgba(13, 125, 242, 0.10); /* 卡片 hover 阴影 */
}
```

### 4.2 字体规范

| 用途 | 字号 | 字重 | 字间距 | 行高 | Tailwind 近似 |
|------|------|------|--------|------|---------------|
| 页面主标题 | 18px | 800 (extrabold) | -0.02em | 1.3 | text-[18px] font-extrabold |
| Header 平台名称 | 16px | 800 (extrabold) | -0.02em | 1.3 | text-[16px] font-extrabold |
| Header 副标题 | 10px | 400 | 0.05em | 1.2 | text-[10px] tracking-wider |
| 顶部导航文字 | 13px | 600 (semibold) | 0 | 1.4 | text-[13px] font-semibold |
| Sidebar 导航文字 | 13px | 600 (semibold) | 0 | 1.4 | text-[13px] font-semibold |
| 卡片标题 | 14px | 700 (bold) | 0 | 1.4 | text-[14px] font-bold |
| 指标卡标签 | 10px | 700 (bold) | 0.05em | 1.2 | text-[10px] font-bold tracking-wider uppercase |
| 指标卡主数据 | 24px | 900 (black) | -0.02em | 1.1 | text-[24px] font-black |
| 指标卡单位 | 11px | 700 (bold) | 0 | 1.4 | text-[11px] font-bold |
| 面板标题 | 14px | 700 (bold) | 0 | 1.4 | text-[14px] font-bold |
| 面板副标题 | 11px | 400 | 0 | 1.4 | text-[11px] |
| 表格表头文字 | 10px | 700 (bold) | 0.05em | 1.3 | text-[10px] font-bold tracking-wider uppercase |
| 表格正文 | 12px | 400 | 0 | 1.5 | text-[12px] |
| 按钮文字 | 11px - 13px | 700 (bold) | 0.04em | 1.2 | text-[11px] font-bold tracking-wider |
| Badge / 标签文字 | 10px - 11px | 700 (bold) | 0 | 1.2 | text-[10px] font-bold |
| 辅助说明文字 | 10px | 400 | 0 | 1.4 | text-[10px] |
| 图例文字 | 10px | 500 (medium) | 0 | 1.3 | text-[10px] font-medium |
| 大数字（置信度） | 32px | 900 (black) | 0 | 1.1 | text-[32px] font-black |

默认字体族：`"PingFang SC", "Microsoft YaHei", "Noto Sans SC", Arial, Helvetica, sans-serif`

### 4.3 间距规范

| 用途 | 间距值 | Tailwind 近似 |
|------|--------|---------------|
| 页面内容区 padding | 24px 左右, 20px 上下 | px-6 py-5 |
| Header 内边距 | 24px 左右 | px-6 |
| Header 高度 | 88px - 96px | h-[88px] |
| Sidebar 宽度 | 200px - 220px | w-[200px] |
| Sidebar 导航项内边距 | 12px 左右, 10px 上下 | px-3 py-2.5 |
| 导航项间距 | 4px | gap-1 |
| 指标卡间距 | 12px | gap-3 |
| 面板间距 | 16px | gap-4 |
| 页面区块间距 | 20px | space-y-5 |
| 卡片内边距 | 16px - 20px | p-4 或 p-5 |
| 表格行内边距 | 10px 上下, 12px 左右 | py-2.5 px-3 |
| 图表区内边距 | 0（由图表 margin 控制） | — |
| 按钮内边距 | 6px 上下, 12px - 16px 左右 | py-1.5 px-3 |
| 图标与文字间距 | 6px - 8px | gap-1.5 或 gap-2 |
| 设备卡片内指标间距 | 6px | gap-1.5 |
| 右侧面板内元素间距 | 12px - 16px | space-y-3 或 space-y-4 |

### 4.4 圆角规范

| 用途 | 圆角值 | Tailwind 近似 |
|------|--------|---------------|
| 页面最外层容器 | 12px - 16px | rounded-xl 或 rounded-2xl |
| 卡片 / 面板 | 10px - 12px | rounded-xl |
| 大按钮 | 8px - 10px | rounded-lg 或 rounded-xl |
| 小按钮 / Badge | 6px - 8px | rounded-lg |
| Badge（胶囊型） | 20px（全圆角） | rounded-full |
| 输入框 | 8px | rounded-lg |
| 地图容器 | 10px | rounded-xl |
| 图标占位符 | 8px - 12px | rounded-lg 或 rounded-xl |
| 吉祥物占位符 | 12px - 16px | rounded-xl 或 rounded-2xl |
| 模态框 | 12px | rounded-xl |
| 雷达扫描圆 | 50% | rounded-full |

### 4.5 阴影规范

| 用途 | 阴影值 |
|------|--------|
| 卡片默认 | `0 2px 8px rgba(13, 125, 242, 0.06)` |
| 卡片 hover | `0 4px 16px rgba(13, 125, 242, 0.10)` |
| 浮层 / 弹出框 | `0 4px 16px rgba(13, 125, 242, 0.08)` |
| 主按钮默认 | `0 2px 8px rgba(13, 125, 242, 0.25)` |
| 主按钮 hover | `0 4px 14px rgba(13, 125, 242, 0.35)` |
| 模态框遮罩 | 无阴影，背景 `rgba(11, 37, 64, 0.30)` + backdrop blur |
| 地图控件 | `0 2px 8px rgba(13, 125, 242, 0.06)` |
| Sidebar Logo | `0 2px 8px rgba(22, 184, 216, 0.25)` |

### 4.6 边框规范

| 用途 | 边框样式 |
|------|----------|
| 页面最外层容器 | `1px solid rgba(88, 190, 210, 0.22)` |
| 卡片 / 面板 | `1px solid rgba(88, 190, 210, 0.22)` |
| 卡片 hover | `1px solid rgba(88, 190, 210, 0.40)` |
| 表格行底部 | `1px solid rgba(13, 125, 242, 0.06)` |
| 图表容器 | `1px solid rgba(13, 125, 242, 0.08)` |
| 输入框 | `1px solid rgba(13, 125, 242, 0.15)` |
| 输入框 focus | `1px solid #0D7DF2` |
| 选中态 / 拖拽中卡片 | `2px solid #0D7DF2` |
| 高风险设备卡片 | `1px solid rgba(245, 34, 45, 0.25)` |
| 虚线占位符 | `2px dashed rgba(13, 125, 242, 0.12)` |
| 侧边栏分隔 | `1px solid rgba(13, 125, 242, 0.08)` |
| Header 底部分隔 | `1px solid rgba(13, 125, 242, 0.10)` |

### 4.7 状态色规范

| 状态 | 标签文案 | 圆点色 | 文字色 | 背景色 | Tailwind 参考 |
|------|----------|--------|--------|--------|---------------|
| online | 在线采样 | #08A65A | #08A65A | rgba(8,166,90,0.10) | text-[#08A65A] bg-[rgba(8,166,90,0.1)] |
| idle | 待机 | #F7B500 | #F7B500 | rgba(247,181,0,0.10) | text-[#F7B500] bg-[rgba(247,181,0,0.1)] |
| offline | 离线 | #F5222D | #F5222D | rgba(245,34,45,0.10) | text-[#F5222D] bg-[rgba(245,34,45,0.1)] |
| normal | 正常 | #08A65A | #08A65A | rgba(8,166,90,0.10) | — |
| attention/watch | 关注 | #F7B500 | #F7B500 | rgba(247,181,0,0.10) | — |
| warning | 警戒 | #FF7A00 | #FF7A00 | rgba(255,122,0,0.10) | — |
| danger/critical | 高风险 | #F5222D | #F5222D | rgba(245,34,45,0.10) | — |

### 4.8 插画和吉祥物规范

**插画风格：**
- 线条简洁、柔和的手绘/扁平风格
- 蓝色系为主调，搭配薄荷绿和珊瑚红点缀
- 主题围绕：水体、藻类、浮标、实验器材（烧瓶、显微镜）、水生物
- 不使用 3D 渲染、强霓虹、赛博朋克风格

**出现位置（占位符）：**
- Header 右上角：小吉祥物（约 84px × 84px）
- Sidebar 底部：大吉祥物 + 水草气泡装饰（约 160px × 220px）
- 总览页内容区：不额外放置，仅使用全局装饰
- 地图页右侧面板底部：设备插画（约 120px × 100px）
- 数据分析页左下角：显微镜/实验器材插画（约 180px × 160px）
- 设备页右侧面板底部：实验器材小插画（约 100px × 120px）

**占位符通用规则：**
- 占位符必须拥有与最终图片完全相同的宽高
- 占位符显示浅蓝半透明背景 + 虚线边框 + 居中文字标注
- 占位符不得遮挡任何数据内容
- 占位符 opacity 不超过 0.6，视觉上不喧宾夺主
- 暂无真实图片时必须使用占位符参与正常排版，不得导致布局塌陷
- 素材目录 `Materials/` 当前为空，所有图片和图标路径均先指向占位符组件

---

## 5. 全局布局规范

### 设计基准

- **基准分辨率**：1536px × 960px（桌面端 Dashboard 典型尺寸）
- **最佳体验范围**：1280px - 1600px 宽度
- **最小支持宽度**：1024px（小屏纵向堆叠）

### 5.1 PageFrame（页面最外层容器）

- **组件名称**：`PageFrame`（在 AppShell 中渲染）
- **位置**：包裹整个应用内容（Header + Sidebar + MainContent）
- **宽度**：100vw，最大宽度无上限（背景渐变覆盖全屏）
- **最小高度**：100vh
- **背景**：`linear-gradient(170deg, #F8FEFF 0%, #EAF8FF 40%, #EDFBF7 100%)`
- **装饰伪元素**：固定定位的径向渐变光斑（蓝色和绿色），不响应滚轮
  - 左下：`radial-gradient(ellipse 80% 50% at 20% 80%, rgba(13,125,242,0.04) 0%, transparent 70%)`
  - 右上：`radial-gradient(ellipse 60% 40% at 80% 20%, rgba(8,166,90,0.03) 0%, transparent 60%)`
- **z-index**：0
- **不包含**：外层页面圆角边框（如有设计蓝图需要，在 AppShell 内部加 .page-border）

### 5.2 AppHeader（顶部品牌导航栏）

- **组件名称**：`AppHeader`
- **文件路径**：`src/layouts/AppHeader.tsx`
- **位置**：页面顶部，sticky 定位
- **高度**：88px - 96px（推荐 88px）
- **背景**：`rgba(255, 255, 255, 0.80)` + `backdrop-filter: blur(16px)`
- **底边框**：`1px solid rgba(13, 125, 242, 0.10)`
- **z-index**：50
- **内部布局**：flex row, align-items: center, justify-content: space-between
- **内边距**：左右 24px (px-6)

**左侧 Logo 区域：**
- 宽度：约 220px（与 Sidebar 宽度对齐）
- 内容：
  - Logo 圆形占位符：40px × 40px，蓝色渐变背景，内含水滴 SVG 图标
  - 标题组（垂直排列）：
    - 主标题：`水体藻毒素监测平台`，16px，extrabold，color #0B2540
    - 副标题：`Water Algal Toxin Monitoring`，10px，tracking-wider，color #5A7184
- Logo 与标题间距：12px

**中部导航区：**
- 位置：Header 水平居中
- 显示：4 个横向导航胶囊按钮（桌面端显示，移动端隐藏）
- 样式：默认文字 #5A7184，hover 文字 #0D7DF2 + 浅蓝底
- 激活态：文字 #0D7DF2，背景 rgba(13,125,242,0.10)，圆角 20px
- 导航项内边距：6px 上下, 14px 左右
- 导航项间距：6px
- 导航项文字：13px，semibold

**右侧用户区：**
- 内容：
  - 通知按钮：32px × 32px 圆形按钮，浅蓝边框，内含铃铛 SVG
  - 团队选择器：`iGEM Team` 文字 + 下拉箭头，浅蓝底胶囊
- 元素间距：12px
- 右上角吉祥物占位符：84px × 84px（位于 Header 右上角外侧或内部最右侧）

### 5.3 SidebarNav（左侧垂直导航栏）

- **组件名称**：`SidebarNav`
- **文件路径**：`src/layouts/SidebarNav.tsx`
- **位置**：Header 下方，左侧固定
- **宽度**：200px - 220px（推荐 200px）
- **高度**：calc(100vh - 88px)（Header 下方到页面底部）
- **背景**：`rgba(255, 255, 255, 0.60)` + `backdrop-filter: blur(12px)`
- **右边框**：`1px solid rgba(13, 125, 242, 0.08)`
- **z-index**：40
- **显示条件**：lg 屏幕及以上显示，小屏隐藏

**导航列表区：**
- 顶部起始位置：距 Sidebar 顶部 20px
- 导航项结构（共 4 项）：
  - 总览（icon: 房子/首页 SVG）
  - 地图监视（icon: 地图/定位 SVG）
  - 数据分析（icon: 图表/柱状图 SVG）
  - 设备配对（icon: 芯片/设备 SVG）
- 每个导航项：
  - 高度：40px - 44px
  - 内边距：10px 上下, 12px 左右
  - 圆角：8px
  - 导航项间距：4px
  - 内容：左侧 SVG 图标（18px × 18px）+ 右侧文字（13px semibold）
  - 图标与文字间距：10px

**导航激活态：**
- 左侧 3px 宽蓝色指示条（#0D7DF2），圆角右侧，垂直居中
- 背景：rgba(13, 125, 242, 0.10)
- 文字颜色：#0D7DF2
- 图标 strokeWidth 从 1.5 变为 2

**底部装饰区：**
- 位置：Sidebar 底部，mt-auto
- 内容（从上到下）：
  - 水草/气泡 CSS 动画装饰（opacity 0.2 - 0.3）
  - 大吉祥物占位符：160px × 220px
- 占位符样式：虚线边框、浅蓝底、居中文字
- 内边距：12px 左右, 16px 下

### 5.4 MainContent（主内容区）

- **组件名称**：`MainContent`（在 AppShell 中渲染为 `<main>`）
- **位置**：Header 下方，Sidebar 右侧
- **定位**：flex-1，overflow-y: auto
- **内边距**：24px 左右 (px-6), 20px 上下 (py-5)
- **底部内边距**：48px (pb-12)
- **z-index**：10
- **最大宽度**：无上限，内容自适应
- **滚动规则**：垂直滚动（主要内容区滚动，Header 和 Sidebar 固定）

### 5.5 全局装饰元素总表

| 元素名称 | 推荐文件名 | 放置路径 | 页面位置 | 宽度 | 高度 | z-index | 是否可点击 | 缺失 fallback |
|----------|-----------|----------|----------|------|------|---------|------------|--------------|
| Header Logo 圆形图标 | logo-ocean-placeholder | Materials/General/ | Header 左侧 | 40px | 40px | — | 否 | 蓝色渐变圆形 + 水滴 SVG |
| Header 小吉祥物 | header-mascot-placeholder | Materials/General/ | Header 右上角 | 84px | 84px | — | 否 | 虚线框 + "萌物占位" |
| 通知图标 | notification-icon-placeholder | Materials/General/ | Header 右侧通知按钮内 | 16px | 16px | — | 是（铃铛按钮） | SVG 铃铛图标 |
| Sidebar 大吉祥物 | sidebar-mascot-placeholder | Materials/General/ | Sidebar 底部 | 160px | 220px | — | 否 | 虚线框 + "萌物占位\n藻类实验助手" |
| 气泡装饰 | bubble-decoration-placeholder | Materials/General/ | Sidebar 底部水区上方 | 各 8px-16px | 各 8px-16px | — | 否 | CSS 圆形 + 动画 |
| 水波装饰 | wave-decoration-placeholder | Materials/General/ | 页面背景 | 100% | 40px | 0 | 否 | CSS 渐变模拟 |
| Sidebar 水草装饰 | water-plant-decoration | Materials/General/ | Sidebar 底部 | 40px | 40px-64px | — | 否 | CSS 圆角矩形条 |
| 页面背景光斑 | — | — (CSS 实现) | 页面背景固定定位 | — | — | 0 | 否 | 径向渐变（CSS） |

---

## 6. 页面元素级规格总表

### 总览页 (OverviewPage: /)

| 页面 | 元素层级 | 元素名称 | 推荐组件名 | 推荐代码变量/id | 所属父元素 | 页面位置 | 与相邻元素关系 | 推荐宽度 | 推荐高度 | 内边距 | 外边距 | 数据来源 | 功能说明 | 交互说明 | 状态说明 | 是否需要图片/图标 | 占位符名称 | 占位符尺寸 | 素材未来路径 | 缺失 fallback |
|------|----------|----------|------------|-----------------|-----------|----------|--------------|----------|----------|--------|--------|----------|----------|----------|----------|-----------------|-----------|----------|-------------|--------------|
| 总览 | AppShell | 页面壳 | AppShell | app-shell | body | 全页 | 包裹所有内容 | 100vw | 100vh | 0 | 0 | — | 全局布局容器 | 无 | — | 否 | — | — | — | — |
| 总览 | AppHeader | 顶部导航 | AppHeader | app-header | AppShell | 页面顶部 | sticky top-0 | 100% | 88px | px-6 | 0 | — | 品牌展示+导航 | 导航项点击跳转 | 激活态高亮 | 是 | logo-ocean, mascot-header | Logo 40×40, Mascot 84×84 | Materials/General/ | 蓝色渐变圆形+SVG |
| 总览 | SidebarNav | 侧边导航 | SidebarNav | sidebar-nav | AppShell | 左侧 | Header下方 | 200px | calc(100vh-88px) | px-3 py-5 | 0 | — | 页面导航 | 导航项点击跳转 | 总览高亮 | 是 | nav-icons, sidebar-mascot | 图标18×18, 吉祥物160×220 | Materials/General/ | SVG图标+虚线占位 |
| 总览 | MainContent | 主内容区 | MainContent | main-content | AppShell | 右侧 | Sidebar右侧 | flex-1 | auto | px-6 py-5 pb-12 | 0 | — | 承载页面内容 | 滚动 | — | 否 | — | — | — | — |
| 总览 | 指标卡行 | 在线设备卡 | MetricSummaryCard | metric-card-online | MainContent | 内容区顶部第1行 | 5列网格，列间距12px | 1fr (约280px) | 88px-96px | p-4 | 0 | demoSummary.onlineDevices | 展示在线设备数量 | hover卡片边框加深 | 正常 | 是 | overview-online-icon | 40px×40px | Materials/Overview/ | aqua-card+SVG图标+文字 |
| 总览 | 指标卡行 | 空闲设备卡 | MetricSummaryCard | metric-card-idle | MainContent | 内容区顶部第1行 | 在线设备卡右侧12px | 1fr (约280px) | 88px-96px | p-4 | 0 | demoReadings filter idle | 展示空闲设备数量 | hover卡片边框加深 | 关注 | 是 | overview-idle-icon | 40px×40px | Materials/Overview/ | aqua-card+SVG图标+文字 |
| 总览 | 指标卡行 | 离线设备卡 | MetricSummaryCard | metric-card-offline | MainContent | 内容区顶部第1行 | 空闲设备卡右侧12px | 1fr (约280px) | 88px-96px | p-4 | 0 | demoReadings filter offline | 展示离线设备数量 | hover卡片边框加深 | 危险 | 是 | overview-offline-icon | 40px×40px | Materials/Overview/ | aqua-card+SVG图标+文字 |
| 总览 | 指标卡行 | 平均藻毒素卡 | MetricSummaryCard | metric-card-avg-toxin | MainContent | 内容区顶部第1行 | 离线设备卡右侧12px | 1fr (约280px) | 88px-96px | p-4 | 0 | demoSummary.averageToxinUgL | 展示平均藻毒素浓度 | hover卡片边框加深 | 按数值变色 | 是 | overview-average-toxin-icon | 40px×40px | Materials/Overview/ | aqua-card+SVG图标+文字 |
| 总览 | 指标卡行 | 最高风险卡 | MetricSummaryCard | metric-card-max-risk | MainContent | 内容区顶部第1行 | 平均藻毒素卡右侧12px | 1fr (约280px) | 88px-96px | p-4 | 0 | demoSummary.maxToxinReading | 展示最高风险设备信息 | hover卡片边框加深 | 红色强调 | 是 | overview-risk-icon | 40px×40px | Materials/Overview/ | aqua-card+SVG图标+文字 |
| 总览 | 中部左侧面板 | 系统状态面板 | SystemStatusPanel | system-status-panel | MainContent | 内容区中部第2行左侧 | 3列网格第1列 | 1fr (约490px) | 260px-280px | p-5 | gap-4 | demoSummary | 展示系统整体运行状态 | 无 | 正常/异常 | 是 | overview-system-shield-icon | 56px×56px | Materials/Overview/ | 盾牌SVG+文字状态 |
| 总览 | 中部中间面板 | 告警摘要面板 | AlertSummaryPanel | alert-summary-panel | MainContent | 内容区中部第2行中间 | 3列网格第2列，左侧面板右16px | 1fr (约490px) | 260px-280px | p-5 | gap-4 | demoReadings风险统计 | 4行告警列表 | 点击行可跳转 | 各行颜色不同 | 是 | overview-alert-icon | 内嵌图标14×14 | Materials/Overview/ | 颜色条+数字+箭头 |
| 总览 | 中部右侧面板 | 趋势概览面板 | OverviewTrendChart | overview-trend-chart | MainContent | 内容区中部第2行右侧 | 3列网格第3列，中间面板右16px | 1fr (约490px) | 260px-280px | p-5 | gap-4 | demoDeviceHistory聚合7天 | Recharts面积图+折线 | hover tooltip | 阈值线变色 | 否 | — | — | — | Recharts AreaChart |
| 总览 | 底部表格 | 最新采样表格 | LatestReadingsTable | latest-readings-table | MainContent | 内容区底部第3行 | 趋势面板下方20px | 100% | auto | p-5 | mt-5 | demoReadings前5条 | 7列表格展示最新数据 | "查看全部"按钮跳转/map | 行hover高亮 | 否 | — | — | — | HTML table+状态圆点 |
| 总览 | 表格内 | "查看全部"按钮 | AppButton | btn-view-all | LatestReadingsTable header-right | 表格面板右上角 | 面板标题右侧 | auto | 32px | py-1 px-3 | 0 | — | 跳转到地图页 | click跳转/map | hover阴影加深 | 是 | 右箭头SVG | 12px×12px | — | SVG箭头图标 |

### 地图监视页 (MapMonitorPage: /map)

| 页面 | 元素层级 | 元素名称 | 推荐组件名 | 推荐代码变量/id | 所属父元素 | 页面位置 | 与相邻元素关系 | 推荐宽度 | 推荐高度 | 内边距 | 外边距 | 数据来源 | 功能说明 | 交互说明 | 状态说明 | 是否需要图片/图标 | 占位符名称 | 占位符尺寸 | 素材未来路径 | 缺失 fallback |
|------|----------|----------|------------|-----------------|-----------|----------|--------------|----------|----------|--------|--------|----------|----------|----------|----------|-----------------|-----------|----------|-------------|--------------|
| 地图 | 地图+详情容器 | 主内容布局 | — | map-page-layout | MainContent | 内容区 | 2列: 1fr + 340px | 100% | auto | 0 | gap-4 | — | 左右分栏布局 | 无 | — | 否 | — | — | — | — |
| 地图 | 地图主面板 | 湖泊风险地图 | LakeRiskMap | lake-risk-map | 地图+详情容器 | 左侧主列 | 占左侧1fr | 1fr | 720px | p-2.5 | 0 | demoReadings | Leaflet地图+热力+设备点 | 点击设备点选中等 | 加载中/加载完成/无数据 | 是 | map-marker系列 | marker 36×48 | Materials/Map/ | Leaflet CircleMarker |
| 地图 | 地图内控件 | 图层切换按钮组 | MapLayerToggle | map-layer-toggle | LakeRiskMap (绝对定位) | 地图顶部居中 | 距顶部20px | auto | 36px | p-1 | 0 | showDevices/showHeat state | 切换设备图层/热力图层 | 点击切换激活态 | 激活/未激活 | 是 | map-layer-icon | 16px×16px | Materials/Map/ | 胶囊按钮文字 |
| 地图 | 地图内控件 | 居中选择按钮 | — | btn-locate | LakeRiskMap (绝对定位) | 地图右上角 | 距顶部20px, 距右侧20px | 32px | 32px | 0 | 0 | — | 地图居中定位 | click | hover变色 | 是 | map-location-icon | 16px×16px | Materials/Map/ | SVG十字准星 |
| 地图 | 地图内控件 | 缩放按钮 | — | map-zoom-control | LakeRiskMap (Leaflet默认) | 地图左上角 | 距左上角10px | 32px | 64px | 0 | 0 | — | 地图缩放 | Leaflet原生 | — | 否 | — | — | — | Leaflet自带 |
| 地图 | 地图底部 | 风险图例 | RiskLegend | risk-legend | LakeRiskMap (绝对定位) | 地图底部居中 | 距底部20px | auto (约460px) | 36px-40px | px-4 py-2 | 0 | 固定风险等级定义 | 展示4级风险颜色+范围 | 无（静态展示） | — | 否（CSS色块） | — | 色块10×10 | — | CSS圆点 |
| 地图 | 右侧面板 | 选中设备详情 | SelectedDevicePanel | selected-device-panel | 地图+详情容器 | 右侧固定栏 | 地图面板右侧16px | 340px | auto (min:720px) | p-4 | 0 | selectedReading | 展示选中设备全部信息 | 查看历史数据按钮 | 默认选中最高风险设备 | 是 | map-selected-device-illustration | 120px×100px | Materials/Map/ | 6项指标网格+设备类型 |
| 地图 | 右侧面板底部 | 设备插画占位 | ImagePlaceholder | map-device-illustration | SelectedDevicePanel | 右侧面板底部 | 详情信息下方 | 100% | 100px-120px | p-3 | mt-2 | — | 装饰占位 | 无 | — | 是 | map-bottom-mascot-placeholder | 填充宽度×100px | Materials/Map/ | 虚线框+"设备插画占位" |

### 数据分析页 (DataAnalysisPage: /data)

| 页面 | 元素层级 | 元素名称 | 推荐组件名 | 推荐代码变量/id | 所属父元素 | 页面位置 | 与相邻元素关系 | 推荐宽度 | 推荐高度 | 内边距 | 外边距 | 数据来源 | 功能说明 | 交互说明 | 状态说明 | 是否需要图片/图标 | 占位符名称 | 占位符尺寸 | 素材未来路径 | 缺失 fallback |
|------|----------|----------|------------|-----------------|-----------|----------|--------------|----------|----------|--------|--------|----------|----------|----------|----------|-----------------|-----------|----------|-------------|--------------|
| 数据 | 筛选栏 | 数据分析筛选栏 | DataFilterBar | data-filter-bar | MainContent | 内容区第1行 | 全宽 | 100% | 48px-52px | px-4 py-3 | mb-4 | FilterState | 时间/设备/传感器筛选+导出 | 下拉选择筛选条件 | — | 是 | data-export-icon | 14px×14px | Materials/Data/ | aqua-panel+select+button |
| 数据 | 趋势+对比容器 | 第2行布局 | — | data-row-2 | MainContent | 筛选栏下方 | 2列: 1fr + 300px | 100% | auto | 0 | gap-4 | — | 趋势图+传感器对比 | 无 | — | 否 | — | — | — | — |
| 数据 | 左侧趋势图 | 多指标趋势图 | MultiMetricTrendChart | multi-metric-trend-chart | data-row-2 | 左侧主列 | 占1fr | 1fr | 320px (图表区) | p-5 | 0 | demoDeviceHistory聚合7天 | Recharts多线图+阈值线 | hover tooltip | 异常点红色警告 | 是 | data-trend-warning-icon | 14px×14px (异常标记) | Materials/Data/ | Recharts LineChart |
| 数据 | 右侧对比面板 | 传感器对比面板 | SensorComparisonPanel | sensor-comparison-panel | data-row-2 | 右侧300px列 | 趋势图右16px | 300px | 与趋势图等高 | p-5 | 0 | demoReadings按toxin排序 | 设备列表+毒素值排序 | 无（静态列表） | 各行颜色按风险等级 | 否 | — | 色块8×8 (列表圆点) | — | aqua-panel+列表 |
| 数据 | AI预测模块 | AI预测面板 | ToxinPredictionPanel | toxin-prediction-panel | MainContent | 内容区第3行 | 趋势图下方16px | 100% | auto | 0 | mt-4 | predictionData (useMemo生成) | 2列: 1fr + 260px | 无 | — | 是 | data-prediction-icon, data-confidence-icon | 16px×16px | Materials/Data/ | — |
| 数据 | AI预测左侧图 | 预测图表区 | — | prediction-chart | ToxinPredictionPanel | 左侧 | 1fr | 1fr | 280px (图表区) | p-5 | 0 | predictionData | 历史+预测+置信区间AreaChart | hover tooltip | 预测线虚线 | 否 | — | — | — | Recharts AreaChart |
| 数据 | AI预测右侧摘要 | 模型置信度卡 | — | model-confidence-card | ToxinPredictionPanel | 右侧 | 260px | auto | p-5 | 0 | 固定演示值 | 置信度87%/预测区间/高风险时间 | 无（静态展示） | 预警红色卡片 | 是 | data-confidence-icon | 16px×16px | Materials/Data/ | aqua-panel+文字 |
| 数据 | 左下装饰 | 显微镜占位 | ImagePlaceholder | data-microscope-placeholder | MainContent或Sidebar | 数据分析页左下角 | 不遮挡数据 | 180px | 160px | 0 | 0 | — | 实验器材装饰 | 无 | — | 是 | data-sidebar-microscope-placeholder | 180px×160px | Materials/Data/ | 虚线框+"显微镜占位" |
| 数据 | 背景装饰 | 水波装饰 | — | data-wave-deco | MainContent | 数据分析页底部 | z-index:0 | 100% | 40px | 0 | 0 | — | CSS水波装饰 | 无 | — | 否（CSS实现） | — | — | — | CSS渐变/阴影 |

### 设备配对页 (DevicePairingPage: /device)

| 页面 | 元素层级 | 元素名称 | 推荐组件名 | 推荐代码变量/id | 所属父元素 | 页面位置 | 与相邻元素关系 | 推荐宽度 | 推荐高度 | 内边距 | 外边距 | 数据来源 | 功能说明 | 交互说明 | 状态说明 | 是否需要图片/图标 | 占位符名称 | 占位符尺寸 | 素材未来路径 | 缺失 fallback |
|------|----------|----------|------------|-----------------|-----------|----------|--------------|----------|----------|--------|--------|----------|----------|----------|----------|-----------------|-----------|----------|-------------|--------------|
| 设备 | 工具栏 | 设备操作工具栏 | DeviceToolbar | device-toolbar | MainContent | 内容区第1行 | 全宽 | 100% | 36px-40px | 0 | mb-4 | 本地state | 添加/刷新/批量操作按钮 | 按钮点击 | — | 是 | device-add-icon, device-refresh-icon | 14px×14px | Materials/Drive/ | aqua-button系列 |
| 设备 | 内容布局 | 卡片+面板容器 | — | device-content-layout | MainContent | 工具栏下方 | 2列: 1fr + 300px | 100% | auto | 0 | gap-4 | — | 设备卡片区+配对面板 | 无 | — | 否 | — | — | — | — |
| 设备 | 设备卡片网格 | 设备卡片网格 | DeviceCardGrid | device-card-grid | device-content-layout | 左侧主列 | 占1fr | 1fr | auto | 0 | 0 | devices state (DeviceItem[]) | 3列卡片网格+拖拽排序 | 拖拽排序 | 拖拽中蓝色边框 | 否 | — | — | — | DndContext+SortableContext |
| 设备 | 单张设备卡片 | 设备卡片 | DeviceCard | device-card-{id} | DeviceCardGrid | 网格内 | 3列, 列间距12px, 行间距12px | 300px-330px | 230px-260px | p-3 | 0 | DeviceItem | 设备信息+操作按钮 | 详情/编辑/删除/连接/断开 | online/idle/offline/high-risk | 是 | device-card-buoy, device-card-probe, device-card-offline | 40px×40px (设备图标) | Materials/Drive/ | aqua-card+指标网格 |
| 设备 | 设备卡片-插画区 | 设备插画占位 | ImagePlaceholder | device-illustration-{id} | DeviceCard | 卡片左上 | 设备名左侧 | 40px | 40px | 0 | 0 | — | 设备类型视觉区分 | 无 | — | 是 | device-card-buoy-placeholder | 40px×40px | Materials/Drive/ | 虚线框+设备SVG |
| 设备 | 设备卡片-状态区 | 状态圆点+文字 | StatusBadge | status-badge-{id} | DeviceCard | 卡片上部 | 设备名下方 | auto | 18px-20px | px-2 py-0.5 | 0 | device.status | 设备状态展示 | 无 | 在线=绿闪烁, 待机=黄, 离线=红 | 否 | — | 圆点6px×6px | — | 彩色圆点+文字 |
| 设备 | 设备卡片-连接图标 | WiFi/蓝牙图标 | — | conn-icon-{id} | DeviceCard | 卡片右上角 | 状态文字右侧 | 14px | 14px | 0 | 0 | device.connectionType | 连接方式图标 | 无 | wifi=绿, bluetooth=蓝 | 是 | device-wifi-icon, device-bluetooth-icon | 14px×14px | Materials/Drive/ | SVG WiFi/蓝牙图标 |
| 设备 | 设备卡片-指标区 | 三列指标 | — | metrics-grid-{id} | DeviceCard | 卡片中部 | 设备状态下方 | 100% | 60px-70px | p-1.5 | mb-2 | device.toxinUgL/waterTempC/ph | 藻毒素/水温/pH | 无 | 藻毒素按风险变色 | 否 | — | — | — | 3列grid+数值+单位 |
| 设备 | 设备卡片-电量信号 | 电量+信号行 | — | battery-signal-{id} | DeviceCard | 指标区下方 | 指标行下方 | 100% | 16px | px-1 | mb-2 | device.battery/signalDbm | 电量和信号展示 | 无 | 低电量红, 弱信号黄 | 否 | — | — | — | 文字+颜色 |
| 设备 | 设备卡片-操作区 | 详情/编辑/删除按钮 | — | card-actions-{id} | DeviceCard | 卡片底部 | mt-auto | 100% | 32px-36px | 0 | 0 | — | 设备操作入口 | 按钮点击→弹窗/状态变更 | hover变色 | 是 | device-drag-icon | 12px×12px | Materials/Drive/ | AppButton+编辑/删除图标 |
| 设备 | 设备卡片-拖拽手柄 | 拖拽手柄 | — | drag-handle-{id} | DeviceCard | 卡片顶部居中 | 绝对定位 | 32px | 4px | 0 | 0 | — | 拖拽触发点 | 拖拽 | hover变色 | 否 | — | 圆角矩形条 | — | CSS圆角矩形 |
| 设备 | 拖拽提示区 | 拖拽排序提示 | DeviceSortDropZone | device-sort-drop-zone | device-content-layout (左侧列) | 设备网格下方 | 网格下方12px | 100% | 40px-48px | p-2.5 | mt-3 | — | 拖拽操作说明 | 无 | — | 否 | — | — | — | 虚线框+"拖拽设备卡片可调整顺序" |
| 设备 | 右侧配对面板 | 配对扫描面板 | PairingPanel | pairing-panel | device-content-layout | 右侧300px列 | 左侧网格右16px | 300px | auto | p-4 | 0 | DISCOVERED_DEVICES, isScanning | 扫描/配对/添加设备 | 扫描/配对按钮 | 扫描中/扫描完成 | 是 | device-scan-bluetooth, device-lab-flask | 蓝牙72×72, 器材100×120 | Materials/Drive/ | aqua-panel+雷达圆环 |
| 设备 | 配对面板-雷达 | 雷达扫描圆环 | — | scan-radar | PairingPanel | 面板上部居中 | 标题下方 | 112px | 112px | 0 | mx-auto | isScanning | 扫描动画 | 无 | 扫描中=旋转ping | 是 | device-scan-bluetooth-placeholder | 36px×36px (中心图标) | Materials/Drive/ | 3层CSS圆形+蓝牙SVG |
| 设备 | 配对面板-发现列表 | 已发现设备列表 | DiscoveredDeviceItem | discovered-device-{name} | PairingPanel | 雷达下方 | 扫描按钮下方 | 100% | 每项48px-56px | p-2.5 | 项间距8px | DISCOVERED_DEVICES | 发现设备+RSSI+配对按钮 | 配对按钮点击 | — | 否 | — | — | — | aqua-card+按钮 |
| 设备 | 配对面板-底部装饰 | 实验器材占位 | ImagePlaceholder | device-lab-flask-placeholder | PairingPanel | 面板底部 | 发现列表下方 | 100px | 120px | 0 | mt-auto | — | 装饰占位 | 无 | — | 是 | device-lab-flask-placeholder | 100px×120px | Materials/Drive/ | 虚线框+"实验器材占位" |

---

## 7. 图片与图标占位符总表

### 7.1 通用 (General)

| 页面 | 占位符名称 | 推荐素材文件名 | 未来素材路径 | 类型 | 用途 | 页面位置 | 所属组件 | 推荐宽度 | 推荐高度 | 是否保持比例 | 是否透明背景 | 当前占位符样式 | 缺失 fallback 文案 | 备注 |
|------|-----------|---------------|-------------|------|------|----------|----------|----------|----------|------------|------------|--------------|-----------------|------|
| 通用 | logo-ocean-placeholder | logo-ocean.png | Materials/General/ | logo | 平台 Logo | Header 左侧 | AppHeader | 40px | 40px | 是 | 否 | 蓝色渐变圆形+水滴SVG | "Logo" | 圆形 |
| 通用 | header-user-avatar-placeholder | user-avatar-default.png | Materials/General/ | icon | 用户头像 | Header 右侧 | AppHeader | 28px | 28px | 是 | 否 | 浅蓝圆形+人形SVG | — | 暂不需要，团队选择器文字替代 |
| 通用 | notification-icon-placeholder | notification-bell.svg | Materials/General/ | icon | 通知铃铛 | Header 右侧通知按钮 | AppHeader | 16px | 16px | 是 | 是 | 内联SVG铃铛图标 | "通知" | 功能按钮图标 |
| 通用 | nav-overview-icon-placeholder | nav-overview.svg | Materials/General/ | icon | 总览导航图标 | Sidebar 导航列表第1项 | SidebarNav | 18px | 18px | 是 | 是 | SVG房子图标 | — | 导航图标 |
| 通用 | nav-map-icon-placeholder | nav-map.svg | Materials/General/ | icon | 地图导航图标 | Sidebar 导航列表第2项 | SidebarNav | 18px | 18px | 是 | 是 | SVG地图图标 | — | 导航图标 |
| 通用 | nav-data-icon-placeholder | nav-data.svg | Materials/General/ | icon | 数据分析导航图标 | Sidebar 导航列表第3项 | SidebarNav | 18px | 18px | 是 | 是 | SVG图表图标 | — | 导航图标 |
| 通用 | nav-device-icon-placeholder | nav-device.svg | Materials/General/ | icon | 设备配对导航图标 | Sidebar 导航列表第4项 | SidebarNav | 18px | 18px | 是 | 是 | SVG设备图标 | — | 导航图标 |
| 通用 | bubble-decoration-placeholder | — | — (CSS) | decoration | 气泡装饰 | Sidebar 底部 | SidebarNav | 8px-16px | 8px-16px | 是 | 是 | CSS圆形+动画 | — | CSS实现 |
| 通用 | wave-decoration-placeholder | — | — (CSS) | decoration | 水波装饰 | 页面背景 | AppShell | 100% | 40px | 否 | 是 | CSS渐变 | — | CSS实现 |
| 通用 | header-mascot-placeholder | header-mascot.png | Materials/General/ | mascot | Header 吉祥物 | Header 右上角 | AppHeader | 84px | 84px | 是 | 是 | 虚线框+文字 | "萌物占位" | 小吉祥物 |
| 通用 | sidebar-mascot-placeholder | sidebar-mascot.png | Materials/General/ | mascot | Sidebar 大吉祥物 | Sidebar 底部 | SidebarNav | 160px | 220px | 是 | 是 | 虚线框+文字 | "萌物占位\n藻类实验助手" | 大吉祥物 |

### 7.2 总览页 (Overview)

| 页面 | 占位符名称 | 推荐素材文件名 | 未来素材路径 | 类型 | 用途 | 页面位置 | 所属组件 | 推荐宽度 | 推荐高度 | 是否保持比例 | 是否透明背景 | 当前占位符样式 | 缺失 fallback 文案 | 备注 |
|------|-----------|---------------|-------------|------|------|----------|----------|----------|----------|------------|------------|--------------|-----------------|------|
| 总览 | overview-system-shield-icon-placeholder | system-shield.svg | Materials/Overview/ | status-icon | 系统状态盾牌图标 | 系统状态面板居中 | SystemStatusPanel | 56px | 56px | 是 | 是 | 圆形浅绿底+盾牌勾SVG | "运行正常" | 可复用StatusBadge逻辑 |
| 总览 | overview-online-icon-placeholder | icon-online.svg | Materials/Overview/ | icon | 在线设备图标 | 在线设备指标卡 | MetricSummaryCard | 40px | 40px | 是 | 是 | 圆形浅绿底+WiFi SVG | "在线" | 指标卡左侧圆形图标 |
| 总览 | overview-idle-icon-placeholder | icon-idle.svg | Materials/Overview/ | icon | 空闲设备图标 | 空闲设备指标卡 | MetricSummaryCard | 40px | 40px | 是 | 是 | 圆形浅黄底+时钟 SVG | "空闲" | 指标卡左侧圆形图标 |
| 总览 | overview-offline-icon-placeholder | icon-offline.svg | Materials/Overview/ | icon | 离线设备图标 | 离线设备指标卡 | MetricSummaryCard | 40px | 40px | 是 | 是 | 圆形浅红底+叉号 SVG | "离线" | 指标卡左侧圆形图标 |
| 总览 | overview-average-toxin-icon-placeholder | icon-toxin.svg | Materials/Overview/ | icon | 藻毒素图标 | 平均藻毒素指标卡 | MetricSummaryCard | 40px | 40px | 是 | 是 | 圆形浅蓝底+水滴 SVG | "藻毒素" | 指标卡左侧圆形图标 |
| 总览 | overview-risk-icon-placeholder | icon-risk.svg | Materials/Overview/ | icon | 风险警告图标 | 最高风险指标卡 | MetricSummaryCard | 40px | 40px | 是 | 是 | 圆形浅红底+警告三角 SVG | "风险" | 指标卡左侧圆形图标 |
| 总览 | overview-alert-icon-placeholder | icon-alert.svg | Materials/Overview/ | icon | 告警箭头图标 | 告警摘要各行 | AlertSummaryPanel | 14px | 14px | 是 | 是 | SVG右箭头 | ">" | 列表行末尾箭头 |

### 7.3 地图监视页 (Map)

| 页面 | 占位符名称 | 推荐素材文件名 | 未来素材路径 | 类型 | 用途 | 页面位置 | 所属组件 | 推荐宽度 | 推荐高度 | 是否保持比例 | 是否透明背景 | 当前占位符样式 | 缺失 fallback 文案 | 备注 |
|------|-----------|---------------|-------------|------|------|----------|----------|----------|----------|------------|------------|--------------|-----------------|------|
| 地图 | map-header-mascot-placeholder | map-mascot.png | Materials/Map/ | mascot | 地图页吉祥物 | Header 右上角 | AppHeader | 84px | 84px | 是 | 是 | 同通用header-mascot | 同通用 | 与通用共用 |
| 地图 | map-marker-normal-placeholder | marker-normal.svg | Materials/Map/ | map-marker | 正常设备点位 | 地图Leaflet图层 | LakeRiskMap | 20px | 20px | 是 | 是 | CSS CircleMarker 绿色 #08A65A | 绿色圆形marker | Leaflet CircleMarker/CSS icon |
| 地图 | map-marker-attention-placeholder | marker-attention.svg | Materials/Map/ | map-marker | 关注设备点位 | 地图Leaflet图层 | LakeRiskMap | 20px | 20px | 是 | 是 | CSS CircleMarker 黄色 #F7B500 | 黄色圆形marker | — |
| 地图 | map-marker-warning-placeholder | marker-warning.svg | Materials/Map/ | map-marker | 警戒设备点位 | 地图Leaflet图层 | LakeRiskMap | 20px | 20px | 是 | 是 | CSS CircleMarker 橙色 #FF7A00 | 橙色圆形marker | — |
| 地图 | map-marker-danger-placeholder | marker-danger.svg | Materials/Map/ | map-marker | 高风险设备点位 | 地图Leaflet图层 | LakeRiskMap | 20px | 20px | 是 | 是 | CSS CircleMarker 红色 #F5222D | 红色圆形marker | — |
| 地图 | map-selected-device-illustration-placeholder | device-illustration.png | Materials/Map/ | device-illustration | 选中设备插画 | 右侧面板底部 | SelectedDevicePanel | 120px | 100px | 是 | 是 | 虚线框+文字 | "设备插画占位" | 设备外观示意 |
| 地图 | map-bottom-mascot-placeholder | map-bottom-mascot.png | Materials/Map/ | mascot | 地图页底部吉祥物 | 右侧面板底部 | SelectedDevicePanel | 120px | 100px | 是 | 是 | 虚线框+文字 | "萌物占位" | 可合并到device-illustration |
| 地图 | map-layer-icon-placeholder | layer-icon.svg | Materials/Map/ | icon | 图层切换图标 | 地图顶部居中按钮内 | MapLayerToggle | 14px | 14px | 是 | 是 | SVG图层图标 | — | 按钮内嵌图标 |
| 地图 | map-location-icon-placeholder | location-icon.svg | Materials/Map/ | icon | 居中定位图标 | 地图右上角定位按钮 | LakeRiskMap | 16px | 16px | 是 | 是 | SVG十字准星图标 | — | 居中按钮图标 |

### 7.4 数据分析页 (Data)

| 页面 | 占位符名称 | 推荐素材文件名 | 未来素材路径 | 类型 | 用途 | 页面位置 | 所属组件 | 推荐宽度 | 推荐高度 | 是否保持比例 | 是否透明背景 | 当前占位符样式 | 缺失 fallback 文案 | 备注 |
|------|-----------|---------------|-------------|------|------|----------|----------|----------|----------|------------|------------|--------------|-----------------|------|
| 数据 | data-sidebar-microscope-placeholder | microscope.png | Materials/Data/ | decoration | 显微镜装饰 | 数据分析页左下角 | AppShell/SidebarNav | 180px | 160px | 是 | 是 | 虚线框+文字 | "显微镜占位" | 实验器材装饰 |
| 数据 | data-trend-warning-icon-placeholder | trend-warning.svg | Materials/Data/ | chart-icon | 趋势异常警告图标 | 趋势图异常标记区 | MultiMetricTrendChart | 14px | 14px | 是 | 是 | SVG红色三角警告 | "!" | 异常点标注 |
| 数据 | data-export-icon-placeholder | export.svg | Materials/Data/ | button-icon | 导出数据图标 | 筛选栏右侧导出按钮 | DataFilterBar | 14px | 14px | 是 | 是 | SVG下载箭头 | — | 按钮内嵌图标 |
| 数据 | data-confidence-icon-placeholder | confidence.svg | Materials/Data/ | icon | 模型置信度图标 | 置信度卡片内 | ToxinPredictionPanel | 16px | 16px | 是 | 是 | SVG盾牌/对勾 | — | 卡片内嵌图标 |
| 数据 | data-prediction-icon-placeholder | prediction.svg | Materials/Data/ | icon | AI预测图标 | 预测模块标题旁 | ToxinPredictionPanel | 16px | 16px | 是 | 是 | SVG趋势/大脑 | — | 标题旁图标 |

### 7.5 设备配对页 (Drive)

| 页面 | 占位符名称 | 推荐素材文件名 | 未来素材路径 | 类型 | 用途 | 页面位置 | 所属组件 | 推荐宽度 | 推荐高度 | 是否保持比例 | 是否透明背景 | 当前占位符样式 | 缺失 fallback 文案 | 备注 |
|------|-----------|---------------|-------------|------|------|----------|----------|----------|----------|------------|------------|--------------|-----------------|------|
| 设备 | device-card-buoy-placeholder | buoy-device.png | Materials/Drive/ | device-illustration | 浮标设备插画 | 设备卡片左上 | DeviceCard | 40px | 40px | 是 | 是 | 虚线框+浮标SVG | "浮标" | 设备类型图标 |
| 设备 | device-card-probe-placeholder | probe-device.png | Materials/Drive/ | device-illustration | 探针设备插画 | 设备卡片左上 | DeviceCard | 40px | 40px | 是 | 是 | 虚线框+探针SVG | "探针" | 设备类型图标 |
| 设备 | device-card-offline-placeholder | offline-device.png | Materials/Drive/ | device-illustration | 离线设备插画 | 设备卡片左上 | DeviceCard | 40px | 40px | 是 | 是 | 虚线框+灰色设备SVG | "离线" | 灰色态 |
| 设备 | device-scan-bluetooth-placeholder | bluetooth-scan.svg | Materials/Drive/ | icon | 蓝牙扫描图标 | 雷达中心 | PairingPanel | 36px | 36px | 是 | 是 | SVG蓝牙图标 | "蓝牙" | 雷达中心图标 |
| 设备 | device-bottom-mascot-placeholder | device-mascot.png | Materials/Drive/ | mascot | 设备页底部吉祥物 | 配对面板底部 | PairingPanel | 100px | 120px | 是 | 是 | 虚线框+文字 | "实验萌物占位" | 底部装饰 |
| 设备 | device-lab-flask-placeholder | lab-flask.png | Materials/Drive/ | decoration | 实验器材装饰 | 配对面板底部 | PairingPanel | 100px | 120px | 是 | 是 | 虚线框+文字 | "器材占位" | 可与吉祥物合并 |
| 设备 | device-add-icon-placeholder | add.svg | Materials/Drive/ | button-icon | 添加设备图标 | 工具栏添加按钮 | DeviceToolbar | 14px | 14px | 是 | 是 | SVG加号 | "+" | 按钮内嵌 |
| 设备 | device-refresh-icon-placeholder | refresh.svg | Materials/Drive/ | button-icon | 刷新图标 | 工具栏刷新按钮 | DeviceToolbar | 14px | 14px | 是 | 是 | SVG刷新箭头 | "刷新" | 按钮内嵌 |
| 设备 | device-drag-icon-placeholder | drag.svg | Materials/Drive/ | icon | 拖拽手柄图标 | 设备卡片顶部 | DeviceCard | 32px | 4px | 否 | — | CSS圆角矩形条 | — | CSS实现 |
| 设备 | device-wifi-icon-placeholder | wifi.svg | Materials/Drive/ | status-icon | WiFi连接图标 | 设备卡片右上角 | DeviceCard | 14px | 14px | 是 | 是 | SVG WiFi弧形 | — | 绿色 |
| 设备 | device-battery-icon-placeholder | battery.svg | Materials/Drive/ | status-icon | 电量图标 | 设备卡片电量行 | DeviceCard | 12px | 12px | 是 | 是 | SVG电池 | — | 可选文字替代 |
| 设备 | device-signal-icon-placeholder | signal.svg | Materials/Drive/ | status-icon | 信号强度图标 | 设备卡片信号行 | DeviceCard | 12px | 12px | 是 | 是 | SVG信号波纹 | — | 可选文字替代 |

---

## 8. 页面 1：总览页详细规格

### 8.1 基本信息

- **路由**：`/`
- **页面组件名**：`OverviewPage`
- **文件路径**：`src/pages/OverviewPage.tsx`
- **素材目录**：`Materials/Overview/`

### 8.2 页面布局结构

```
┌──────────────────────────────────────────────────────────┐
│ AppHeader (88px)                                         │
│ [Logo][标题组]  [总览|地图|数据|设备]  [通知][团队][吉祥物] │
├────────┬─────────────────────────────────────────────────┤
│Sidebar │ MainContent (px-6 py-5)                        │
│200px   │ ┌─────────────────────────────────────────────┐ │
│        │ │ 指标卡行 (5列, gap-3)                      │ │
│ [总览] │ │ [在线][空闲][离线][平均][最高风险]          │ │
│ [地图] │ └─────────────────────────────────────────────┘ │
│ [数据] │ ┌─────────────────────────────────────────────┐ │
│ [设备] │ │ 中部3列 (gap-4)                            │ │
│        │ │ [系统状态][告警摘要][趋势概览]              │ │
│        │ └─────────────────────────────────────────────┘ │
│ [气泡] │ ┌─────────────────────────────────────────────┐ │
│ [水草] │ │ 最新采样表格 (全宽)                         │ │
│ [吉祥物]│ │ [设备|时间|藻毒素|电量|信号|状态|位置]      │ │
│        │ └─────────────────────────────────────────────┘ │
├────────┴─────────────────────────────────────────────────┤
└──────────────────────────────────────────────────────────┘
```

### 8.3 顶部指标卡行

**容器规格：**
- 布局：CSS Grid，5 列，`grid-cols-2 lg:grid-cols-5`
- 列间距：12px (gap-3)
- 位置：MainContent 第 1 行

**每张指标卡 (MetricSummaryCard) 详细规格：**

| 属性 | 在线设备 | 空闲设备 | 离线设备 | 平均藻毒素 | 最高风险 |
|------|----------|----------|----------|-----------|---------|
| 卡片宽度 | 1fr | 1fr | 1fr | 1fr | 1fr |
| 卡片高度 | 88px-96px | 88px-96px | 88px-96px | 88px-96px | 88px-96px |
| 内边距 | p-4 | p-4 | p-4 | p-4 | p-4 |
| 图标尺寸 | 40×40px | 40×40px | 40×40px | 40×40px | 40×40px |
| 图标形状 | 圆形 | 圆形 | 圆形 | 圆形 | 圆形 |
| 图标背景 | rgba(8,166,90,0.10) | rgba(247,181,0,0.10) | rgba(245,34,45,0.10) | rgba(13,125,242,0.10) | rgba(245,34,45,0.10) |
| 图标颜色 | #08A65A | #F7B500 | #F5222D | #0D7DF2 | #F5222D |
| 标签文字 | "在线设备" | "空闲设备" | "离线设备" | "平均藻毒素" | "最高风险" |
| 标签字号 | 10px bold | 10px bold | 10px bold | 10px bold | 10px bold |
| 主数据格式 | "X / 14 台" | "X / 14 台" | "X / 14 台" | "X.XX" | "X.XX" |
| 主数据字号 | 24px black | 24px black | 24px black | 24px black | 24px black |
| 主数据颜色 | #08A65A | #F7B500 | #F5222D | #0D7DF2 | #F5222D |
| 单位 | — | — | — | "μg/L" (11px) | "μg/L" (11px) |
| 辅助描述 | — | — | — | — | "设备名 · 风险等级" (11px) |
| 数据来源 | demoSummary.onlineDevices | idleCount | offlineCount | demoSummary.averageToxinUgL | demoSummary.maxToxinReading |
| hover 交互 | 边框加深+阴影加强 | 同左 | 同左 | 同左 | 同左 |

**图标 SVG 内容：**
- 在线：WiFi 信号弧形
- 空闲：时钟
- 离线：叉号 / 禁止符号
- 平均藻毒素：水滴 / 藻类
- 最高风险：警告三角

### 8.4 中部内容区

**容器规格：**
- 布局：CSS Grid，3 列，`grid-cols-1 lg:grid-cols-3`
- 列间距：16px (gap-4)
- 位置：指标卡行下方 20px (space-y-5)

#### 8.4.1 SystemStatusPanel（系统状态）

- **组件名**：`SystemStatusPanel`
- **文件路径**：`src/components/overview/SystemStatusPanel.tsx`
- **宽度**：1fr（约 490px @1536px 屏宽）
- **高度**：260px-280px
- **内边距**：p-5
- **标题**："系统状态"
- **副标题**："整体运行概况"

**内部元素（从上到下）：**

1. 盾牌图标区：
   - 居中显示
   - 56px × 56px 圆形图标
   - 背景色：rgba(8, 166, 90, 0.10)
   - 图标色：#08A65A
   - 图标：盾牌+对勾 SVG
   - 下方文字："运行正常"，14px bold，color #08A65A

2. 三项状态摘要：
   - 布局：3 列 grid，gap-2
   - 每项：浅蓝底卡片，border-radius 8px，p-2，居中文字
   - 项 1：标签"数据采集"，值"正常"或"中断"，颜色绿/红
   - 项 2：标签"数据传输"，值"正常"，颜色绿
   - 项 3：标签"设备在线率"，值"XX%"，颜色条件判断（≥50%绿, <50%红）

#### 8.4.2 AlertSummaryPanel（告警摘要）

- **组件名**：`AlertSummaryPanel`
- **文件路径**：`src/components/overview/AlertSummaryPanel.tsx`
- **宽度**：1fr（约 490px @1536px）
- **高度**：260px-280px
- **内边距**：p-5
- **标题**："告警摘要"
- **副标题**："需要关注的异常项"

**内部元素（4 行告警列表）：**

| 行 | 标签 | 颜色 | 背景色 | 左边框 | 数据来源 |
|----|------|------|--------|--------|----------|
| 1 | 高风险告警 | #F5222D | rgba(245,34,45,0.06) | 3px solid #F5222D | toxinUgL > 5 的数量 |
| 2 | 警戒告警 | #FF7A00 | rgba(255,122,0,0.06) | 3px solid #FF7A00 | 1 <= toxinUgL <= 5 的数量 |
| 3 | 关注告警 | #F7B500 | rgba(247,181,0,0.06) | 3px solid #F7B500 | 0.5 <= toxinUgL < 1 的数量 |
| 4 | 设备离线 | #0D7DF2 | rgba(13,125,242,0.06) | 3px solid #0D7DF2 | status === "offline" 的数量 |

每行规格：
- 内边距：p-2.5
- 左侧：文字标签（12px medium）
- 右侧：数字（16px black）+ 右箭头 SVG（14px）
- 行间距：8px
- 整行 hover：背景变为 rgba(13,125,242,0.04)
- cursor: pointer

#### 8.4.3 OverviewTrendChart（趋势概览）

- **组件名**：`OverviewTrendChart`
- **文件路径**：`src/components/overview/OverviewTrendChart.tsx`
- **宽度**：1fr（约 490px @1536px）
- **高度**：260px-280px
- **内边距**：p-5
- **标题**："趋势概览"
- **副标题**："{maxReading.name} 藻毒素浓度"
- **标题操作**：右侧"近 7 天"标签（10px，浅蓝底胶囊，静态展示）

**图表规格：**
- 图表库：Recharts
- 图表类型：AreaChart（面积+折线）
- 图表高度：140px
- 数据：7 天聚合数据（从 demoDeviceHistory 生成）
- X 轴：日期（MM-DD 格式），fontSize 10，tickLine false
- Y 轴：藻毒素值 (μg/L)，fontSize 10，tickLine false
- 面积渐变：从上到下 #0D7DF2 (opacity 0.15) → transparent
- 折线：stroke #0D7DF2, strokeWidth 2
- 阈值线 1（警戒）：y=1.0, stroke #FF7A00, strokeDasharray "4 4"
- 阈值线 2（高风险）：y=5.0, stroke #F5222D, strokeDasharray "4 4"
- Tooltip：白底 95%透明度 + 蓝色边框 + 8px 圆角
- 右上角显示当前值：20px black，color #0D7DF2，如 "6.35 μg/L"

### 8.5 底部最新采样表格 (LatestReadingsTable)

- **组件名**：`LatestReadingsTable`
- **文件路径**：`src/components/overview/LatestReadingsTable.tsx`
- **位置**：中部 3 列下方 20px
- **宽度**：100%
- **高度**：auto
- **内边距**：p-5
- **标题**："最新采样"
- **副标题**："设备端回传的藻毒素浓度、电量和信号质量"
- **标题操作**：右上角 "查看全部" 按钮（aqua-button 样式），点击跳转 /map

**表格规格：**

| 列名 | 宽度比例 | 对齐 | 内容格式 |
|------|----------|------|----------|
| 设备名称 | 2fr | 左 | 8px 彩色圆点 + 设备名（12px bold） |
| 采样时间 | 1fr | 左 | 时间文字（12px, #5A7184） |
| 藻毒素 | 1fr | 左 | 数值（bold, 风险颜色）+ "μg/L" |
| 电量 | 0.8fr | 左 | "XX%"，<20% 红色 |
| 信号强度 | 0.8fr | 左 | "XX dBm"（#5A7184） |
| 状态 | 0.8fr | 左 | 6px 彩色圆点 + 状态文字 |
| 位置 | 1.5fr | 左 | 位置文字（#5A7184），truncate |

**表格样式：**
- 表头背景：rgba(13, 125, 242, 0.04)
- 表头文字：10px bold uppercase，color #5A7184
- 表头圆角：左上/右上 rounded-tl-lg / rounded-tr-lg
- 行高：py-2.5
- 行分隔：border-b border-[rgba(13,125,242,0.06)]
- 行 hover：bg-[rgba(13,125,242,0.03)]
- 数据行数：5 条（按 updatedAt 倒序取前 5）
- 状态圆点：6px × 6px，与文字间距 4px
- 设备名圆点：8px × 8px，风险颜色

### 8.6 总览页交互

1. **指标卡 hover**：边框加深 + 阴影加强（CSS transition 0.2s）
2. **告警摘要行 hover**：背景色微变 + cursor pointer（当前阶段不实现点击跳转）
3. **趋势图 hover**：Tooltip 显示具体日期和数值
4. **"查看全部"按钮 click**：react-router-dom navigate('/map')
5. **表格行 hover**：浅蓝背景高亮

---

## 9. 页面 2：地图监视页详细规格

### 9.1 基本信息

- **路由**：`/map`
- **页面组件名**：`MapMonitorPage`
- **文件路径**：`src/pages/MapMonitorPage.tsx`
- **素材目录**：`Materials/Map/`

### 9.2 页面布局结构

```
┌──────────────────────────────────────────────────────────┐
│ AppHeader (88px) [地图监视 高亮]                         │
├────────┬─────────────────────────────────────────────────┤
│Sidebar │ MainContent                                     │
│200px   │ ┌──────────────────────┬──────────────────────┐ │
│        │ │ LakeRiskMap (1fr)   │ SelectedDevicePanel  │ │
│ [总览] │ │ 720px 高            │ 340px 宽             │ │
│ [地图]◄│ │                     │                      │ │
│ [数据] │ │ [缩放按钮]          │ 设备名称              │ │
│ [设备] │ │ [定位按钮]          │ 风险标签              │ │
│        │ │ [图层切换胶囊]      │ 状态                  │ │
│ [装饰] │ │                     │ [6项指标网格]         │ │
│        │ │ [热力图/设备点]     │ [设备类型/连接/信号]  │ │
│        │ │                     │ [查看历史数据按钮]    │ │
│        │ │ [风险图例]          │ [设备插画占位]        │ │
│        │ └──────────────────────┴──────────────────────┘ │
├────────┴─────────────────────────────────────────────────┤
└──────────────────────────────────────────────────────────┘
```

### 9.3 主地图面板 (LakeRiskMap)

- **组件名**：`LakeRiskMap`
- **文件路径**：`src/components/map/LakeRiskMap.tsx`
- **位置**：MainContent 左侧主列
- **宽度**：1fr（自适应）
- **高度**：720px（min-height）
- **圆角**：12px
- **容器背景**：aqua-panel（白色半透明+蓝色边框+轻阴影）
- **内边距**：p-2.5
- **地图底图区**：内部 inset-2.5，border-radius 10px，overflow hidden，1px border
- **地图实现**：MapContainer（react-leaflet），动态导入确保仅在客户端渲染

**地图控件：**
1. **缩放按钮**（Leaflet 默认）：左上角，蓝色样式覆盖（见 globals.css 已有定义）
2. **定位按钮**：右上角，32×32px，白底+蓝色图标，点击触发 map.flyTo(demoLake.center)
3. **图层切换按钮组（MapLayerToggle）**：顶部水平居中，距顶部 20px

**MapLayerToggle 规格：**
- 位置：absolute，top-5，left-1/2，-translate-x-1/2
- z-index：500
- 背景：white/90 + backdrop-blur
- 按钮：2 个胶囊按钮（"设备图层"/"热力图层"）
- 激活态：蓝色背景+白色文字
- 未激活态：灰色文字
- 按钮内边距：px-3 py-1.5
- 按钮字号：11px semibold

**热力图层：**
- 使用 leaflet.heat
- 透明度：0.45
- 混合模式：multiply
- radius：40
- blur：38
- 渐变色阶（从低到高）：#16B8D8 → #0D7DF2 → #08A65A → #F7B500 → #FF7A00 → #F5222D
- 热力点：基于 IDW 插值算法从 demoReadings 计算格网点
- 随地图缩放/平移自动更新

**设备点位：**
- 使用 Leaflet CircleMarker
- marker 半径：默认 10px，选中 14px，离线 7px
- marker 颜色：根据 getRiskColor(toxinUgL)
- 选中态：蓝色描边(#0D7DF2)，strokeWeight 3
- 点击：onSelectDevice(reading.id)
- Popup：显示设备名、位置、藻毒素、电量、信号、水温、pH、更新时间
- 离线设备：透明度降低（fillOpacity 0.3, opacity 0.5）

### 9.4 右侧设备详情面板 (SelectedDevicePanel)

- **组件名**：`SelectedDevicePanel`
- **文件路径**：`src/components/map/SelectedDevicePanel.tsx`
- **位置**：MainContent 右侧 340px 固定列
- **宽度**：340px
- **高度**：auto（最小 720px 与地图等高）
- **内边距**：p-4
- **容器**：aqua-panel

**内部元素（从上到下）：**

1. **标题区**：
   - 标签："选中设备"（10px bold uppercase tracking-wider, #5A7184）

2. **设备名**：
   - 标题：设备名（15px bold, #0B2540）
   - 副标题：位置（11px, #5A7184）

3. **风险标签（RiskBadge）**：
   - 10px bold，圆角全圆角
   - 颜色按风险等级

4. **状态行**：
   - 状态圆点（6px）+ 状态文字（11px bold）+ 更新时间（11px, #5A7184）

5. **指标网格（2 列 3 行）**：
   每格：圆角卡片（p-2），浅蓝底，9px 标签 uppercase，数值 bold

   | 指标 | 数据字段 | 颜色 |
   |------|----------|------|
   | 藻毒素浓度 | toxinUgL + "μg/L" | 风险色 |
   | 更新时间 | updatedAt | #0B2540 |
   | 电量 | batteryPercent + "%" | <20% 红色 |
   | 信号强度 | signalDbm + "dBm" | #0B2540 |
   | 水温 | waterTempC + "°C" | #0B2540 |
   | pH | ph | #0B2540 |

6. **额外信息区**：
   - 设备类型："水质监测浮标"（固定演示值）
   - 连接方式：WiFi / 蓝牙 / 未连接
   - 信号质量：良好 / 一般 / 弱信号
   - 分隔线：border-t

7. **操作按钮**：
   - "查看历史数据"：aqua-button，全宽，12px 文字，带右箭头图标
   - 点击：navigate('/data') 或仅按钮占位

8. **设备插画占位**：
   - 100% 宽 × 100px-120px 高
   - 虚线边框 + "设备插画占位"文字

**默认状态**：选中 demoSummary.maxToxinReading（最高风险设备），不显示空白面板

### 9.5 风险图例 (RiskLegend)

- **组件名**：`RiskLegend`
- **文件路径**：`src/components/map/RiskLegend.tsx`
- **位置**：地图底部居中，absolute，bottom-5，left-1/2，-translate-x-1/2
- **z-index**：500
- **背景**：white/90 + backdrop-blur
- **内边距**：px-4 py-2
- **圆角**：8px
- **边框**：1px solid rgba(13,125,242,0.10)
- **阴影**：shadow-sm

**图例项（4 项，横向排列）：**

| 颜色 | 标签 | 范围 |
|------|------|------|
| #08A65A | 正常 | < 0.5 μg/L |
| #F7B500 | 关注 | 0.5 - 1.0 μg/L |
| #FF7A00 | 警戒 | 1.0 - 5.0 μg/L |
| #F5222D | 高风险 | > 5.0 μg/L |

每项：10px 圆点(#08A65A) + 标签文字(10px medium #0B2540) + 范围文字(10px #5A7184)
项间距：16px

### 9.6 地图页交互

1. **点击设备点位**：setSelectedDeviceId → 更新右侧 SelectedDevicePanel
2. **点击定位按钮**：map.flyTo(demoLake.center, 13)
3. **切换设备图层**：setShowDevices → 过滤/显示设备 CircleMarker
4. **切换热力图层**：setShowHeat → 添加/移除 HeatLayer
5. **查看历史数据按钮**：navigate('/data')
6. **地图加载中**：全屏居中加载 spinner（蓝色旋转圆圈 + "地图加载中..."文字）
7. **地图加载失败**：显示错误提示卡片（浅红底 + 刷新按钮）
8. **无设备数据**：地图仍正常显示底图，设备点为空，右侧面板显示 "暂无设备数据"

---

## 10. 页面 3：数据分析页详细规格

### 10.1 基本信息

- **路由**：`/data`
- **页面组件名**：`DataAnalysisPage`
- **文件路径**：`src/pages/DataAnalysisPage.tsx`
- **素材目录**：`Materials/Data/`

### 10.2 页面布局结构

```
┌──────────────────────────────────────────────────────────┐
│ AppHeader (88px) [数据分析 高亮]                         │
├────────┬─────────────────────────────────────────────────┤
│Sidebar │ MainContent                                     │
│200px   │ ┌─────────────────────────────────────────────┐ │
│        │ │ DataFilterBar (48-52px)                     │ │
│ [总览] │ │ [时间范围][设备筛选][传感器筛选] [导出数据] │ │
│ [地图] │ └─────────────────────────────────────────────┘ │
│ [数据]◄│ ┌──────────────────────┬──────────────────────┐ │
│ [设备] │ │ MultiMetricTrend     │ SensorComparison     │ │
│        │ │ Chart (1fr, 320px)   │ Panel (300px)        │ │
│ [装饰] │ │                      │                      │ │
│        │ │ [藻毒素/水温/pH]     │ [设备排序列表]       │ │
│        │ │ [阈值线+异常点]      │                      │ │
│        │ └──────────────────────┴──────────────────────┘ │
│        │ ┌──────────────────────┬──────────────────────┐ │
│        │ │ ToxinPrediction (1fr)│ 置信度摘要 (260px)   │ │
│        │ │ [历史+预测+区间]     │ [87%/区间/高风险日]  │ │
│        │ └──────────────────────┴──────────────────────┘ │
│        │ [显微镜占位 180×160]                            │
├────────┴─────────────────────────────────────────────────┤
└──────────────────────────────────────────────────────────┘
```

### 10.3 顶部筛选栏 (DataFilterBar)

- **组件名**：`DataFilterBar`
- **文件路径**：`src/components/data/DataFilterBar.tsx`
- **位置**：MainContent 第一行
- **宽度**：100%
- **高度**：48px-52px
- **内边距**：px-4 py-3
- **容器**：aqua-panel
- **布局**：flex row，flex-wrap，align-items center，gap-3

**筛选控件：**

| 控件 | 类型 | 宽度 | 标签 | 默认值 | 选项 |
|------|------|------|------|--------|------|
| 时间范围 | input (readonly) | 180px | "时间范围" | "2025-05-20 ~ 2025-05-27" | — |
| 设备筛选 | select | auto | "设备" | "all" | 全部设备 / 在线 / 待机 / 离线 |
| 传感器筛选 | select | auto | "传感器" | "all" | 藻毒素+水温+pH / 藻毒素 / 水温 / pH |

- 标签：10px bold uppercase tracking-wider
- 输入框/选择框：12px 文字，白色背景，蓝色边框，圆角 8px，py-1.5 px-2.5

**右侧导出按钮：**
- aqua-button-secondary 样式
- 带导出 SVG 图标（14×14px, 下载箭头）
- 文字："导出数据"（11px bold）
- 位置：flex-1 推到最右

**交互说明：**
- select 变更触发 onFilterChange 回调（当前阶段仅为 UI 状态变更，不强制实施数据过滤）
- 导出按钮点击：当前阶段 console.log 或 alert("导出功能将在后端接入后启用")

### 10.4 趋势分析面板 (MultiMetricTrendChart)

- **组件名**：`MultiMetricTrendChart`
- **文件路径**：`src/components/data/MultiMetricTrendChart.tsx`
- **位置**：筛选栏下方第 2 行左侧
- **宽度**：1fr
- **高度**：320px（图表区）
- **内边距**：p-5
- **容器**：aqua-panel
- **标题**："趋势分析"
- **副标题**："藻毒素、水温、pH 综合趋势图"

**图表规格：**
- 图表库：Recharts
- 图表类型：LineChart（多线折线图）
- 图表区高度：320px
- X 轴：日期（05-20 到 05-27），fontSize 11
- Y 轴（左）：藻毒素值 (μg/L)，fontSize 11
- Y 轴（右）：水温和 pH，fontSize 11，隐藏轴线
- 网格线：水平虚线，stroke rgba(13,125,242,0.08)

**数据线：**

| 线名 | 数据字段 | 颜色 | 线宽 | 线型 | Y轴 |
|------|----------|------|------|------|-----|
| 藻毒素 | toxin | #0D7DF2 | 2.5px | 实线 | 左 |
| 最大浓度 | maxToxin | #F5222D | 1.5px | 虚线 | 左 |
| 水温 | temp | #08A65A | 1.5px | 实线 | 右 |
| pH | ph | #A78BFA | 1.5px | 实线 | 右 |

**阈值线：**
- 警戒线：y=1.0，stroke #FF7A00，strokeDasharray "4 4"，标签"警戒 1.0"
- 高风险线：y=5.0，stroke #F5222D，strokeDasharray "4 4"，标签"高风险 5.0"

**异常点标注：**
- 当 trendData 中有 isHighRisk=true 的数据点时
- 图表下方显示：红色三角警告 SVG + "检测到 N 个异常高值日期"（10px，红色文字）
- 异常点 SVG 图标：14px × 14px

**图例：**
- 顶部水平排列，iconType "line"
- fontSize 11px

**Tooltip：**
- 白底 95%透明度 + 蓝色边框 + 8px 圆角

**空状态：**
- 如果无数据，显示 "暂无趋势数据"（浅蓝虚线框居中）

### 10.5 传感器对比面板 (SensorComparisonPanel)

- **组件名**：`SensorComparisonPanel`
- **文件路径**：`src/components/data/SensorComparisonPanel.tsx`
- **位置**：趋势图右侧
- **宽度**：300px
- **高度**：与趋势图等高（320px+）
- **内边距**：p-5
- **容器**：aqua-panel
- **标题**："传感器对比"
- **副标题**："按当前浓度排序"
- **最大高度**：340px，overflow-y auto

**列表项规格：**
- 每项：flex row，align-items center，justify-between
- 左侧：8px 彩色圆点（风险色）+ 设备名（12px medium, #0B2540, truncate）
- 右侧：藻毒素数值（13px bold, 风险色）
- 行间距：py-1.5
- 行分隔：border-b（最后一行无）
- 排序：按 toxinUgL 从高到低
- 数据来源：demoReadings 按 toxinUgL 降序排列

### 10.6 AI 预测模块 (ToxinPredictionPanel)

- **组件名**：`ToxinPredictionPanel`
- **文件路径**：`src/components/data/ToxinPredictionPanel.tsx`
- **位置**：趋势分析面板下方 16px
- **宽度**：100%
- **布局**：2 列 grid，`grid-cols-1 lg:grid-cols-[1fr_260px]`，gap-4

**左侧预测图：**
- 标题："AI 预测（藻毒素浓度）"
- 副标题："基于历史检测数据的未来浓度演变趋势"
- 标题操作："预测未来 7 天"下拉（10px 浅蓝底胶囊，静态展示）
- 图表区高度：280px
- 数据：14 天（过去 7 天 + 未来 7 天），使用 useMemo 生成

**图表数据线：**
- historical：历史数据（Area, 实线 #0D7DF2, strokeWidth 2.5, 浅蓝面积）
- predicted：预测值（Area, 虚线 #0D7DF2, strokeDasharray "5 5", 更浅面积）
- upperBound / lowerBound：95% 置信区间（Area, 半透明浅蓝填充）
- 危险阈值线：y=5.0, stroke #F5222D, strokeDasharray "3 3"

**图例：**
- "历史数据" / "预测值" / "置信区间 95%"
- 顶部水平排列
- fontSize 10px

**右侧置信度摘要卡：**
- 卡片 1（模型置信度）：
  - 87%（32px black, #0D7DF2）
  - "模型置信度"（10px muted）
  - 分隔线
  - "预测区间（95%）"：0.45 - 3.20 μg/L
  - 分隔线
  - "下一高风险时间"：5月29日（14px bold, #F5222D）
- 卡片 2（爆发预警）：
  - 红色三角警告图标 + "爆发预警"标题（11px bold, #F5222D）
  - "浓度可能在 4-5 天内出现显著上升并逼近危险阈值"（10px muted）
  - 浅红背景，红色边框

### 10.7 数据分析页装饰占位符

- **显微镜/实验器材**：左下角，180px × 160px，虚线框 + "显微镜占位"
  - 可放在 Sidebar 底部或 MainContent 左下绝对定位
  - z-index: 0，不遮挡数据
- **水波装饰**：页面底部 CSS 实现，100% × 40px
- **异常点图标**：红色三角警告，14px × 14px（在趋势图异常提示中使用）
- **导出图标**：下载箭头，14px × 14px（在导出按钮中使用）

---

## 11. 页面 4：设备配对页详细规格

### 11.1 基本信息

- **路由**：`/device`
- **页面组件名**：`DevicePairingPage`
- **文件路径**：`src/pages/DevicePairingPage.tsx`
- **素材目录**：`Materials/Drive/`

### 11.2 页面布局结构

```
┌──────────────────────────────────────────────────────────┐
│ AppHeader (88px) [设备配对 高亮]                         │
├────────┬─────────────────────────────────────────────────┤
│Sidebar │ MainContent                                     │
│200px   │ ┌─────────────────────────────────────────────┐ │
│        │ │ DeviceToolbar (36-40px)                     │ │
│ [总览] │ │ [添加设备] [刷新列表] [批量操作▾]          │ │
│ [地图] │ └─────────────────────────────────────────────┘ │
│ [数据] │ ┌────────────────────┬────────────────────────┐ │
│ [设备]◄│ │ DeviceCardGrid     │ PairingPanel (300px)   │ │
│        │ │ (DndContext)       │                        │ │
│ [装饰] │ │ ┌─────┬─────┬────┐│ 添加新设备             │ │
│        │ │ │卡片1│卡片2│卡片3││ [雷达扫描圆]           │ │
│        │ │ │卡片4│卡片5│卡片6││ 扫描附近设备...        │ │
│        │ │ │ ... │ ... │ ...││ [开始/重新扫描]        │ │
│        │ │ └─────┴─────┴────┘│                        │ │
│        │ │ [拖拽提示虚线框]   │ 已发现设备（2）         │ │
│        │ │                    │ [WaterProbe-7F2A]      │ │
│        │ │                    │ [Buoy-3C91]            │ │
│        │ │                    │ [实验器材占位]         │ │
│        │ └────────────────────┴────────────────────────┘ │
├────────┴─────────────────────────────────────────────────┤
└──────────────────────────────────────────────────────────┘
```

### 11.3 顶部工具栏 (DeviceToolbar)

- **组件名**：`DeviceToolbar`
- **文件路径**：`src/components/device/DeviceToolbar.tsx`
- **位置**：MainContent 第一行
- **宽度**：100%
- **高度**：36px-40px
- **布局**：flex row，align-items center，gap-2
- **下边距**：mb-4

**按钮规格：**

| 按钮 | 样式 | 图标 | 文字 | 功能 |
|------|------|------|------|------|
| 添加设备 | aqua-button | 加号 SVG (14×14) | "添加设备" | 打开添加模态框/重置扫描 |
| 刷新列表 | aqua-button-secondary | 刷新 SVG (14×14) | "刷新列表" | 重置设备列表为初始数据 |
| 批量操作 | aqua-button-secondary | 下拉箭头 SVG (12×12) | "批量操作" | 当前阶段为占位按钮 |

- 按钮内边距：py-1.5 px-3
- 按钮字号：11px bold
- 按钮高度：32px

### 11.4 设备卡片网格 (DeviceCardGrid)

- **组件名**：`DeviceCardGrid`
- **文件路径**：`src/components/device/DeviceCardGrid.tsx`
- **位置**：工具栏下方，左侧主列
- **宽度**：1fr
- **高度**：auto
- **网格布局**：`grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3`，gap-3
- **拖拽上下文**：包裹在 DndContext + SortableContext 中

### 11.5 单张设备卡片 (DeviceCard)

- **组件名**：`DeviceCard`
- **文件路径**：`src/components/device/DeviceCard.tsx`
- **宽度**：300px-330px（3 列网格中 1 列）
- **高度**：230px-260px
- **内边距**：p-3
- **容器**：aqua-card
- **圆角**：10px
- **离线态**：opacity 0.6，grayscale 30%
- **高风险态**：border color rgba(245,34,45,0.25)

**内部元素（从上到下）：**

1. **拖拽手柄**（绝对定位，卡片顶部居中）：
   - 宽 32px，高 4px
   - 圆角矩形条，color rgba(13,125,242,0.15)
   - hover：rgba(13,125,242,0.30)
   - cursor：grab / grabbing

2. **头部区域**：
   - 设备插画占位：40px × 40px，左侧
   - 设备名：13px bold，truncate
   - 状态标签：10px bold + 6px 圆点
   - 更新时间：10px, #5A7184
   - 右上角 WiFi/蓝牙图标：14px × 14px

3. **三列指标区**（grid grid-cols-3 gap-1.5）：
   每格：p-1.5，浅蓝底卡片，居中文字

   | 指标 | 数据 | 字号 | 颜色 |
   |------|------|------|------|
   | 藻毒素 | XX.XX μg/L | 13px black | 风险色 |
   | 水温 | XX.X °C | 13px black | #0B2540 |
   | pH | X.X | 13px black | #0B2540 |

   每个指标上方有 8px 灰色标签（"藻毒素"/"水温"/"pH"）

4. **电量/信号行**：
   - flex row，justify-between
   - 电量：10px，"电量 XX%"，<20% 红色 bold
   - 信号：10px，"信号 {良好/一般/弱信号}"，弱信号黄色 bold

5. **操作按钮区**（mt-auto，卡片底部）：
   - 离线设备：蓝牙 + WiFi 连接按钮（各占 50%）
   - 已连接设备：断开连接按钮（全宽，红色边框）
   - 详情按钮（aqua-button，flex-1）+ 编辑图标按钮 + 删除图标按钮

**操作按钮样式：**
- 详情按钮：flex-1，py-1.5，aqua-button，10px bold
- 编辑按钮：py-1.5 px-2，白底蓝边框，10px bold，编辑 SVG 图标
- 删除按钮：py-1.5 px-2，白底红边框，10px bold，删除 SVG 图标
- 蓝牙按钮：flex-1，浅蓝底蓝边框，"蓝牙"文字+蓝牙SVG
- WiFi 按钮：flex-1，浅绿底绿边框，"WiFi"文字+WiFi SVG
- 断开按钮：全宽，浅红底红边框，"断开连接"

### 11.6 拖拽排序提示区 (DeviceSortDropZone)

- **组件名**：`DeviceSortDropZone`
- **文件路径**：`src/components/device/DeviceSortDropZone.tsx`
- **位置**：设备卡片网格下方
- **宽度**：100%（与网格同宽）
- **高度**：40px-48px
- **上边距**：mt-3
- **样式**：虚线边框（2px dashed rgba(13,125,242,0.10)），圆角 8px
- **内容**：居中文字 "拖拽设备卡片可调整顺序"（10px, #5A7184）

### 11.7 右侧配对面板 (PairingPanel)

- **组件名**：`PairingPanel`
- **文件路径**：`src/components/device/PairingPanel.tsx`
- **位置**：右侧 300px 固定列
- **宽度**：300px
- **高度**：auto
- **内边距**：p-4
- **容器**：aqua-panel
- **内部间距**：space-y-4

**内部元素（从上到下）：**

1. **标题**："添加新设备"（14px bold, #0B2540）

2. **雷达扫描区域**：
   - 宽 112px，高 112px，水平居中
   - 3 层同心圆（CSS border）：最外层 opacity 0.12，中间 0.08，内层 0.06
   - 中心图标：36px × 36px 圆形 + 蓝牙 SVG 图标
   - 扫描动画：外层圆 animate-ping（蓝色，opacity 0.3，仅在 isScanning 时显示）

3. **扫描状态文字**：
   - "扫描附近设备..."（扫描中）/ "扫描附近设备"（空闲）
   - 11px，居中，#5A7184

4. **扫描按钮**：
   - aqua-button，全宽，11px
   - 文字：scanDone ? "重新扫描" : "开始扫描"
   - 仅当 !isScanning 时显示

5. **已发现设备列表**：
   - 标题："已发现设备（N）"（11px bold, #0B2540）
   - 列表项（每项 48px-56px）：
     - aqua-card 容器，p-2.5，flex row justify-between
     - 左侧：设备名（12px bold）+ RSSI（10px muted）
     - 右侧：配对按钮（aqua-button，10px，py-1 px-2.5）
       - bluetooth 设备 → "蓝牙配对"
       - wifi 设备 → "WiFi连接"

6. **底部装饰**：
   - 实验器材占位：100px × 120px
   - 虚线框 + "实验器材占位"

**默认显示设备：**
- WaterProbe-7F2A：RSSI -48 dBm，type bluetooth
- Buoy-3C91：RSSI -62 dBm，type wifi

### 11.8 模态框 (DeviceFormModal)

当前阶段所有模态框（详情、编辑、删除确认、连接中、添加中）均使用固定定位 + 遮罩层实现：

- **遮罩**：固定定位全屏，bg-[#0B2540]/30，backdrop-filter blur(4px)，z-100
- **内容框**：aqua-panel，p-5，max-w-md（详情/编辑）/ max-w-sm（删除/加载），居中
- **关闭方式**：右上角 X 按钮 + 取消按钮

**详情模态框规格：**
- 标题："采样详情"（15px bold）
- 8 行键值对（设备名称、位置、藻毒素、水温、pH、电量、信号、更新时间）
- 底部 "确认" 按钮（aqua-button，全宽）

**编辑模态框规格：**
- 标题："编辑设备"（15px bold）
- 4 个表单字段：设备名称（input）、设备类型（select: 浮标/探针/岸线巡检器/其他）、位置名称（input）、连接方式（select: 未连接/WiFi/蓝牙）
- 底部双按钮：取消（aqua-button-secondary）+ 保存（aqua-button）

**删除确认模态框规格：**
- 居中红色圆形警告图标（40×40px）
- 标题："确认删除"（14px bold）
- 文案："确定要删除设备 {name} 吗？"（12px muted）
- 底部双按钮：取消 + 确认删除（红色实心按钮）

**连接/添加中模态框规格：**
- 旋转加载圆圈（border-2 border-[#0D7DF2] border-t-transparent animate-spin，40×40px）
- 标题：操作名称（14px bold）
- 文案：操作说明（12px muted）
- "中断"按钮（aqua-button-secondary）

### 11.9 设备页交互

| 交互 | 触发元素 | 状态变化 | UI 反馈 | 数据 | 是否仅前端 |
|------|----------|----------|---------|------|-----------|
| 添加设备 | "添加设备"按钮 | isScanning→false, scanDone→false | 重置扫描面板 | — | 是 |
| 刷新列表 | "刷新列表"按钮 | devices→demoReadings | 设备网格恢复初始 | demoReadings | 是 |
| 查看详情 | 设备卡片"详情"按钮 | modal.type='details' | 详情模态框弹出 | device | 是 |
| 编辑设备 | 设备卡片编辑图标 | modal.type='edit' | 编辑模态框弹出 | device | 是 |
| 保存编辑 | 编辑模态框"保存"按钮 | devices更新 | 设备卡片更新，模态框关闭 | editForm | 是 |
| 删除设备 | 设备卡片删除图标 | modal.type='delete' | 删除确认模态框弹出 | device | 是 |
| 确认删除 | 删除模态框"确认删除"按钮 | devices过滤 | 卡片移除，模态框关闭 | device.id | 是 |
| 蓝牙连接 | 离线卡"蓝牙"按钮 | modal.type='connecting'→status变idle | 加载动画→设备变为待机 | device.id | 是（模拟延时1.2s） |
| WiFi连接 | 离线卡"WiFi"按钮 | modal.type='connecting'→status变idle | 加载动画→设备变为待机 | device.id | 是（模拟延时1.2s） |
| 断开连接 | 已连接卡"断开连接"按钮 | status变offline, connectionType变none | 卡片灰色态 | device.id | 是 |
| 拖拽排序 | 设备卡片顶部拖拽手柄 | 设备列表顺序变化 | 拖拽中卡片半透明+z-10 | devices | 是（@dnd-kit） |
| 扫描设备 | 配对面板"开始扫描"按钮 | isScanning=true→2s后false | 雷达动画→显示结果 | DISCOVERED_DEVICES | 是（模拟延时2s） |
| 蓝牙配对 | 发现设备"蓝牙配对"按钮 | modal.type='adding'→设备添加 | 加载动画→新卡片出现 | discovered device | 是（模拟延时1s） |
| WiFi连接 | 发现设备"WiFi连接"按钮 | modal.type='adding'→设备添加 | 加载动画→新卡片出现 | discovered device | 是（模拟延时1s） |

---

## 12. 数据模型与字段规范

### 12.1 TypeScript 类型定义

所有类型定义位于 `src/types/domain.ts`。

```typescript
// ── 枚举类型 ──

/** 设备运行状态 */
export type DeviceStatus = 'online' | 'idle' | 'offline';

/** 连接方式 */
export type ConnectionType = 'bluetooth' | 'wifi' | 'none';

/** 风险等级 */
export type RiskLevel = 'normal' | 'watch' | 'warning' | 'critical';
```

### 12.2 核心数据接口

#### DeviceReading（采样读数）

| 字段名 | 类型 | 含义 | 示例值 | 必填 | 对应页面用途 |
|--------|------|------|--------|------|-------------|
| id | string | 设备唯一标识 | "aq-001" | 是 | 所有页面设备主键 |
| name | string | 设备名称 | "湖心浮标-01" | 是 | 表格/卡片/地图/详情展示 |
| status | DeviceStatus | 运行状态 | "online" | 是 | 状态筛选/颜色/交互 |
| connectionType | ConnectionType | 连接方式 | "wifi" | 是 | 设备卡片连接图标 |
| locationLabel | string | 位置描述 | "东湖湖心采样点" | 是 | 表格/详情展示 |
| lat | number | 纬度 | 30.5558 | 是 | 地图点位 |
| lng | number | 经度 | 114.3991 | 是 | 地图点位 |
| batteryPercent | number | 电量百分比 (0-100) | 86 | 是 | 指标/电量显示 |
| signalDbm | number | 信号强度 (dBm) | -61 | 是 | 信号质量显示 |
| toxinUgL | number | 藻毒素浓度 (μg/L) | 0.42 | 是 | 风险计算/图表Y轴 |
| waterTempC | number | 水温 (°C) | 24.8 | 是 | 图表/详情展示 |
| ph | number | pH 值 | 7.4 | 是 | 图表/详情展示 |
| updatedAt | string | 最后更新时间 | "09:42" | 是 | 所有页面的时间显示 |

#### DeviceHistoryPoint（历史数据点）

| 字段名 | 类型 | 含义 | 示例值 | 必填 | 对应页面用途 |
|--------|------|------|--------|------|-------------|
| time | string | 时间标签 | "12:00" | 是 | 图表 X 轴 |
| toxinUgL | number | 藻毒素浓度 | 0.45 | 是 | 趋势图 Y 轴 |
| waterTempC | number | 水温 | 25.1 | 是 | 趋势图 Y 轴 |
| ph | number | pH 值 | 7.5 | 是 | 趋势图 Y 轴 |
| batteryPercent | number | 电量百分比 | 82 | 是 | 备用 |
| signalDbm | number | 信号强度 | -64 | 是 | 备用 |

#### AlertSummary（告警摘要）

此类型由 demoReadings 计算得出，不作为独立持久化类型，但在 AlertSummaryPanel 中作为 props 传递：

```typescript
interface AlertSummaryData {
  criticalCount: number;   // toxinUgL > 5
  warningCount: number;    // 1 <= toxinUgL <= 5
  watchCount: number;      // 0.5 <= toxinUgL < 1
  offlineCount: number;    // status === "offline"
}
```

#### TrendPoint（趋势数据点）

```typescript
interface TrendPoint {
  date: string;        // "05-20"
  toxin: number;       // 平均藻毒素
  maxToxin: number;    // 最大藻毒素
  temp: number;        // 平均水温
  ph: number;          // 平均 pH
  isHighRisk: boolean; // 是否包含高风险数据点
}
```

#### PredictionPoint（预测数据点）

```typescript
interface PredictionPoint {
  date: string;              // "05-20"
  historical: number | null; // 历史值（过去7天有效，未来为null）
  predicted: number | null;  // 预测值（未来7天有效，过去为null）
  upperBound: number | null; // 置信区间上限
  lowerBound: number | null; // 置信区间下限
}
```

#### DiscoveredDevice（发现设备）

```typescript
interface DiscoveredDevice {
  name: string;            // 设备名称
  rssi: number;            // RSSI 信号强度 (dBm)
  type: 'bluetooth' | 'wifi'; // 连接类型
}
```

#### FilterState（筛选条件）

```typescript
interface FilterState {
  dateRange: string;   // 时间范围文本
  device: string;      // 设备筛选值 ("all" | "online" | "idle" | "offline")
  metric: string;      // 传感器筛选值 ("all" | "toxin" | "temp" | "ph")
}
```

#### DeviceItem（设备卡片数据，设备页用）

```typescript
interface DeviceItem {
  id: string;
  deviceName: string;
  status: DeviceStatus;
  location: string;
  battery: number;
  signalDbm: number;
  toxinUgL: number;
  waterTempC: number;
  ph: number;
  updatedAt: string;
  connectionType: ConnectionType;
}
```

#### DeviceAction（设备操作类型）

```typescript
type DeviceModalType = 'none' | 'details' | 'edit' | 'delete' | 'connecting' | 'adding';

interface DeviceModalState {
  type: DeviceModalType;
  device?: DeviceItem;
  title?: string;
  message?: string;
  loading?: boolean;
}
```

### 12.3 演示数据常量

| 常量名 | 类型 | 说明 |
|--------|------|------|
| demoReadings | DeviceReading[] | 14 个模拟设备采样数据 |
| demoDeviceHistory | Record<string, DeviceHistoryPoint[]> | 每设备 24 小时模拟历史数据 |
| demoSummary | object | 汇总统计（在线数、低电量数、弱信号数、平均毒素、最高毒素设备） |
| demoLake | object | 演示湖泊中心坐标 (30.5667, 114.3833) 和边界 |

---

## 13. 风险规则与状态规则

### 13.1 藻毒素浓度风险分级

| 风险等级 | RiskLevel | 阈值范围 | 中文标签 | 颜色代码 | 颜色名称 |
|----------|-----------|----------|----------|----------|----------|
| 正常 | normal | < 0.5 μg/L | 正常 | #08A65A | 薄荷绿 |
| 关注 | watch | 0.5 - 1.0 μg/L | 关注 | #F7B500 | 黄 |
| 警戒 | warning | 1.0 - 5.0 μg/L | 警戒 | #FF7A00 | 橙 |
| 高风险 | critical | > 5.0 μg/L | 高风险 | #F5222D | 红 |

所有页面统一使用 `src/utils/risk.ts` 中的以下函数：

```typescript
getRiskLevel(toxinUgL: number): RiskLevel
getRiskLabel(toxinUgL: number): string    // → "正常" | "关注" | "警戒" | "高风险"
getRiskColor(toxinUgL: number): string    // → "#08A65A" | "#F7B500" | "#FF7A00" | "#F5222D"
```

### 13.2 设备状态映射

| 状态 | DeviceStatus | 中文标签 | 圆点颜色 | 文字颜色 | 圆点动画 | 备注 |
|------|-------------|----------|----------|----------|----------|------|
| online | online | 在线采样 | #08A65A | #08A65A | animate-pulse | 正常工作中 |
| idle | idle | 待机 | #F7B500 | #F7B500 | 无 | 已连接但未采样 |
| offline | offline | 离线 | #F5222D | #F5222D | 无 | 未连接 |

使用 `getStatusText(status: DeviceStatus): string` 获取中文标签。

### 13.3 数值颜色规则

| 场景 | 条件 | 颜色 |
|------|------|------|
| 藻毒素高风险 | toxinUgL > 5 | #F5222D |
| 藻毒素警戒 | 1 <= toxinUgL <= 5 | #FF7A00 |
| 藻毒素关注 | 0.5 <= toxinUgL < 1 | #F7B500 |
| 藻毒素正常 | toxinUgL < 0.5 | #08A65A |
| 低电量 | batteryPercent < 20 | #F5222D |
| 弱信号 | signalDbm < -85 | #F7B500 |
| 主强调 / 平均值 | — | #0D7DF2 |

### 13.4 表格状态圆点

- **直径**：设备名前圆点 8px，状态圆点 6px
- **颜色**：按风险等级或设备状态取色
- **与文字间距**：4px-6px（gap-1 到 gap-1.5）
- **在线设备**：添加 animate-pulse 脉动动画

### 13.5 Badge / 标签规范

| 类型 | 尺寸 | 背景色 | 文字颜色 | 圆角 | 内边距 |
|------|------|--------|----------|------|--------|
| 状态 Badge | inline-flex | 对应状态色 10% 透明度 | 对应状态色 | full (20px) | px-2 py-0.5 |
| 风险 Badge | inline-flex | 对应风险色 ~8% 透明度 | 对应风险色 | 6px | px-2 py-0.5 |
| 数值 Badge | 内联 | none | 风险色 | — | — |

---

## 14. 交互流程

### 14.1 导航切换

1. **触发元素**：Header 顶部导航胶囊 / Sidebar 导航项
2. **触发条件**：点击
3. **状态变化**：URL 变更 + 激活态切换
4. **UI 反馈**：当前路由对应的导航项高亮（蓝色背景/文字/指示条）
5. **涉及数据**：无
6. **当前阶段**：react-router-dom 正常路由跳转

### 14.2 总览页 → 查看全部

1. **触发元素**：最新采样表格右上角 "查看全部" 按钮
2. **触发条件**：点击
3. **状态变化**：路由跳转到 /map
4. **UI 反馈**：页面切换到地图监视页
5. **涉及数据**：无
6. **当前阶段**：正常路由跳转

### 14.3 总览页 → 点击告警摘要

1. **触发元素**：告警摘要各行
2. **触发条件**：点击
3. **状态变化**：当前阶段仅 console.log 对应告警类别
4. **UI 反馈**：行 hover 高亮
5. **涉及数据**：告警类别
6. **当前阶段**：仅前端展示，不跳转

### 14.4 地图页 → 点击设备点

1. **触发元素**：Leaflet CircleMarker
2. **触发条件**：点击
3. **状态变化**：selectedDeviceId → 被点击设备 id
4. **UI 反馈**：
   - 被点击 marker：蓝色描边 + 半径变大（14px）
   - 之前选中 marker：恢复默认样式
   - 右侧面板：更新为选中设备详情
   - Popup：显示设备摘要信息
5. **涉及数据**：selectedDeviceId, demoReadings
6. **当前阶段**：纯前端 state

### 14.5 地图页 → 切换热力图

1. **触发元素**：地图顶部 "热力图层" 胶囊按钮
2. **触发条件**：点击
3. **状态变化**：showHeat toggle
4. **UI 反馈**：
   - 按钮：激活态蓝色/未激活灰色
   - 热力图层：显示/隐藏（添加/移除 HeatLayer）
5. **涉及数据**：showHeat state
6. **当前阶段**：纯前端 state，Leaflet layer 操作

### 14.6 地图页 → 切换设备图层

1. **触发元素**：地图顶部 "设备图层" 胶囊按钮
2. **触发条件**：点击
3. **状态变化**：showDevices toggle
4. **UI 反馈**：
   - 按钮：激活态蓝色/未激活灰色
   - 设备 CircleMarker：显示/隐藏
5. **涉及数据**：showDevices state
6. **当前阶段**：纯前端 state

### 14.7 地图页 → 查看历史数据

1. **触发元素**：右侧面板底部 "查看历史数据" 按钮
2. **触发条件**：点击
3. **状态变化**：navigate('/data')
4. **UI 反馈**：页面切换到数据分析页
5. **涉及数据**：无
6. **当前阶段**：正常路由跳转

### 14.8 数据分析页 → 筛选时间范围

1. **触发元素**：时间范围 input
2. **触发条件**：当前阶段为 readonly，仅展示
3. **状态变化**：无
4. **UI 反馈**：无
5. **涉及数据**：FilterState.dateRange
6. **当前阶段**：静态展示，不实现真实日期选择器

### 14.9 数据分析页 → 筛选设备

1. **触发元素**：设备 select 下拉
2. **触发条件**：选择变更
3. **状态变化**：FilterState.device 更新
4. **UI 反馈**：当前阶段仅更新 state，不强制过滤图表数据
5. **涉及数据**：FilterState.device
6. **当前阶段**：UI 状态变更，不强制数据过滤

### 14.10 数据分析页 → 筛选传感器

1. **触发元素**：传感器 select 下拉
2. **触发条件**：选择变更
3. **状态变化**：FilterState.metric 更新
4. **UI 反馈**：当前阶段仅更新 state，不强制过滤图表数据
5. **涉及数据**：FilterState.metric
6. **当前阶段**：UI 状态变更，不强制数据过滤

### 14.11 数据分析页 → 导出数据

1. **触发元素**：筛选栏 "导出数据" 按钮
2. **触发条件**：点击
3. **状态变化**：无
4. **UI 反馈**：当前阶段 alert("导出功能将在后端接入后启用")
5. **涉及数据**：无
6. **当前阶段**：仅按钮占位

### 14.12 设备页 → 添加设备

1. **触发元素**：工具栏 "添加设备" 按钮
2. **触发条件**：点击
3. **状态变化**：isScanning→false, scanDone→false
4. **UI 反馈**：右侧配对面板重置为初始扫描状态
5. **涉及数据**：isScanning, scanDone state
6. **当前阶段**：纯前端 state

### 14.13 设备页 → 编辑设备

1. **触发元素**：设备卡片编辑图标按钮
2. **触发条件**：点击
3. **状态变化**：modal.type='edit', modal.device=当前设备, editForm填充
4. **UI 反馈**：编辑模态框弹出
5. **涉及数据**：device, editForm
6. **当前阶段**：纯前端 state + 表单

### 14.14 设备页 → 删除设备

1. **触发元素**：设备卡片删除图标按钮
2. **触发条件**：点击
3. **状态变化**：modal.type='delete', modal.device=当前设备
4. **UI 反馈**：删除确认模态框弹出
5. **涉及数据**：device
6. **当前阶段**：纯前端 state，确认后从前端 devices 数组中移除

### 14.15 设备页 → 拖拽排序

1. **触发元素**：设备卡片顶部拖拽手柄
2. **触发条件**：PointerEvent (需移动 > 5px 激活)
3. **状态变化**：devices 数组顺序变化（arrayMove）
4. **UI 反馈**：
   - 拖拽中：卡片 opacity 0.85 + z-10 浮起
   - 放下：卡片重新排序
5. **涉及数据**：devices state
6. **当前阶段**：@dnd-kit 纯前端排序

### 14.16 设备页 → 扫描附近设备

1. **触发元素**：配对面板 "开始扫描" / "重新扫描" 按钮
2. **触发条件**：点击
3. **状态变化**：isScanning=true → 2s后 → isScanning=false, scanDone=true
4. **UI 反馈**：
   - 雷达动画（animate-ping）
   - 扫描文字变为 "扫描附近设备..."
   - 2s 后恢复并显示结果
5. **涉及数据**：isScanning, scanDone state
6. **当前阶段**：setTimeout 模拟扫描过程

### 14.17 设备页 → 蓝牙配对

1. **触发元素**：离线设备卡片 "蓝牙" 按钮 / 发现设备 "蓝牙配对" 按钮
2. **触发条件**：点击
3. **状态变化**：
   - 离线设备：modal.type='connecting' → 1.2s后 status变idle, connectionType变bluetooth
   - 发现设备：modal.type='adding' → 1s后将新设备加入 devices 数组
4. **UI 反馈**：加载动画 → 设备卡片状态更新 / 新卡片出现
5. **涉及数据**：devices state, 目标设备 id
6. **当前阶段**：setTimeout 模拟，纯前端 state

### 14.18 设备页 → WiFi 连接

1. **触发元素**：离线设备卡片 "WiFi" 按钮 / 发现设备 "WiFi连接" 按钮
2. **触发条件**：点击
3. **状态变化**：
   - 离线设备：modal.type='connecting' → 1.2s后 status变idle, connectionType变wifi
   - 发现设备：modal.type='adding' → 1s后将新设备加入 devices 数组
4. **UI 反馈**：加载动画 → 设备卡片状态更新 / 新卡片出现
5. **涉及数据**：devices state, 目标设备 id
6. **当前阶段**：setTimeout 模拟，纯前端 state

### 14.19 设备页 → 断开连接

1. **触发元素**：已连接设备卡片 "断开连接" 按钮
2. **触发条件**：点击
3. **状态变化**：status→offline, connectionType→none
4. **UI 反馈**：卡片变灰（opacity 0.6 + grayscale 30%）
5. **涉及数据**：devices state, 目标设备 id
6. **当前阶段**：纯前端 state，即时生效

### 14.20 加载态、空状态、错误态

| 状态类型 | 触发条件 | UI 表现 | 涉及页面 |
|----------|----------|---------|----------|
| 地图加载中 | Leaflet MapContainer 初次渲染 | 蓝色旋转圆圈 + "地图加载中..." | /map |
| 地图加载失败 | Leaflet 初始化异常 | 浅红底错误卡片 + 刷新按钮 | /map |
| 图表无数据 | 数据数组为空时 | "暂无趋势数据" 虚线占位 | /data |
| 设备列表为空 | devices 全部删除后 | 空状态提示 "暂无配对设备" | /device |
| 选中设备无数据 | selectedDeviceId 对应设备不存在 | "暂无设备数据"文字 | /map |
| 模态框加载中 | 连接/添加设备异步过程 | 旋转圆圈 + 操作说明 + 中断按钮 | /device |
| 图片加载失败 | <img> onError | 显示 ImagePlaceholder 占位符 | 所有页面 |
| 页面 404 | 路由不匹配 | 简单的 404 提示文字 | 全局 |

---

## 15. 组件拆分方案

### 15.1 通用组件 (common/)

| 组件名 | 文件路径 | 所属页面 | 功能 | Props | State | 是否可复用 | 是否依赖数据 | 是否依赖图片占位符 | 子组件 | 父组件 |
|--------|----------|----------|------|-------|-------|-----------|-------------|-----------------|--------|--------|
| AquaPanel | src/components/common/AquaPanel.tsx | 全部 | 通用半透明白色面板容器 | title?, subtitle?, children, className?, action? | 无 | 是，全局 | 否 | 否 | 无 | 各页面组件 |
| AquaCard | src/components/common/AquaCard.tsx | 全部 | 通用白色数据卡片 | children, className?, onClick? | 无 | 是，全局 | 否 | 否 | 无 | 各页面组件 |
| ImagePlaceholder | src/components/common/ImagePlaceholder.tsx | 全部 | 图片占位符（固定宽高） | width, height, label, fileName, variant? | 无 | 是，全局 | 否 | 是（自举占位） | 无 | 各页面组件 |
| IconPlaceholder | src/components/common/IconPlaceholder.tsx | 全部 | 图标占位符（固定宽高） | size, label, iconType?, color? | 无 | 是，全局 | 否 | 是（自举占位） | SVG图标 | 各页面组件 |
| EmptyAssetSlot | src/components/common/EmptyAssetSlot.tsx | 全部 | 通用资源占位（从旧项目迁移） | label, variant, size | 无 | 是，全局 | 否 | 是（自举占位） | SVG图标 | ImagePlaceholder备用 |
| StatusBadge | src/components/common/StatusBadge.tsx | 全部 | 设备状态标签 | status: DeviceStatus | 无 | 是，全局 | 否（仅用status枚举） | 否 | 无 | DeviceCard, SelectedDevicePanel, LatestReadingsTable |
| RiskBadge | src/components/common/RiskBadge.tsx | 全部 | 风险等级标签 | toxinUgL: number, showValue?: boolean | 无 | 是，全局 | 是（调用getRiskColor/getRiskLabel） | 否 | 无 | SelectedDevicePanel, 各指标卡片 |
| AppButton | src/components/common/AppButton.tsx | 全部 | 通用按钮（主/次/危险） | variant: 'primary' \| 'secondary' \| 'danger', children, onClick?, icon?, className? | 无 | 是，全局 | 否 | 否（可选icon prop） | 无 | 各页面工具栏/操作区 |
| AppSelect | src/components/common/AppSelect.tsx | 数据/设备 | 通用下拉选择器 | label, value, options, onChange | 无 | 是 | 否 | 否 | 无 | DataFilterBar |

### 15.2 布局组件 (layouts/)

| 组件名 | 文件路径 | 所属页面 | 功能 | Props | State | 是否可复用 | 是否依赖数据 | 是否依赖图片占位符 | 子组件 | 父组件 |
|--------|----------|----------|------|-------|-------|-----------|-------------|-----------------|--------|--------|
| AppShell | src/layouts/AppShell.tsx | 全部 | 全局布局壳（Header+Sidebar+Content） | children | 无 | 否，单例 | 否 | 是（Header/Sidebar中的占位符） | AppHeader, SidebarNav, MainContent | App.tsx |
| AppHeader | src/layouts/AppHeader.tsx | 全部 | 顶部品牌导航栏 | 无（内部使用useLocation判断激活态） | 无 | 否，单例 | 否 | 是（Logo占位+吉祥物占位） | react-router-dom NavLink | AppShell |
| SidebarNav | src/layouts/SidebarNav.tsx | 全部 | 左侧垂直导航栏 | 无（内部使用useLocation判断激活态） | 无 | 否，单例 | 否 | 是（导航图标+吉祥物+装饰占位） | react-router-dom NavLink | AppShell |

### 15.3 总览页组件 (overview/)

| 组件名 | 文件路径 | 所属页面 | 功能 | Props | State | 是否可复用 | 是否依赖数据 | 是否依赖图片占位符 | 子组件 | 父组件 |
|--------|----------|----------|------|-------|-------|-----------|-------------|-----------------|--------|--------|
| MetricSummaryCard | src/components/overview/MetricSummaryCard.tsx | 总览 | 顶部指标卡 | label, value, suffix?, description?, color, icon | 无 | 是，5次实例化 | 是（数据通过props） | 是（图标占位符） | IconPlaceholder | OverviewPage |
| SystemStatusPanel | src/components/overview/SystemStatusPanel.tsx | 总览 | 系统状态面板 | summary: DemoSummary | 无 | 否 | 是（demoSummary） | 是（盾牌图标占位符） | AquaPanel | OverviewPage |
| AlertSummaryPanel | src/components/overview/AlertSummaryPanel.tsx | 总览 | 告警摘要面板 | alerts: AlertSummaryData | 无 | 否 | 是（AlertSummaryData） | 否 | AquaPanel | OverviewPage |
| OverviewTrendChart | src/components/overview/OverviewTrendChart.tsx | 总览 | 7天趋势概览图 | data: TrendPoint[], currentValue: number | 无 | 否 | 是（TrendPoint[]） | 否 | AquaPanel, Recharts AreaChart | OverviewPage |
| LatestReadingsTable | src/components/overview/LatestReadingsTable.tsx | 总览 | 最新采样表格 | readings: DeviceReading[] | 无 | 否 | 是（DeviceReading[]） | 否 | AquaPanel, StatusBadge | OverviewPage |

### 15.4 地图页组件 (map/)

| 组件名 | 文件路径 | 所属页面 | 功能 | Props | State | 是否可复用 | 是否依赖数据 | 是否依赖图片占位符 | 子组件 | 父组件 |
|--------|----------|----------|------|-------|-------|-----------|-------------|-----------------|--------|--------|
| LakeRiskMap | src/components/map/LakeRiskMap.tsx | 地图 | Leaflet地图+热力+设备点 | readings, selectedDeviceId, onSelectDevice, showHeat, showDevices | 无 | 否 | 是（DeviceReading[]） | 否（用CircleMarker替代marker图标） | MapContainer, TileLayer, HeatLayer, CircleMarker, MapLayerToggle, RiskLegend | MapMonitorPage |
| RiskLegend | src/components/map/RiskLegend.tsx | 地图 | 风险等级图例 | 无（固定数据） | 无 | 否 | 否（固定风险定义） | 否 | 无 | LakeRiskMap |
| SelectedDevicePanel | src/components/map/SelectedDevicePanel.tsx | 地图 | 选中设备详情面板 | reading: DeviceReading | 无 | 否 | 是（DeviceReading） | 是（设备插画占位符） | AquaPanel, RiskBadge, StatusBadge, ImagePlaceholder | MapMonitorPage |
| MapLayerToggle | src/components/map/MapLayerToggle.tsx | 地图 | 图层切换胶囊按钮组 | showDevices, showHeat, onToggleDevices, onToggleHeat | 无 | 否 | 否（接收状态） | 否 | 无 | LakeRiskMap |

### 15.5 数据分析页组件 (data/)

| 组件名 | 文件路径 | 所属页面 | 功能 | Props | State | 是否可复用 | 是否依赖数据 | 是否依赖图片占位符 | 子组件 | 父组件 |
|--------|----------|----------|------|-------|-------|-----------|-------------|-----------------|--------|--------|
| DataFilterBar | src/components/data/DataFilterBar.tsx | 数据 | 数据分析筛选栏 | onFilterChange? | FilterState (useState) | 否 | 否（内部state） | 是（导出图标） | AppSelect | DataAnalysisPage |
| MultiMetricTrendChart | src/components/data/MultiMetricTrendChart.tsx | 数据 | 多指标趋势图 | trendData: TrendPoint[] | 无 | 否 | 是（TrendPoint[]） | 是（异常警告图标） | AquaPanel, Recharts LineChart | DataAnalysisPage |
| SensorComparisonPanel | src/components/data/SensorComparisonPanel.tsx | 数据 | 传感器对比面板 | readings: DeviceReading[] | 无 | 否 | 是（DeviceReading[]） | 否 | AquaPanel | DataAnalysisPage |
| ToxinPredictionPanel | src/components/data/ToxinPredictionPanel.tsx | 数据 | AI预测模块 | 无（内部生成数据） | 无 | 否 | 是（内部useMemo生成） | 是（预测/置信度图标） | AquaPanel, Recharts AreaChart | DataAnalysisPage |

### 15.6 设备页组件 (device/)

| 组件名 | 文件路径 | 所属页面 | 功能 | Props | State | 是否可复用 | 是否依赖数据 | 是否依赖图片占位符 | 子组件 | 父组件 |
|--------|----------|----------|------|-------|-------|-----------|-------------|-----------------|--------|--------|
| DeviceToolbar | src/components/device/DeviceToolbar.tsx | 设备 | 设备操作工具栏 | onAdd, onRefresh | 无 | 否 | 否 | 是（添加/刷新图标） | AppButton | DevicePairingPage |
| DeviceCardGrid | src/components/device/DeviceCardGrid.tsx | 设备 | 设备卡片网格+DndContext | devices, onDragEnd, onConnect, onDisconnect, onDetails, onEdit, onDelete | 无 | 否 | 是（DeviceItem[]） | 否 | DndContext, SortableContext, DeviceCard | DevicePairingPage |
| DeviceCard | src/components/device/DeviceCard.tsx | 设备 | 单张设备卡片（含Sortable） | device: DeviceItem, onConnect, onDisconnect, onDetails, onEdit, onDelete | 无 | 是（每张设备1次实例化） | 是（DeviceItem） | 是（设备插画+WiFi/蓝牙图标） | StatusBadge, ImagePlaceholder, AppButton | DeviceCardGrid |
| DeviceSortDropZone | src/components/device/DeviceSortDropZone.tsx | 设备 | 拖拽排序提示区 | 无 | 无 | 否 | 否 | 否 | 无 | DevicePairingPage |
| PairingPanel | src/components/device/PairingPanel.tsx | 设备 | 右侧扫描配对面板 | isScanning, scanDone, discoveredDevices, onStartScan, onPair | 无 | 否 | 是（DiscoveredDevice[]） | 是（蓝牙雷达+器材占位） | AppButton, DiscoveredDeviceItem, ImagePlaceholder | DevicePairingPage |
| DeviceFormModal | src/components/device/DeviceFormModal.tsx | 设备 | 添加/编辑/详情/删除/连接模态框 | modal: DeviceModalState, editForm?, onClose, onSave, onDelete, onChange | 无 | 否 | 是（DeviceModalState） | 否 | AquaPanel, AppButton | DevicePairingPage |
| DiscoveredDeviceItem | src/components/device/DiscoveredDeviceItem.tsx | 设备 | 发现设备列表项 | device: DiscoveredDevice, onPair | 无 | 是（每项1次实例化） | 是（DiscoveredDevice） | 否 | AppButton | PairingPanel |

---

## 16. 素材占位符实现规范

### 16.1 占位符三大组件

所有图片和图标占位符统一使用以下三个组件实现：

#### ImagePlaceholder

```typescript
// src/components/common/ImagePlaceholder.tsx
interface ImagePlaceholderProps {
  width: number;           // 固定宽度 (px)
  height: number;          // 固定高度 (px)
  label: string;           // 占位文字（如 "萌物占位"）
  fileName?: string;       // 推荐素材文件名（如 "mascot-overview.png"）
  variant?: 'mascot' | 'device' | 'illustration' | 'decoration';
  rounded?: 'sm' | 'md' | 'lg' | 'full';
  className?: string;
}
```

**外观样式：**
- 背景：rgba(13, 125, 242, 0.03)
- 边框：2px dashed rgba(13, 125, 242, 0.12)
- 圆角：根据 variant 选择（mascot=16px, device=10px, illustration=12px, decoration=12px）
- 内部：flex column，居中
- 文字：9-10px，color #5A7184，opacity 0.6
- 可选小图标（根据 variant 选择默认 SVG）

**行为：**
- 始终占据设定的 width × height 空间
- 不因真实图片缺失而改变布局
- 可接受 `as` 属性或 children 来显示真实图片（未来替换）

#### IconPlaceholder

```typescript
// src/components/common/IconPlaceholder.tsx
interface IconPlaceholderProps {
  size: number;            // 图标尺寸 (px)，同时用于宽高
  label: string;           // 占位文字 / aria-label
  iconType?: 'wifi' | 'bluetooth' | 'battery' | 'signal' | 'warning' | 'check' | 'add' | 'refresh' | 'export' | 'location';
  color?: string;          // 图标颜色
  className?: string;
}
```

**外观：**
- 固定 size × size
- 内联 SVG 图标
- 颜色可配置
- 透明背景

#### EmptyAssetSlot

从旧项目迁移并扩展，保持兼容：

```typescript
// src/components/common/EmptyAssetSlot.tsx
interface EmptyAssetSlotProps {
  label: string;
  variant?: 'mascot' | 'icon' | 'illustration' | 'logo' | 'device' | 'microscope' | 'water';
  size?: 'sm' | 'md' | 'lg';  // sm=56px, md=80px, lg=112px
}
```

### 16.2 占位符实现规则

1. **所有图片和图标先用占位符组件显示**
2. **占位符必须拥有固定宽高**（不允许 `auto` 或 `fit-content`）
3. **占位符不能因为真实图片缺失而改变页面布局**
4. **占位符内部显示**：素材名称 + 推荐文件名 + 推荐尺寸
5. **图片加载失败时**：`<img>` 的 `onError` 事件触发，用占位符替换 src
6. **不允许代码直接假设图片一定存在**
7. **未来真实图片放入 Materials 后**，只需替换 assetMap 中的路径映射即可

### 16.3 建议 assetMap 结构

```typescript
// src/assets/assetMap.ts

// 当前所有素材路径指向占位符（空字符串 = 使用占位组件）
const PLACEHOLDER = ''; // 空字符串表示使用占位组件

const assetMap = {
  common: {
    logoOcean: PLACEHOLDER,           // "/Materials/General/logo-ocean.png"
    headerMascot: PLACEHOLDER,        // "/Materials/General/header-mascot.png"
    sidebarMascot: PLACEHOLDER,       // "/Materials/General/sidebar-mascot.png"
    navOverviewIcon: PLACEHOLDER,     // "/Materials/General/nav-overview.svg"
    navMapIcon: PLACEHOLDER,          // "/Materials/General/nav-map.svg"
    navDataIcon: PLACEHOLDER,         // "/Materials/General/nav-data.svg"
    navDeviceIcon: PLACEHOLDER,       // "/Materials/General/nav-device.svg"
    notificationIcon: PLACEHOLDER,    // "/Materials/General/notification-bell.svg"
  },
  overview: {
    systemShieldIcon: PLACEHOLDER,    // "/Materials/Overview/system-shield.svg"
    onlineIcon: PLACEHOLDER,          // "/Materials/Overview/icon-online.svg"
    idleIcon: PLACEHOLDER,            // "/Materials/Overview/icon-idle.svg"
    offlineIcon: PLACEHOLDER,         // "/Materials/Overview/icon-offline.svg"
    avgToxinIcon: PLACEHOLDER,        // "/Materials/Overview/icon-toxin.svg"
    riskIcon: PLACEHOLDER,            // "/Materials/Overview/icon-risk.svg"
    alertArrowIcon: PLACEHOLDER,      // "/Materials/Overview/icon-alert.svg"
  },
  map: {
    markerNormal: PLACEHOLDER,        // "/Materials/Map/marker-normal.svg"
    markerAttention: PLACEHOLDER,     // "/Materials/Map/marker-attention.svg"
    markerWarning: PLACEHOLDER,       // "/Materials/Map/marker-warning.svg"
    markerDanger: PLACEHOLDER,        // "/Materials/Map/marker-danger.svg"
    deviceIllustration: PLACEHOLDER,  // "/Materials/Map/device-illustration.png"
    layerIcon: PLACEHOLDER,           // "/Materials/Map/layer-icon.svg"
    locationIcon: PLACEHOLDER,        // "/Materials/Map/location-icon.svg"
  },
  data: {
    microscope: PLACEHOLDER,          // "/Materials/Data/microscope.png"
    trendWarningIcon: PLACEHOLDER,    // "/Materials/Data/trend-warning.svg"
    exportIcon: PLACEHOLDER,          // "/Materials/Data/export.svg"
    confidenceIcon: PLACEHOLDER,      // "/Materials/Data/confidence.svg"
    predictionIcon: PLACEHOLDER,      // "/Materials/Data/prediction.svg"
  },
  drive: {
    buoyDevice: PLACEHOLDER,          // "/Materials/Drive/buoy-device.png"
    probeDevice: PLACEHOLDER,         // "/Materials/Drive/probe-device.png"
    bluetoothScan: PLACEHOLDER,       // "/Materials/Drive/bluetooth-scan.svg"
    deviceMascot: PLACEHOLDER,        // "/Materials/Drive/device-mascot.png"
    labFlask: PLACEHOLDER,            // "/Materials/Drive/lab-flask.png"
    addIcon: PLACEHOLDER,             // "/Materials/Drive/add.svg"
    refreshIcon: PLACEHOLDER,         // "/Materials/Drive/refresh.svg"
    wifiIcon: PLACEHOLDER,            // "/Materials/Drive/wifi.svg"
    batteryIcon: PLACEHOLDER,         // "/Materials/Drive/battery.svg"
    signalIcon: PLACEHOLDER,          // "/Materials/Drive/signal.svg"
  },
} as const;

// 工具函数：检查素材路径是否可用
export function getAssetPath(path: string): string {
  // path 为空字符串 → 不可用 → 组件应使用占位符
  // path 非空 → 返回路径供 <img> 使用
  return path;
}

export function isAssetAvailable(path: string): boolean {
  return path !== PLACEHOLDER && path.length > 0;
}

export default assetMap;
```

**说明**：当前所有路径值为空字符串（`PLACEHOLDER`）。`ImagePlaceholder` 和 `IconPlaceholder` 组件内部调用 `isAssetAvailable()` 判断：如果 `true` 则渲染真实 `<img>`，如果 `false`（当前阶段）则显示占位符样式。未来只须将 `PLACEHOLDER` 替换为实际路径即可完成素材接入。

---

## 17. Vite 重构迁移步骤

### 步骤概览

按以下顺序执行，每步完成后验证通过再进行下一步。

### 第 1 步：审计旧项目

- **目标**：确认所有需要迁移的内容
- **涉及文件**：所有 `app/` 下的文件
- **注意事项**：
  - 标记 Next.js 专属代码：`next/link`、`next/image`、`next/navigation`、`next/dynamic`
  - 标记需要保留的业务逻辑和数据结构
  - 标记纯展示组件（可直接迁移）
- **验收方式**：输出迁移清单，统计需替换/保留/重写的文件数量

### 第 2 步：初始化 Vite React TypeScript 项目

- **目标**：在 `D:/iGEM-dry/web_tmp/` 创建项目骨架
- **涉及文件**：`package.json`, `index.html`, `vite.config.ts`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`, `postcss.config.mjs`
- **注意事项**：
  - 使用 `npm create vite@latest` 或手动创建
  - 选择 React + TypeScript 模板
  - 不要覆盖已有的 `WEB_REBUILD_SPEC.md`
  - 配置 Tailwind CSS v4（使用 `@import "tailwindcss"` 方式，不创建 `tailwind.config.js`）
- **验收方式**：`npm install` 成功，`npm run dev` 可打开默认 Vite 欢迎页

### 第 3 步：安装依赖

- **目标**：安装所有必需的 dependencies 和 devDependencies
- **涉及文件**：`package.json`
- **注意事项**：
  - 移除 `next`, `eslint-config-next` 等 Next.js 专属依赖
  - 安装版本见 [3.3 推荐依赖清单](#33-推荐依赖清单)
  - 安装后运行 `npm install`
- **验收方式**：`node_modules/` 中包含所有必需包，`npm ls` 无错误

### 第 4 步：建立 src 目录结构

- **目标**：按 [3.5 推荐项目结构](#35-推荐项目结构) 创建所有目录和占位文件
- **涉及文件**：所有 `src/` 下的目录
- **注意事项**：
  - 每个目录创建后放置 `.gitkeep` 或初始空文件
  - 确保路径拼写与本文档完全一致
- **验收方式**：`src/` 下所有目录结构存在

### 第 5 步：迁移 mock data

- **目标**：将 `demoReadings.ts` 从旧项目迁移到 `src/data/`
- **涉及文件**：
  - `src/data/demoReadings.ts`（新建，从旧 `app/lib/demoReadings.ts` 复制并调整导入路径）
- **注意事项**：
  - 保留所有类型定义、数据常量和工具函数
  - 将类型定义引用改为从 `src/types/domain.ts` 导入
  - 保留 `getRiskLevel`, `getRiskLabel`, `getRiskColor`, `getStatusText`, `getSignalLabel`, `normalizeHeatValue` 等工具函数
- **验收方式**：TypeScript 编译通过，导入路径正确

### 第 6 步：迁移类型定义

- **目标**：将所有 TypeScript 类型集中到 `src/types/domain.ts`
- **涉及文件**：
  - `src/types/domain.ts`（新建）
  - `src/types/leaflet-heat.d.ts`（从旧 `app/types/leaflet-heat.d.ts` 复制）
- **注意事项**：
  - 类型定义见 [第 12 章](#12-数据模型与字段规范)
  - 保持与 demoReadings.ts 的类型引用一致
- **验收方式**：TypeScript 编译通过

### 第 7 步：建立风险计算工具函数

- **目标**：将风险相关逻辑从 demoReadings 分离到 `src/utils/risk.ts`
- **涉及文件**：`src/utils/risk.ts`（新建）
- **注意事项**：
  - 从 `demoReadings.ts` 中提取 `getRiskLevel`, `getRiskLabel`, `getRiskColor`, `getStatusText`, `getSignalLabel` 到独立工具文件
  - `demoReadings.ts` 中重新从 `risk.ts` 导入这些函数
- **验收方式**：TypeScript 编译通过，行为与原有一致

### 第 8 步：建立全局样式 token

- **目标**：创建 CSS 设计变量和全局样式
- **涉及文件**：
  - `src/styles/tokens.css`（新建，CSS 变量定义）
  - `src/styles/globals.css`（新建，Tailwind 导入 + 全局样式）
  - `src/styles/layout.css`（新建，布局相关样式）
- **注意事项**：
  - 从旧 `app/globals.css` 迁移所有设计 token 和工具类
  - 移除 Next.js 特定引用
  - 保留 `.aqua-panel`, `.aqua-card`, `.aqua-button` 等工具类
  - 保留水波、气泡、占位符、Leaflet 覆盖样式
- **验收方式**：`npm run dev` 启动无 CSS 错误

### 第 9 步：建立 AppShell（全局布局）

- **目标**：实现 AppHeader + SidebarNav + MainContent 布局
- **涉及文件**：
  - `src/App.tsx`
  - `src/layouts/AppShell.tsx`
  - `src/layouts/AppHeader.tsx`
  - `src/layouts/SidebarNav.tsx`
- **注意事项**：
  - 使用 react-router-dom 的 `<Outlet />` 渲染子路由
  - 将 `next/link` 替换为 `react-router-dom` 的 `Link` / `NavLink`
  - 将 `usePathname()` 替换为 `useLocation()`
  - 全局装饰元素（背景渐变、光斑）在 AppShell 中实现
- **验收方式**：页面显示 Header + Sidebar + 内容区空壳，无报错

### 第 10 步：建立路由配置

- **目标**：配置 react-router-dom 路由
- **涉及文件**：
  - `src/main.tsx`（BrowserRouter 包裹）
  - `src/App.tsx`（Routes 定义）
  - `src/router/routes.tsx`（路由配置对象）
- **注意事项**：
  - 4 个路由：`/`、`/map`、`/data`、`/device`
  - 所有页面包裹在 AppShell 布局路由内
- **验收方式**：4 个路由均可访问（显示占位页面内容），导航切换正常

### 第 11 步：迁移通用组件

- **目标**：从旧项目迁移并适配通用组件
- **涉及文件**：
  - `src/components/common/AquaPanel.tsx`
  - `src/components/common/AquaCard.tsx`
  - `src/components/common/ImagePlaceholder.tsx`
  - `src/components/common/IconPlaceholder.tsx`
  - `src/components/common/EmptyAssetSlot.tsx`
  - `src/components/common/StatusBadge.tsx`
  - `src/components/common/RiskBadge.tsx`
  - `src/components/common/AppButton.tsx`
  - `src/components/common/AppSelect.tsx`
- **注意事项**：
  - 旧 MetricCard → 重命名为 MetricSummaryCard 并移到 overview/
  - 旧 SectionPanel → 重命名为 AquaPanel
  - 旧 MiniSparkline → 可选保留，当前阶段暂不使用
  - 移除所有 `"use client"` 指令（Vite 中不需要）
- **验收方式**：所有通用组件可正常导入和渲染

### 第 12 步：实现总览页

- **目标**：实现 OverviewPage 及其子组件
- **涉及文件**：
  - `src/pages/OverviewPage.tsx`
  - `src/components/overview/MetricSummaryCard.tsx`
  - `src/components/overview/SystemStatusPanel.tsx`
  - `src/components/overview/AlertSummaryPanel.tsx`
  - `src/components/overview/OverviewTrendChart.tsx`
  - `src/components/overview/LatestReadingsTable.tsx`
- **注意事项**：
  - 详细规格见 [第 8 章](#8-页面-1总览页详细规格)
  - 从 demoReadings 获取数据，不硬编码
  - "查看全部"按钮使用 react-router-dom `useNavigate()` 跳转
- **验收方式**：`/` 路由正常显示总览页全部内容

### 第 13 步：实现地图监视页

- **目标**：实现 MapMonitorPage 及其子组件
- **涉及文件**：
  - `src/pages/MapMonitorPage.tsx`
  - `src/components/map/LakeRiskMap.tsx`
  - `src/components/map/RiskLegend.tsx`
  - `src/components/map/SelectedDevicePanel.tsx`
  - `src/components/map/MapLayerToggle.tsx`
- **注意事项**：
  - 详细规格见 [第 9 章](#9-页面-2地图监视页详细规格)
  - Leaflet 核心代码从旧 MonitoringMap.tsx 迁移
  - 移除 `next/dynamic` 包装，改用 `React.lazy` 或在组件内直接使用
  - leaflet.heat 的导入方式保持不变
  - CSS marker 替代图片 marker
- **验收方式**：`/map` 路由正常显示地图+热力图+设备点+图例+详情面板

### 第 14 步：实现数据分析页

- **目标**：实现 DataAnalysisPage 及其子组件
- **涉及文件**：
  - `src/pages/DataAnalysisPage.tsx`
  - `src/components/data/DataFilterBar.tsx`
  - `src/components/data/MultiMetricTrendChart.tsx`
  - `src/components/data/SensorComparisonPanel.tsx`
  - `src/components/data/ToxinPredictionPanel.tsx`
- **注意事项**：
  - 详细规格见 [第 10 章](#10-页面-3数据分析页详细规格)
  - 从旧 `app/data/page.tsx` 和 `ToxinPredictionModel.tsx` 迁移代码
  - ToxinPredictionModel → ToxinPredictionPanel
- **验收方式**：`/data` 路由正常显示筛选栏+趋势图+传感器对比+AI预测

### 第 15 步：实现设备配对页

- **目标**：实现 DevicePairingPage 及其子组件
- **涉及文件**：
  - `src/pages/DevicePairingPage.tsx`
  - `src/components/device/DeviceToolbar.tsx`
  - `src/components/device/DeviceCardGrid.tsx`
  - `src/components/device/DeviceCard.tsx`
  - `src/components/device/DeviceSortDropZone.tsx`
  - `src/components/device/PairingPanel.tsx`
  - `src/components/device/DeviceFormModal.tsx`
  - `src/components/device/DiscoveredDeviceItem.tsx`
- **注意事项**：
  - 详细规格见 [第 11 章](#11-页面-4设备配对页详细规格)
  - 从旧 `app/device/page.tsx` 和 `DeviceStatus.tsx` 迁移代码
  - DeviceStatus → DeviceCard
  - 保留 @dnd-kit 拖拽排序逻辑
  - 保留所有模态框逻辑
- **验收方式**：`/device` 路由正常显示工具栏+设备卡片网格+扫描配对面板，拖拽和模态框可用

### 第 16 步：实现 mock service 层

- **目标**：创建 service 层，当前返回 mock data
- **涉及文件**：
  - `src/services/readingsService.ts`
  - `src/services/deviceService.ts`
- **注意事项**：
  - readingsService：封装从 demoReadings 获取数据的函数
  - deviceService：封装设备的 CRUD 操作（当前操作本地 state）
  - 每个函数返回 Promise，模拟异步行为（setTimeout 100-300ms）
  - 为未来替换为真实 API 调用做好准备
- **验收方式**：所有页面通过 service 层获取数据（非直接 import demoReadings）

### 第 17 步：实现图片占位符系统

- **目标**：确保所有图片/图标位置有正确的占位符
- **涉及文件**：
  - `src/assets/assetMap.ts`
  - 所有使用 ImagePlaceholder / IconPlaceholder 的组件
- **注意事项**：
  - 所有 assetMap 路径当前为 PLACEHOLDER（空字符串）
  - ImagePlaceholder 检测不到图片时显示占位样式
  - 不依赖 Materials/ 目录中的任何真实文件
- **验收方式**：所有页面中的图片/图标位置均有占位符，无布局塌陷

### 第 18 步：处理 Leaflet 样式和 marker 图标

- **目标**：确保 Leaflet 在 Vite 中正常工作
- **涉及文件**：
  - `src/styles/globals.css`（leaflet.css 导入）
  - `src/components/map/LakeRiskMap.tsx`
- **注意事项**：
  - 导入 `leaflet/dist/leaflet.css`
  - marker 使用 CSS CircleMarker，不使用图片 marker
  - leaflet.heat 类型声明文件迁移到 `src/types/`
  - 修复 Leaflet 默认图标路径问题（如果出现）
- **验收方式**：地图正常渲染，无 Leaflet 相关错误

### 第 19 步：配置 Vite 构建

- **目标**：配置路径别名和环境
- **涉及文件**：`vite.config.ts`
- **注意事项**：
  - 配置 `@` 别名指向 `src/`
  - 配置 base path（如需要）
  - 确保 Leaflet CSS 和图片资源正确打包
- **验收方式**：`npm run build` 成功

### 第 20 步：进行构建和验收

- **目标**：完整验收
- **涉及文件**：全部
- **注意事项**：见 [第 18 章验收标准](#18-验收标准)
- **验收方式**：所有验收项通过

---

## 18. 验收标准

### 18.1 技术验收

- [ ] `npm install` 成功，无依赖冲突
- [ ] `npm run dev` 成功，开发服务器正常启动
- [ ] `npm run build` 成功（`tsc -b && vite build`），无 TypeScript 关键错误
- [ ] `npm run preview` 成功，生产预览正常
- [ ] `npm run lint` 通过，无关键 ESLint 错误
- [ ] 浏览器控制台无红色运行时错误

### 18.2 页面验收

- [ ] `/` 正常显示总览页（5 个指标卡 + 3 个中部面板 + 最新采样表格）
- [ ] `/map` 正常显示地图监视页（Leaflet 地图 + 热力图 + 设备点 + 图例 + 选中设备详情面板）
- [ ] `/data` 正常显示数据分析页（筛选栏 + 趋势图 + 传感器对比 + AI 预测 + 置信度摘要）
- [ ] `/device` 正常显示设备配对页（工具栏 + 设备卡片网格 + 拖拽排序 + 扫描配对面板 + 模态框）
- [ ] 4 个页面之间通过 Header 导航和 Sidebar 导航可以正常切换
- [ ] 不存在的路由显示 404 信息

### 18.3 视觉验收

- [ ] 四页整体布局接近目标设计蓝图的布局结构和信息层级
- [ ] 使用浅色青蓝水体实验风（近白背景 + 浅蓝渐变 + 白色面板 + 细蓝边框）
- [ ] Header（88px 高，Logo+标题+导航+用户区）、Sidebar（200-220px 宽，图标导航+装饰）、MainContent 布局在所有页面保持一致
- [ ] 卡片（圆角 10px、轻阴影、白底、细蓝边框）、按钮（蓝色渐变主按钮、白底蓝边次按钮）、图表、表格风格统一
- [ ] 所有图片和图标即使 Materials 目录为空，也有正确尺寸的占位符（虚线框+浅蓝底+文字标注）
- [ ] 页面不会因为 Materials 为空而出现布局错位或报错
- [ ] 风险等级颜色统一（正常绿、关注黄、警戒橙、高风险红）
- [ ] 不出现深色赛博网格或大面积深色卡片

### 18.4 功能验收

**总览页：**
- [ ] 5 个顶部指标卡显示正确数据（在线数、空闲数、离线数、平均藻毒素、最高风险）
- [ ] 系统状态面板显示盾牌图标和三项状态摘要
- [ ] 告警摘要面板显示 4 行告警项（高/警/关/离）
- [ ] 趋势概览面板显示 Recharts 面积图 + 两条阈值线
- [ ] 最新采样表格显示 5 行数据，7 列完整

**地图监视页：**
- [ ] Leaflet 底图正常加载（OpenStreetMap tiles）
- [ ] 设备点位 Marker 正确显示（颜色按风险等级）
- [ ] 热力图层可切换（显示/隐藏）
- [ ] 设备图层可切换（显示/隐藏）
- [ ] 点击设备点 → 右侧详情面板更新
- [ ] 风险图例在地图底部显示
- [ ] 定位按钮可用
- [ ] 缩放按钮可用
- [ ] 地图无 SSR 相关错误（Vite 天然无此问题）

**数据分析页：**
- [ ] 筛选栏（时间范围/设备/传感器选择器 + 导出按钮）可见
- [ ] 趋势分析图显示 4 条线 + 2 条阈值线
- [ ] 异常高值点有红色警告标注
- [ ] 传感器对比面板按毒素浓度降序排列
- [ ] AI 预测图显示历史数据(实线) + 预测数据(虚线) + 置信区间
- [ ] 右侧置信度摘要卡显示 87%、预测区间、高风险时间
- [ ] 爆发预警提示卡片可见

**设备配对页：**
- [ ] 工具栏（添加/刷新/批量操作按钮）可见
- [ ] 设备卡片网格正常（3 列 / 响应式）
- [ ] 每张设备卡片显示完整信息（插画占位、名称、状态、3 指标、电量、信号、操作按钮）
- [ ] 拖拽排序功能正常（@dnd-kit）
- [ ] 详情/编辑/删除模态框可正常弹出和关闭
- [ ] 蓝牙连接按钮 → 加载动画 → 设备状态变更
- [ ] WiFi 连接按钮 → 加载动画 → 设备状态变更
- [ ] 断开连接按钮 → 设备变离线灰色态
- [ ] 右侧配对面板显示雷达圆环 + 扫描按钮 + 发现设备列表
- [ ] 扫描按钮 → 雷达动画 → 2s 后显示结果
- [ ] 蓝牙配对/WiFi连接按钮 → 加载动画 → 新设备添加到列表

### 18.5 响应式与边界验收

- [ ] 桌面端 1280px - 1600px 显示效果最佳，无水平溢出
- [ ] 1024px 宽度下 Sidebar 可切换为窄图标栏或隐藏，内容区纵向堆叠不溢出
- [ ] 关键数据不被装饰图/吉祥物占位符遮挡
- [ ] 所有按钮有可读文本或 title/aria-label
- [ ] 图表图例有文字
- [ ] hover/focus 状态清晰可辨识

---

## 19. 缺失信息与待确认问题

| 编号 | 问题 | 无法确认的原因 | 建议默认方案 | 是否阻塞重构 |
|------|------|---------------|-------------|------------|
| 1 | 设计蓝图中具体元素的精确像素尺寸 | 设计蓝图图片无法通过工具精确测量 | 使用本文档推荐的尺寸范围（如 Header 88px、Sidebar 200px），后续可根据实际效果微调 | 否 |
| 2 | 吉祥物和插画的具体视觉风格 | 当前没有真实美术资产 | 使用占位符标注，不阻塞功能开发。未来美术资产到位后替换 assetMap 即可 | 否 |
| 3 | 设备卡片的具体设备类型分类 | 旧项目数据中设备名已隐含类型（浮标/探针/巡检器），但无独立 type 字段 | 在编辑模态框中提供设备类型选择（浮标/探针/岸线巡检器/其他），但不强制关联到数据模型 | 否 |
| 4 | 地图初始中心点和缩放级别 | 旧项目使用武汉东湖坐标 (30.5667, 114.3833) zoom 13 | 保持旧项目坐标作为演示数据 | 否 |
| 5 | "批量操作"的具体功能 | 设计蓝图有该按钮但旧项目未实现功能 | 当前阶段为占位按钮，点击后 alert("批量操作功能将在后续版本中实现") | 否 |
| 6 | 数据导出格式和范围 | 设计蓝图有导出按钮但未定义导出格式 | 当前阶段为占位按钮，点击后 alert("导出功能将在后端接入后启用") | 否 |
| 7 | 数据分析页筛选栏是否需要实际过滤功能 | 当前阶段无后端，且目标图可能仅为静态展示 | 筛选栏 UI 交互正常，但暂不实施数据过滤逻辑。select 变更更新 FilterState 但图表数据不变 | 否 |
| 8 | react-leaflet v5 与 Leaflet v1.9.x 的兼容性 | react-leaflet v5 需要特殊处理 | 使用 `React.lazy` 动态导入地图组件，确保 Leaflet 仅在客户端加载 | 否 |
| 9 | Tailwind CSS v4 在 Vite 中的配置方式 | Tailwind v4 使用 `@import "tailwindcss"` 而非 v3 的配置文件方式 | 在 `src/styles/globals.css` 顶部 `@import "tailwindcss"`，在 `postcss.config.mjs` 中配置 `@tailwindcss/postcss` 插件 | 否 |
| 10 | 字体选择 | 项目面向中文用户且为 iGEM 展示 | 使用系统默认中文字体栈：`"PingFang SC", "Microsoft YaHei", "Noto Sans SC", Arial, Helvetica, sans-serif` | 否 |
| 11 | 设计蓝图中水波装饰的具体实现方式 | 设计蓝图无法确定是 CSS 实现还是图片资源 | 使用 CSS 实现（渐变 + 伪元素），不依赖图片。如未来有 SVG 素材可增强效果 | 否 |
| 12 | Recharts 版本选择 | 旧项目使用 recharts 3.8.1，新版本可能有 breaking changes | 使用 recharts 2.x 最新稳定版，API 与旧项目代码兼容 | 否 |

---

> **文档结束**
>
> 本文档基于以下源材料编写：
> - `planning/PROJECT.md`（项目说明与约束）
> - `TODO.md`（视觉改造任务分解）
> - 四张设计蓝图（总览页、地图监视页、数据分析页、设备配对页目标图）
> - 当前项目全部源代码（14 个组件、4 个页面、数据文件、样式文件）
> - 用户新增技术路线要求（Vite + React 替代 Next.js）
>
> 后续 Agent 应在 `D:/iGEM-dry/web_tmp/` 空白工作目录中，严格按照本文档的规格进行编码。所有不确定的细节均已在第 19 章列出建议默认方案。
