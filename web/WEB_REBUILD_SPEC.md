# 网页重构有效信息文档 / Web Rebuild Specification

## 一、项目目标摘要

- **项目是什么**：面向 iGEM 干实验团队的水体藻毒素监测 Dashboard，是一个可操作的数据监控平台，不是宣传落地页。
- **面向谁使用**：iGEM 干实验团队成员，用于实时查看水体采样设备的运行状态、地理位置分布和历史数据分析。
- **为什么要重构**：当前项目基于 Next.js 16 + React 19，存在 SSR 水合风险、包体积大、未来难以迁移到桌面/移动端应用等问题。同时现有暗色科技风 UI 需要全面更换为浅色青蓝水体实验风，以匹配新的四张设计蓝图。
- **为什么从 Next.js 迁移到 Vite**：
  - 避免 SSR 在图表（Recharts）和地图（Leaflet）上的水合错误；
  - 减少包体积，提升构建速度；
  - 提供纯静态产物，以便未来无缝通过 Tauri/Capacitor 转化为手机应用；
  - 便于未来适配 Rust 后端，无需受限于 Next.js 的 Node.js 运行时。
- **新网页需要保留哪些核心功能**：
  - 四页路由：总览、地图监视、数据分析、设备配对；
  - 设备统计指标卡、告警摘要、趋势概览、最新采样表格；
  - 真实地理地图 + 热力图 + 设备点位 + 右侧详情面板；
  - 数据分析三 Y 轴趋势图、传感器对比、AI 预测；
  - 设备卡片网格、拖拽排序、扫描配对、CRUD 模拟。
- **新网页视觉上要达到什么效果**：严格还原四张设计蓝图，采用浅色青蓝水体实验风，白色/浅蓝背景，青蓝主强调色，卡片圆角大、阴影轻，整体清新、专业、具有实验室科技感。所有吉祥物、装饰图即使缺失也必须以占位符形式参与正常排版。
- **当前阶段不做哪些事情**：
  - 不接真实后端 API；不接数据库；不接 WebSocket；不做真实硬件通信；
  - 不做用户认证/登录；不做数据持久化（刷新重置）；不做邮件/短信告警通知。

## 二、信息来源与优先级

### 已读取的文件与图片

| 来源 | 路径 | 用途 |
|------|------|------|
| 新增要求文档 | `/iGEM-dry/prompt_1.md` | 重构任务说明与文档规范 |
| 项目说明 | `/iGEM-dry/viewweb/planning/PROJECT.md` | 现有功能范围、页面范围、数据来源、交互能力、验收标准 |
| 项目结构说明 | `/iGEM-dry/viewweb/PROJECT_STRUCTURE.md` | 旧项目目录结构、组件说明、数据流、样式体系 |
| 依赖清单 | `/iGEM-dry/viewweb/package.json` | 分析当前依赖，标记保留/移除/新增 |
| 总览页代码 | `/iGEM-dry/viewweb/app/page.tsx` | 旧总览页实现（暗色风，统计卡+最新采样+风险说明） |
| 地图页代码 | `/iGEM-dry/viewweb/app/map/page.tsx` | 旧地图页入口 |
| 地图 Dashboard | `/iGEM-dry/viewweb/app/map/MapDashboard.tsx` | 地图页主控制器、MetricChart、选中设备详情 |
| 地图组件 | `/iGEM-dry/viewweb/app/map/MonitoringMap.tsx` | react-leaflet 热力图、CircleMarker、Popup 实现 |
| 地图加载器 | `/iGEM-dry/viewweb/app/map/MapClientLoader.tsx` | next/dynamic SSR 隔离（需替换） |
| 数据分析页 | `/iGEM-dry/viewweb/app/data/page.tsx` | 旧数据分析页（统计卡+排行+设备健康+阈值） |
| 设备页代码 | `/iGEM-dry/viewweb/app/device/page.tsx` | 旧设备页（拖拽排序、模态框、添加/连接模拟） |
| 导航栏 | `/iGEM-dry/viewweb/app/components/Navbar.tsx` | 旧顶部胶囊导航（需迁移为双导航） |
| 设备状态卡 | `/iGEM-dry/viewweb/app/components/DeviceStatus.tsx` | 旧设备卡片组件（暗色风，可迁移逻辑） |
| AI 预测组件 | `/iGEM-dry/viewweb/app/components/ToxinPredictionModel.tsx` | 旧 AreaChart 预测占位版（可迁移图表逻辑） |
| 核心数据文件 | `/iGEM-dry/viewweb/app/lib/demoReadings.ts` | 14 台模拟设备、历史数据、风险计算工具函数 |
| 全局样式 | `/iGEM-dry/viewweb/app/globals.css` | Tailwind v4 导入、暗色变量、Leaflet popup 覆盖 |
| 根布局 | `/iGEM-dry/viewweb/app/layout.tsx` | 暗色背景、科技网格、环境光晕、Navbar 挂载 |
| TypeScript 配置 | `/iGEM-dry/viewweb/tsconfig.json` | 旧 Next.js tsconfig（需替换） |
| Next.js 配置 | `/iGEM-dry/viewweb/next.config.ts` | 空配置 |
| 设计蓝图 | `/iGEM-dry/viewweb/designe-figure/Page_design_objective/总览页目标.png` | 新视觉总览页 |
| 设计蓝图 | `/iGEM-dry/viewweb/designe-figure/Page_design_objective/地图监视页目标.png` | 新视觉地图页 |
| 设计蓝图 | `/iGEM-dry/viewweb/designe-figure/Page_design_objective/数据分析页目标.png` | 新视觉数据分析页 |
| 设计蓝图 | `/iGEM-dry/viewweb/designe-figure/Page_design_objective/设备配对页目标.png` | 新视觉设备配对页 |

### 信息优先级

1. **用户当前新增要求**（prompt_1.md）> 2. **四张目标设计蓝图** > 3. **PROJECT.md 中的功能范围和验收标准** > 4. **当前项目源代码** > 5. **可推断的前端最佳实践**

> **冲突处理原则**：如果 PROJECT.md 和本次重构要求冲突，则功能保留参考 PROJECT.md，技术路线以 React + Vite 为准。视觉风格以四张设计蓝图为绝对基准，废弃 PROJECT.md 中的暗色科技风描述。

## 三、技术路线

### 1. 目标技术栈表格

| 类别 | 技术 | 用途 | 是否必须 | 备注 |
|------|------|------|----------|------|
| 构建工具 | Vite | 前端构建与开发服务器 | 必须 | 替代 Next.js，输出纯静态产物 |
| UI 框架 | React 18.x | 组件化 UI | 必须 | 稳定版以确保 Leaflet/Recharts 兼容；旧项目为 19.x 需降级 |
| 类型系统 | TypeScript | 类型安全 | 必须 | 保持 strict 模式 |
| 路由 | react-router-dom | SPA 路由 | 必须 | 替代 Next.js App Router |
| 样式 | Tailwind CSS v4 | 原子化 CSS | 必须 | 使用 `@import "tailwindcss"` 语法，`@theme` 定义变量 |
| 图表 | Recharts | 折线/面积/多轴图表 | 必须 | 趋势图、AI 预测图 |
| 地图 | Leaflet + react-leaflet | 地理地图渲染 | 必须 | 替代 next/dynamic SSR 隔离方案 |
| 热力图 | leaflet.heat | 插值热力图层 | 必须 | 需自行处理 SPA 路由切换时的图层清理 |
| 拖拽 | @dnd-kit/core + @dnd-kit/sortable | 设备卡片拖拽排序 | 必须 | 保持 PointerSensor 5px 激活距离 |
| 图标 | lucide-react | 矢量图标 | 必须 | 替代内联 SVG，统一图标源 |
| 状态管理 | React useState/useMemo | 组件级状态 | 必须 | 当前无需 Redux/Zustand |
| 数据来源 | mock data (demoReadings.ts) | 前端模拟数据 | 必须 | 不接真实后端 |
| 未来 API 层 | src/services/* | 预留 service 层 | 必须 | 当前返回 mock data，未来可替换为真实 API |
| 构建与部署 | Vite build + preview | 静态产物 | 必须 | 输出到 dist/ |

### 2. Next.js 到 Vite 的迁移说明

| 旧技术 | 新技术 | 替换原因 | 迁移注意事项 |
|--------|--------|----------|--------------|
| Next.js 16 App Router | react-router-dom | SPA 路由更轻量，避免 SSR 水合问题 | 移除 `app/` 目录，改用 `src/pages/` + `src/router/routes.tsx` |
| `next/link` | `react-router-dom` 的 `<Link>` | 路由库切换 | 全局替换 import 与使用方式 |
| `next/image` | 原生 `<img>` 或自定义 ImagePlaceholder | Vite 无 next/image | 图片统一走 `/Materials/` 静态目录 |
| Next.js API routes | 前端 mock service | 当前不接后端 | 在 `src/services/` 中返回 mock data |
| SSR / Server Component | 全部客户端组件 | Leaflet/Recharts 依赖浏览器 API | 移除 `'use client'` 区分，所有组件均在浏览器执行 |
| `app/layout.tsx` | `src/layouts/AppShell.tsx` | 布局结构迁移 | 全局装饰、Header、Sidebar 统一在 AppShell 中管理 |
| `app/page.tsx` | `src/pages/OverviewPage.tsx` | 文件路由迁移 | 路由映射：`/` 对应 OverviewPage |
| `next/dynamic(ssr: false)` | 条件渲染/懒加载 | Vite 无 next/dynamic | 地图组件直接导入，通过环境判断或 useEffect 延迟加载 |

### 3. 推荐依赖清单

**dependencies**：`react@^18.3.1`, `react-dom@^18.3.1`, `react-router-dom@^6.26.0`, `recharts@^2.12.7`, `leaflet@^1.9.4`, `react-leaflet@^4.2.1`, `leaflet.heat@^0.2.0`, `@dnd-kit/core@^6.3.1`, `@dnd-kit/sortable@^10.0.0`, `@dnd-kit/utilities@^3.2.2`, `lucide-react@^0.446.0`

**devDependencies**：`vite@^5.4.0`, `@vitejs/plugin-react@^4.3.0`, `typescript@^5.5.0`, `tailwindcss@^4.0.0`, `@tailwindcss/postcss@^4.0.0`, `postcss@^8.4.0`, `@types/react@^18.3.0`, `@types/react-dom@^18.3.0`, `@types/leaflet@^1.9.21`, `eslint@^9.0.0`, `@eslint/js@^9.0.0`, `typescript-eslint@^8.0.0`, `eslint-plugin-react-hooks@^5.0.0`, `eslint-plugin-react-refresh@^0.4.0`

> 安装 Recharts 和 React Leaflet 时如遇 peer deps 冲突，请使用 `--legacy-peer-deps`。

### 4. 推荐脚本命令

```json
{
  "dev": "vite",
  "build": "tsc && vite build",
  "preview": "vite preview",
  "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
}
```

### 5. 推荐项目结构

```
/iGEM-dry/web
  package.json, index.html, vite.config.ts, tsconfig.json, postcss.config.mjs, eslint.config.js
  public/Materials/{General,Overview,Map,Data,Drive}/
  src/
    main.tsx, App.tsx
    router/routes.tsx
    layouts/{AppShell.tsx,AppHeader.tsx,SidebarNav.tsx,PageFrame.tsx}
    pages/{OverviewPage.tsx,MapMonitorPage.tsx,DataAnalysisPage.tsx,DevicePairingPage.tsx}
    components/
      common/{AquaPanel.tsx,AquaCard.tsx,IconPlaceholder.tsx,ImagePlaceholder.tsx,StatusBadge.tsx,RiskBadge.tsx,EmptyAssetSlot.tsx,AppButton.tsx,AppSelect.tsx}
      overview/{MetricSummaryCard.tsx,SystemStatusPanel.tsx,AlertSummaryPanel.tsx,OverviewTrendChart.tsx,LatestReadingsTable.tsx}
      map/{LakeRiskMap.tsx,RiskLegend.tsx,SelectedDevicePanel.tsx,MapLayerToggle.tsx,MapMarkerPlaceholder.tsx,MapController.tsx}
      data/{DataFilterBar.tsx,MultiMetricTrendChart.tsx,SensorComparisonPanel.tsx,ToxinPredictionPanel.tsx}
      device/{DeviceToolbar.tsx,DeviceCardGrid.tsx,DeviceCard.tsx,DeviceSortDropZone.tsx,PairingPanel.tsx,DeviceFormModal.tsx,DiscoveredDeviceItem.tsx,RadarScanner.tsx}
    data/{demoReadings.ts,mockDevices.ts,mockHistory.ts,mockPredictions.ts}
    services/{readingsService.ts,deviceService.ts,predictionService.ts}
    types/domain.ts
    utils/{risk.ts,format.ts,chart.ts}
    styles/{tokens.css,globals.css,layout.css}
    assets/assetMap.ts
```

## 四、整体视觉设计系统

### 1. 色彩 token 与 Tailwind v4 主题定义

在 `src/styles/tokens.css` 中定义：

```css
@import "tailwindcss";

@theme inline {
  --color-bg: #f0f7ff;
  --color-bg-soft: #e6f2ff;
  --color-surface: #ffffff;
  --color-surface-strong: #f8fbff;
  --color-border: #d0e3f5;
  --color-border-subtle: #e8f1fa;
  --color-primary: #0ea5e9;
  --color-primary-strong: #0284c7;
  --color-mint: #34d399;
  --color-warning: #f59e0b;
  --color-danger: #ef4444;
  --color-attention: #f97316;
  --color-normal: #22c55e;
  --color-text: #0f172a;
  --color-muted: #64748b;
  --color-text-inverse: #ffffff;
  --color-chart-toxin: #0ea5e9;
  --color-chart-temp: #34d399;
  --color-chart-ph: #8b5cf6;
  --color-chart-prediction: #6366f1;
  --font-sans: "Inter", "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-mono: "JetBrains Mono", "Courier New", monospace;
  --shadow-card: 0 2px 12px rgba(14, 165, 233, 0.08);
  --shadow-float: 0 8px 32px rgba(14, 165, 233, 0.12);
  --shadow-hover: 0 4px 20px rgba(14, 165, 233, 0.15);
}
```

> 在 `globals.css` 中通过 `@import "./tokens.css"` 引入，并在 `body` 上应用 `bg-bg text-text`。

### 2. 字体规范

| 用途 | 字号 | 字重 | 行高 | 颜色 |
|------|------|------|------|------|
| 页面标题 | 24px - 28px | 700 | 1.3 | --color-text |
| 导航文字（顶部激活） | 14px - 15px | 600 | 1.4 | --color-primary |
| 导航文字（顶部未激活） | 13px | 500 | 1.4 | --color-muted |
| 侧边栏导航 | 14px | 500 | 1.5 | --color-text / --color-muted |
| 卡片标题 | 16px - 18px | 700 | 1.4 | --color-text |
| 主数据数字（指标卡） | 32px - 40px | 800 | 1.1 | --color-text / --color-primary / --color-danger |
| 表格文字 | 13px - 14px | 400 | 1.5 | --color-text |
| 辅助说明文字 | 12px - 13px | 400 | 1.5 | --color-muted |
| Badge 文字 | 11px - 12px | 600 | 1.2 | 跟随状态色 |
| 图表轴标签 | 11px - 12px | 400 | 1.2 | --color-muted |

### 3. 间距规范

| 场景 | 数值 |
|------|------|
| 页面外框内边距 | 24px - 32px |
| Header 内边距 | 16px 32px |
| Sidebar 内边距 | 16px 12px |
| 卡片间距（grid gap） | 16px - 24px |
| 卡片内部 padding | 20px - 24px |
| 表格行高 | 48px - 52px |
| 图表容器 padding | 16px - 20px |
| 图标与文字间距 | 8px |
| 指标卡之间间距 | 16px - 20px |
| 主内容区与 Sidebar 间距 | 24px |

### 4. 圆角规范

| 场景 | 数值 |
|------|------|
| 页面外框圆角 | 24px |
| 卡片圆角 | 16px - 20px |
| 按钮圆角 | 10px - 12px |
| Badge 圆角 | 6px - 8px |
| 输入框/选择器圆角 | 8px - 10px |
| 导航胶囊圆角 | 24px（整体）/ 10px（单个项） |
| 图片占位符圆角 | 12px - 16px |

### 5. 阴影规范

| 场景 | 阴影值 |
|------|--------|
| 卡片阴影 | `0 2px 12px rgba(14, 165, 233, 0.08)` |
| 浮层阴影 | `0 8px 32px rgba(14, 165, 233, 0.12)` |
| 按钮 hover 阴影 | `0 4px 16px rgba(14, 165, 233, 0.18)` |
| 选中卡片阴影 | `0 0 0 2px var(--color-primary), 0 4px 20px rgba(14, 165, 233, 0.15)` |
| 地图容器阴影 | `0 4px 24px rgba(0, 0, 0, 0.08)` |

### 6. 边框规范

| 场景 | 边框值 |
|------|--------|
| 页面外框 | 1px solid `--color-border` |
| 卡片边框 | 1px solid `--color-border-subtle` |
| 表格边框 | 无整体边框，行底部分隔线 1px solid `--color-border-subtle` |
| 图表容器边框 | 1px solid `--color-border-subtle` |
| 选中态边框 | 2px solid `--color-primary` |
| 拖拽虚线边框 | 2px dashed `--color-primary` opacity 0.4 |

### 7. 状态色规范

| 状态 | 色值 | 用途 |
|------|------|------|
| online | `#22c55e` | 在线设备圆点、状态文字 |
| idle | `#f59e0b` | 待机/空闲设备圆点、状态文字 |
| offline | `#94a3b8` | 离线设备圆点、状态文字 |
| normal | `#22c55e` | 正常风险 |
| attention | `#f59e0b` | 关注风险 (0.5 - 1.0 µg/L) |
| warning | `#f97316` | 警戒风险 (1.0 - 5.0 µg/L) |
| danger | `#ef4444` | 高风险 (> 5.0 µg/L) |

> 风险色统一使用 `src/utils/risk.ts` 中的 `getRiskColor` 函数获取，严禁组件内硬编码。

### 8. 插画和吉祥物视觉边界溢出规范（还原度核心指标）

- **插画风格**：浅色扁平可爱风，与 Wiki 协调，配色以青蓝、薄荷绿、白色为主。
- **出现位置**：严格比对蓝图排版。
  - 总览页：Header 右上角小吉祥物；Sidebar 底部大吉祥物。
  - 地图页：Header 右上角小吉祥物；右下角设备/吉祥物占位符。
  - 数据分析页：Sidebar 底部显微镜/实验器材；左下角显微镜装饰。
  - 设备配对页：Sidebar 底部大吉祥物；右下角实验器材/吉祥物占位符。
- **边界溢出控制规约**：
  - 设计图中如右上方、左下方等部分的吉祥物采用了**破格、溢出容器边界（Overlap）**的视觉特效。
  - 承载吉祥物素材组件的父级容器必须显式配置为 `relative overflow-visible`。
  - 吉祥物自身使用 `absolute` 定位并设定高层级 `z-index`（建议 20 - 50）。
  - **严禁误用 `overflow-hidden` 导致吉祥物被切体截断**。
  - 必须保障其图层绝不遮挡底层核心监控数据的交互与视线（如点击、hover、tooltip）。
  - 若吉祥物区域与功能按钮重叠，吉祥物应置于按钮下方（较低 z-index）或通过 `pointer-events-none` 穿透点击。

## 五、全局布局规范

### 设计基准

- 桌面端主设计基准：**1536px × 960px**（视口可用区域）。
- 页面最大宽度：`max-width: 1536px`，居中 `mx-auto`。
- 整体为左右布局：左侧 Sidebar + 右侧主内容区。

### 1. PageFrame

- **组件名**：`PageFrame`
- **位置**：页面最外层容器，包裹在 `AppShell` 内部。
- **宽高**：宽度 100%，高度 `100vh`（或 `min-h-screen`）。
- **圆角**：页面外框整体圆角 `24px`（仅当作为窗口应用时可见，全屏浏览器可忽略）。
- **边框**：`1px solid var(--color-border)`。
- **背景**：`var(--color-bg)`（`#f0f7ff`），带有极淡的水波/网格装饰背景（CSS 渐变或 SVG 背景图，opacity 0.3 - 0.5）。
- **水波装饰**：在 `PageFrame` 底层放置绝对定位的半透明波浪 SVG 或 CSS 渐变弧形，作为全局氛围装饰。

### 2. Header（AppHeader）

- **组件名**：`AppHeader`
- **位置**：页面顶部，横向贯穿整个 PageFrame。
- **高度**：`80px - 96px`（推荐 `88px`）。
- **左侧 Logo 区域宽度**：`240px - 280px`。
  - Logo 图标占位符：`48px × 48px`，圆角 `12px`。
  - 标题文字："水体藻毒素监测平台"，字号 `18px - 20px`，字重 700，颜色 `--color-text`。
- **顶部导航位置**：Header 中部偏右，与左侧 Logo 区域保持 `auto` 间距（flex 居中或靠右）。
  - 导航整体为一个圆角胶囊容器（圆角 `24px`），背景 `rgba(255,255,255,0.6)`，边框 `1px solid var(--color-border)`，backdrop-blur。
  - 每个导航项：高度 `40px - 44px`，激活态宽度 `100px - 120px`，未激活态宽度 `80px - 90px`。
  - 激活态：浅蓝背景 `rgba(14,165,233,0.12)`，文字 `--color-primary`，圆角 `10px`。
- **用户区域位置**：Header 最右侧。
  - 通知按钮：`40px × 40px`，图标 `20px × 20px`（铃铛）。
  - 用户胶囊：高度 `36px - 40px`，包含头像占位符 `28px × 28px` + 文字 "iGEM Team" + 下拉箭头。
- **右上角吉祥物占位符位置与尺寸**：
  - 位置：`AppHeader` 右侧边缘，向下延伸溢出 Header 下边界。
  - 尺寸：`84px × 84px`（小吉祥物）。
  - z-index：`30`。
  - 父容器必须 `overflow-visible`。

### 3. Sidebar（SidebarNav）

- **组件名**：`SidebarNav`
- **位置**：PageFrame 左侧，紧贴 Header 下方。
- **宽度**：`200px - 220px`（推荐 `210px`）。
- **顶部起始位置**：Header 底部下方（`top: 88px` 或 `mt-0` 如果在同一 flex 容器内）。
- **背景**：半透明 `rgba(255,255,255,0.5)`，backdrop-blur，`border-right: 1px solid var(--color-border)`。
- **每个导航项尺寸**：高度 `48px - 52px`，宽度 `100%`（含 padding）。
- **导航项间距**：项与项之间 `gap: 4px - 8px`。
- **当前激活态样式**：
  - 左侧边框发光：`border-left: 3px solid var(--color-primary)`。
  - 背景：`rgba(14,165,233,0.08)`。
  - 文字颜色：`--color-primary`。
  - 圆角：`0 10px 10px 0`（仅右侧圆角）。
- **未激活态样式**：文字 `--color-muted`，hover 背景 `rgba(14,165,233,0.04)`。
- **底部装饰占位符位置与尺寸**：
  - 位置：Sidebar 底部居中。
  - 大吉祥物占位符：`160px × 220px`。
  - 水波装饰：宽度 `180px`，高度 `40px`，位于吉祥物下方。
  - 气泡装饰：数个 `12px - 20px` 的圆形，散布在 Sidebar 中下部，opacity 0.3。
  - z-index：`20`。
  - 父容器 `overflow-visible`。

### 4. MainContent

- **组件名**：`MainContent`
- **位置**：Sidebar 右侧，Header 下方。
- **左侧与 Sidebar 的关系**：`margin-left: 210px`（与 Sidebar 宽度一致），或 flex 布局中 `flex-1`。
- **顶部与 Header 的关系**：`margin-top: 0`，内容区从 Header 底部开始。
- **内容区 padding**：`24px - 32px`。
- **页面最大宽度**：`1536px - 210px = 1326px` 可用内容宽度。
- **滚动规则**：`overflow-y: auto`，独立滚动条，不影响 Sidebar 和 Header。

### 5. 全局装饰元素

| 元素名称 | 推荐文件名 | 放置路径 | 页面位置 | 宽度 | 高度 | z-index | 是否可点击 | 缺失 fallback 文本 |
|----------|-----------|----------|----------|------|------|---------|-----------|-------------------|
| Logo 占位符 | `logo-ocean.png` | `/Materials/General/` | AppHeader 左侧 | 48px | 48px | 10 | 否 | "LOGO" |
| Header 小吉祥物占位符 | `mascot-header-small.png` | `/Materials/General/` | AppHeader 右上角，溢出边界 | 84px | 84px | 30 | 否 | "吉祥物" |
| Sidebar 大吉祥物占位符 | `mascot-sidebar-large.png` | `/Materials/General/` | SidebarNav 底部 | 160px | 220px | 20 | 否 | "吉祥物" |
| 气泡装饰占位符 | `bubble.png` | `/Materials/General/` | Sidebar 中下部、页面角落 | 16px | 16px | 5 | 否 | "●" |
| 水波装饰占位符 | `wave.png` | `/Materials/General/` | Sidebar 底部、页面底部 | 180px | 40px | 5 | 否 | "〰" |
| 实验器材装饰占位符（数据分析页） | `microscope-decoration.png` | `/Materials/Data/` | 数据分析页左下角 | 120px | 120px | 15 | 否 | "显微镜" |
| 实验器材装饰占位符（设备页） | `lab-flask-decoration.png` | `/Materials/Drive/` | 设备配对页右下角 | 100px | 100px | 15 | 否 | "烧杯" |
| 地图页右下角吉祥物占位符 | `mascot-map-corner.png` | `/Materials/Map/` | 地图页右下角 | 100px | 100px | 25 | 否 | "吉祥物" |

### 6. 双导航状态联动机制（硬性设计还原要求）

- **横向与纵向导航联动**：顶部 `AppHeader` 的横向胶囊 Tab 与左侧 `SidebarNav` 的纵向菜单项，必须共享同一个来自 `react-router-dom` 的路由状态。
- **状态源**：统一使用 `useLocation().pathname` 判断当前路由。
- **联动表现**：
  - 无论用户点击哪一套导航，两边的激活高亮态必须保持绝对同步变色。
  - 顶部激活态：浅蓝胶囊背景 `rgba(14,165,233,0.12)` + 文字 `--color-primary`。
  - 侧边栏激活态：左侧边框发光 `3px solid --color-primary` + 浅蓝背景 + 文字 `--color-primary`。
- **路由映射**：`/` → "总览"；`/map` → "地图监视"；`/data` → "数据分析"；`/device` → "设备配对"。

## 六、页面元素级规格总表

### 表 6.1：几何布局与数据源表

#### 总览页（OverviewPage）

| 页面 | 层级 | 推荐组件名 | 变量名/id | 所属父元素 | 页面位置 | 相邻关系 | 推荐宽度 | 推荐高度 | Padding | Margin | 数据来源 |
|------|------|------------|-----------|------------|----------|----------|----------|----------|---------|--------|----------|
| 总览页 | L0 | OverviewPage | overviewPage | MainContent | 顶部第一页 | 占据全部可用宽度 | 100% | auto | 24-32px | 0 | — |
| 指标卡行 | L1 | MetricSummaryCard | metricCardsRow | OverviewPage | 顶部第一行 | 5张卡片等间距 gap 16px | 100% | 120-140px | 0 | 0 0 24px 0 | demoSummary |
| 在线设备卡 | L2 | MetricSummaryCard | onlineCard | metricCardsRow | 第1个 | 右侧紧邻空闲设备卡 16px | calc(20%-13px) | 120-140px | 20px | 0 | demoSummary.onlineDevices/totalDevices |
| 空闲设备卡 | L2 | MetricSummaryCard | idleCard | metricCardsRow | 第2个 | 位于在线设备卡右侧 16px | calc(20%-13px) | 120-140px | 20px | 0 | demoReadings filter status=idle |
| 离线设备卡 | L2 | MetricSummaryCard | offlineCard | metricCardsRow | 第3个 | 位于空闲设备卡右侧 16px | calc(20%-13px) | 120-140px | 20px | 0 | demoReadings filter status=offline |
| 平均藻毒素卡 | L2 | MetricSummaryCard | avgToxinCard | metricCardsRow | 第4个 | 位于离线设备卡右侧 16px | calc(20%-13px) | 120-140px | 20px | 0 | demoSummary.averageToxinUgL |
| 最高风险卡 | L2 | MetricSummaryCard | maxRiskCard | metricCardsRow | 第5个 | 最右侧 | calc(20%-13px) | 120-140px | 20px | 0 | demoSummary.maxToxinReading |
| 中部内容区 | L1 | div/section | middleSection | OverviewPage | 指标卡行下方 | 三列布局 gap 24px | 100% | 360-400px | 0 | 24px 0 | — |
| 系统状态面板 | L2 | SystemStatusPanel | systemStatusPanel | middleSection | 中部左侧 | 宽占比约28% | 28%(min 300px) | 100% | 20-24px | 0 | demoSummary聚合计算 |
| 告警摘要面板 | L2 | AlertSummaryPanel | alertSummaryPanel | middleSection | 中部中间 | 位于系统状态面板右侧 24px | 32%(min 340px) | 100% | 20-24px | 0 | demoReadings遍历统计 |
| 趋势概览面板 | L2 | OverviewTrendChart | trendPanel | middleSection | 中部右侧 | 位于告警摘要面板右侧 24px | 36%(min 380px) | 100% | 20-24px | 0 | demoDeviceHistory聚合平均 |
| 最新采样表格 | L1 | LatestReadingsTable | readingsTable | OverviewPage | 中部下方 | 占据整行 | 100% | auto | 20-24px | 24px 0 0 0 | demoReadings前5条 |
| 查看全部按钮 | L2 | AppButton | viewAllBtn | readingsTable标题行右侧 | 表格右上角 | 与标题同行靠右 | auto | 32-36px | 6px 16px | 0 | — |

#### 地图监视页（MapMonitorPage）

| 页面 | 层级 | 推荐组件名 | 变量名/id | 所属父元素 | 页面位置 | 相邻关系 | 推荐宽度 | 推荐高度 | Padding | Margin | 数据来源 |
|------|------|------------|-----------|------------|----------|----------|----------|----------|---------|--------|----------|
| 地图监视页 | L0 | MapMonitorPage | mapPage | MainContent | 顶部第一页 | 左右两栏 | 100% | auto | 24-32px | 0 | — |
| 主地图面板 | L1 | LakeRiskMap | lakeRiskMap | MapMonitorPage | 左侧主区域 | 右侧与SelectedDevicePanel间距24px | calc(100%-360px-24px) | 640-680px | 0 | 0 | demoReadings+demoLake |
| 地图控件容器 | L2 | div | mapControls | LakeRiskMap | 地图左上角/上方 | 悬浮于地图之上 z-index 450+ | auto | auto | 8px | 16px | — |
| 缩放按钮 | L3 | Leaflet默认 | zoomControl | LakeRiskMap | 地图左侧 | Leaflet内置 | auto | auto | 0 | 0 | — |
| 图层切换按钮组 | L3 | MapLayerToggle | layerToggles | mapControls | 地图上方偏左 | 两个胶囊按钮 | auto | 36px | 0 | 0 8px 0 0 | 本地state |
| 设备点位 | L3 | CircleMarker | deviceMarkers | LakeRiskMap | 地图坐标位置 | 14个点位 | 半径11-15px | 半径11-15px | 0 | 0 | demoReadings |
| 风险图例 | L2 | RiskLegend | riskLegend | LakeRiskMap | 地图底部浮层 | 悬浮底部中央 距下边缘16px | 480-520px | 48-56px | 12px 20px | 0 | — |
| 右侧设备详情面板 | L1 | SelectedDevicePanel | selectedDevicePanel | MapMonitorPage | 右侧固定宽栏 | 左侧紧邻LakeRiskMap | 360px | 640-680px | 20-24px | 0 | 选中设备demoReadings+getDeviceHistory |
| 详情标题区 | L2 | div | deviceDetailHeader | SelectedDevicePanel | 面板顶部 | 设备名+风险状态Badge | 100% | auto | 0 0 16px 0 | 0 | selectedReading.name |
| 藻毒素浓度卡 | L2 | AquaCard | toxinDetailCard | SelectedDevicePanel | 标题下方第一行 | 占据整行 | 100% | 80-90px | 16px | 0 0 12px 0 | selectedReading.toxinUgL |
| 电量/信号/水温/pH网格 | L2 | div | metricGrid | SelectedDevicePanel | 浓度卡下方 | 2x2网格 gap 12px | 100% | auto | 0 | 0 0 12px 0 | selectedReading各字段 |
| 查看历史数据按钮 | L2 | AppButton | viewHistoryBtn | SelectedDevicePanel | 面板底部 | 位于详情信息下方 | 100% | 44px | 0 | 16px 0 0 0 | — |
| 底部设备/吉祥物占位符 | L2 | ImagePlaceholder | mapBottomMascot | SelectedDevicePanel | 面板最底部 | 位于按钮下方 | 100px | 100px | 0 | 16px 0 0 0 | — |

#### 数据分析页（DataAnalysisPage）

| 页面 | 层级 | 推荐组件名 | 变量名/id | 所属父元素 | 页面位置 | 相邻关系 | 推荐宽度 | 推荐高度 | Padding | Margin | 数据来源 |
|------|------|------------|-----------|------------|----------|----------|----------|----------|---------|--------|----------|
| 数据分析页 | L0 | DataAnalysisPage | dataPage | MainContent | 顶部第一页 | 占据全部可用宽度 | 100% | auto | 24-32px | 0 | — |
| 顶部筛选栏 | L1 | DataFilterBar | filterBar | DataAnalysisPage | 页面最顶部 | 内部横向排列 gap 16px | 100% | 56-64px | 0 | 0 0 24px 0 | 本地FilterState |
| 时间范围选择器 | L2 | AppSelect | timeRangeSelect | DataFilterBar | 筛选栏左侧 | 与设备筛选器间距16px | 220-260px | 40px | 0 12px | 0 | 本地state |
| 设备筛选器 | L2 | AppSelect | deviceSelect | DataFilterBar | 时间范围右侧 | 与传感器筛选器间距16px | 180-200px | 40px | 0 12px | 0 | demoReadings名称列表 |
| 传感器筛选器 | L2 | AppSelect | sensorSelect | DataFilterBar | 设备筛选器右侧 | 与导出按钮间距16px | 200-240px | 40px | 0 12px | 0 | 本地state |
| 导出数据按钮 | L2 | AppButton | exportBtn | DataFilterBar | 筛选栏最右侧 | 靠右对齐 | auto | 40px | 8px 20px | 0 0 0 auto | — |
| 趋势分析区 | L1 | div | trendSection | DataAnalysisPage | 筛选栏下方 | 左右两栏：趋势图+传感器对比 | 100% | 420-460px | 0 | 0 0 24px 0 | — |
| 趋势分析图 | L2 | MultiMetricTrendChart | trendChart | trendSection | 左侧 | 右侧与SensorComparisonPanel间距24px | calc(100%-320px-24px) | 420-460px | 20px | 0 | demoDeviceHistory多设备聚合 |
| 传感器对比面板 | L2 | SensorComparisonPanel | sensorCompare | trendSection | 趋势图右侧 | 固定宽侧边栏 | 320px | 420-460px | 20px | 0 | demoReadings最新值 |
| AI预测区 | L1 | div | predictionSection | DataAnalysisPage | 趋势分析区下方 | 左右两栏：预测图+置信度卡 | 100% | 380-420px | 0 | 24px 0 0 0 | — |
| AI预测图 | L2 | ToxinPredictionPanel | predictionChart | predictionSection | 左侧 | 右侧与置信度信息卡间距24px | calc(100%-280px-24px) | 380-420px | 20px | 0 | mockPredictions.ts |
| 模型置信度卡列 | L2 | div | confidenceCards | predictionSection | 预测图右侧 | 垂直堆叠3张卡片 | 280px | 380-420px | 0 | 0 | 模拟数据 |
| 模型置信度值 | L3 | AquaCard | confidenceValueCard | confidenceCards | 顶部 | 大字号87% | 100% | 100px | 16px | 0 0 12px 0 | 模拟数据 |
| 预测区间卡 | L3 | AquaCard | predictionRangeCard | confidenceCards | 中部 | 0.45-3.20µg/L | 100% | 100px | 16px | 0 0 12px 0 | 模拟数据 |
| 下一高风险时间卡 | L3 | AquaCard | nextRiskCard | confidenceCards | 底部 | 5月29日 | 100% | 100px | 16px | 0 | 模拟数据 |

#### 设备配对页（DevicePairingPage）

| 页面 | 层级 | 推荐组件名 | 变量名/id | 所属父元素 | 页面位置 | 相邻关系 | 推荐宽度 | 推荐高度 | Padding | Margin | 数据来源 |
|------|------|------------|-----------|------------|----------|----------|----------|----------|---------|--------|----------|
| 设备配对页 | L0 | DevicePairingPage | devicePage | MainContent | 顶部第一页 | 左右两栏：设备卡片区+配对面板 | 100% | auto | 24-32px | 0 | — |
| 顶部操作栏 | L1 | DeviceToolbar | toolbar | DevicePairingPage | 页面最顶部 | 与下方卡片网格间距20px | 100% | 48px | 0 | 0 0 20px 0 | — |
| 添加设备按钮 | L2 | AppButton | addDeviceBtn | DeviceToolbar | 左侧第一个 | 与刷新按钮间距12px | auto | 40px | 8px 20px | 0 | — |
| 刷新列表按钮 | L2 | AppButton | refreshBtn | DeviceToolbar | 添加设备按钮右侧 | 与批量操作间距12px | auto | 40px | 8px 16px | 0 | — |
| 批量操作按钮 | L2 | AppButton | batchBtn | DeviceToolbar | 最右侧 | 带下拉箭头 | auto | 40px | 8px 16px | 0 0 0 auto | — |
| 设备卡片网格 | L1 | DeviceCardGrid | cardGrid | DevicePairingPage | 操作栏下方 | 3列网格 与右侧PairingPanel间距24px | calc(100%-340px-24px) | auto | 0 | 0 | mockDevices.ts/本地state |
| 单张设备卡片 | L2 | DeviceCard | deviceCard | DeviceCardGrid | 网格单元格 | 列间距20px 行间距20px | calc((100%-40px)/3) | 280-300px | 16-20px | 0 | 单个device对象 |
| 拖拽排序提示区 | L1 | DeviceSortDropZone | sortDropZone | DevicePairingPage | 卡片网格下方 | 与卡片网格间距20px | calc(100%-340px-24px) | 64-80px | 16px | 20px 0 0 0 | — |
| 右侧配对面板 | L1 | PairingPanel | pairingPanel | DevicePairingPage | 页面右侧固定栏 | 左侧紧邻卡片网格 | 340px | auto | 20-24px | 0 | — |
| 雷达扫描区域 | L2 | RadarScanner | radarScanner | PairingPanel | 面板顶部 | 居中 | 280px | 280px | 0 | 0 0 20px 0 | — |
| 发现设备列表 | L2 | div | discoveredList | PairingPanel | 雷达下方 | 垂直列表 | 100% | auto | 0 | 16px 0 0 0 | 模拟DiscoveredDevice[] |
| 单个发现设备项 | L3 | DiscoveredDeviceItem | discoveredItem | discoveredList | 列表行 | 行高64-72px | 100% | 64-72px | 12px 0 | 0 0 8px 0 | DiscoveredDevice |

### 表 6.2：交互与视觉素材表

#### 总览页

| 推荐组件名 | 功能说明 | 交互说明 | 状态说明 | 是否需要图片/图标 | 视觉素材占位符名称 | 占位符初始呈现尺寸 | 未来素材存放路径 | 缺失素材Fallback文本 |
|------------|----------|----------|----------|-------------------|---------------------|---------------------|-------------------|------------------------|
| MetricSummaryCard(在线设备) | 展示在线设备数量 | 点击可跳转设备页（前端模拟） | 数字为--color-text 描述为--color-muted | 是 | overview-online-icon-placeholder | 48px×48px | /Materials/Overview/ | "在线" |
| MetricSummaryCard(空闲设备) | 展示空闲设备数量 | hover轻微上浮shadow-hover | 数字橙色--color-attention | 是 | overview-idle-icon-placeholder | 48px×48px | /Materials/Overview/ | "空闲" |
| MetricSummaryCard(离线设备) | 展示离线设备数量 | hover轻微上浮 | 数字灰色--color-muted | 是 | overview-offline-icon-placeholder | 48px×48px | /Materials/Overview/ | "离线" |
| MetricSummaryCard(平均藻毒素) | 展示平均值 | hover轻微上浮 | 数字蓝色--color-primary | 是 | overview-average-toxin-icon-placeholder | 48px×48px | /Materials/Overview/ | "平均" |
| MetricSummaryCard(最高风险) | 展示最高风险值 | 点击可跳转地图页并选中该设备 | 数字红色--color-danger 设备名--color-muted | 是 | overview-risk-icon-placeholder | 48px×48px | /Materials/Overview/ | "风险" |
| SystemStatusPanel | 系统整体运行状态 | 点击无交互（纯展示） | 正常：绿色盾牌图标+"运行正常"；异常：橙色图标+"需关注" | 是 | overview-system-shield-icon-placeholder | 64px×64px | /Materials/Overview/ | "状态" |
| AlertSummaryPanel | 告警分类统计 | 点击某类告警可跳转数据分析页并带上筛选条件 | 高风险：红色；警戒：橙色；关注：黄色；离线：蓝色 | 是 | overview-alert-icon-placeholder | 24px×24px（每行左侧） | /Materials/Overview/ | "!" |
| OverviewTrendChart | 近7天平均藻毒素趋势 | hover数据点显示tooltip | 折线颜色--color-primary 面积填充rgba(14,165,233,0.1) | 否 | — | — | — | — |
| LatestReadingsTable | 最新5条采样记录 | 行hover背景变浅蓝；点击查看全部跳转数据分析页 | 状态列彩色圆点（normal绿/attention黄/warning橙/danger红） | 否 | — | — | — | — |

#### 地图监视页

| 推荐组件名 | 功能说明 | 交互说明 | 状态说明 | 是否需要图片/图标 | 视觉素材占位符名称 | 占位符初始呈现尺寸 | 未来素材存放路径 | 缺失素材Fallback文本 |
|------------|----------|----------|----------|-------------------|---------------------|---------------------|-------------------|------------------------|
| LakeRiskMap | 地图主容器 | 滚轮缩放、拖拽平移；点击设备点位选中 | 地图底图OpenStreetMap | 否 | — | — | — | — |
| MapMarkerPlaceholder(normal) | 正常风险设备标记 | click选中设备 popup显示详情 | 绿色#22c55e | 是 | map-marker-normal-placeholder | 36px×48px | /Materials/Map/ | "●" |
| MapMarkerPlaceholder(attention) | 关注风险设备标记 | click选中 | 黄色#f59e0b | 是 | map-marker-attention-placeholder | 36px×48px | /Materials/Map/ | "●" |
| MapMarkerPlaceholder(warning) | 警戒风险设备标记 | click选中 | 橙色#f97316 | 是 | map-marker-warning-placeholder | 36px×48px | /Materials/Map/ | "●" |
| MapMarkerPlaceholder(danger) | 高风险设备标记 | click选中 popup自动展开 | 红色#ef4444 | 是 | map-marker-danger-placeholder | 36px×48px | /Materials/Map/ | "●" |
| SelectedDevicePanel | 选中设备详情 | 点击"查看历史数据"跳转数据分析页 | 风险色随设备toxinUgL变化 | 是（设备插画） | map-selected-device-illustration-placeholder | 80px×80px | /Materials/Map/ | "设备" |
| RiskLegend | 图例说明 | 无交互 | 四级色点 | 否 | — | — | — | — |
| MapLayerToggle | 图层开关 | click切换热力图/设备图层显示 | 激活态浅蓝背景 | 否 | map-layer-icon-placeholder | 20px×20px | /Materials/Map/ | "图层" |

#### 数据分析页

| 推荐组件名 | 功能说明 | 交互说明 | 状态说明 | 是否需要图片/图标 | 视觉素材占位符名称 | 占位符初始呈现尺寸 | 未来素材存放路径 | 缺失素材Fallback文本 |
|------------|----------|----------|----------|-------------------|---------------------|---------------------|-------------------|------------------------|
| DataFilterBar | 数据筛选 | 改变筛选项后图表数据前端过滤重算 | — | 是（日历/筛选/导出图标） | data-export-icon-placeholder | 20px×20px | /Materials/Data/ | "导出" |
| MultiMetricTrendChart | 三轴趋势图 | hover显示tooltip；图例可点击隐藏折线 | 藻毒素折线蓝/水温绿/pH紫；超阈值红点三角标记 | 是（告警三角） | data-trend-warning-icon-placeholder | 16px×16px（数据点） | /Materials/Data/ | "▲" |
| SensorComparisonPanel | 传感器对比排行 | 点击设备名可跳转地图页定位 | 数值颜色跟随风险等级 | 否 | — | — | — | — |
| ToxinPredictionPanel | AI预测图表 | hover tooltip；时间范围下拉切换 | 历史实线蓝/预测虚线紫/置信区间半透明紫 | 否 | data-prediction-icon-placeholder | 20px×20px | /Materials/Data/ | "AI" |
| 模型置信度卡 | 展示模型置信度 | 无交互 | 大字号蓝色--color-primary | 是（置信度图标） | data-confidence-icon-placeholder | 24px×24px | /Materials/Data/ | "置信" |
| 显微镜装饰 | 左下角实验器材 | 无交互，纯装饰 | — | 是 | data-sidebar-microscope-placeholder | 120px×120px | /Materials/Data/ | "显微镜" |

#### 设备配对页

| 推荐组件名 | 功能说明 | 交互说明 | 状态说明 | 是否需要图片/图标 | 视觉素材占位符名称 | 占位符初始呈现尺寸 | 未来素材存放路径 | 缺失素材Fallback文本 |
|------------|----------|----------|----------|-------------------|---------------------|---------------------|-------------------|------------------------|
| DeviceCard | 单台设备信息卡 | 点击选中（勾选）；拖拽手柄可排序；离线设备显示连接按钮 | 在线：绿点；待机：黄点；离线：灰点；选中：蓝边框+阴影 | 是（设备插画按type动态渲染） | device-card-buoy-placeholder / device-card-probe-placeholder / device-card-offline-placeholder | 92px×92px | /Materials/Drive/ | "浮标"/"探针" |
| DeviceToolbar | 顶部操作 | 点击触发对应模态框/下拉菜单 | hover背景变浅 | 是（加号/刷新/批量图标） | device-add-icon-placeholder / device-refresh-icon-placeholder | 20px×20px | /Materials/Drive/ | "+"/"↻" |
| DeviceSortDropZone | 拖拽排序提示 | 拖拽时虚线高亮 | 默认虚线边框淡蓝 | 是（拖拽手柄图标） | device-drag-icon-placeholder | 24px×24px | /Materials/Drive/ | "⇅" |
| RadarScanner | 雷达扫描动画 | 点击"扫描"启动动画（前端模拟） | 3层虚线圆环淡蓝旋转 | 是（蓝牙图标） | device-scan-bluetooth-placeholder | 72px×72px | /Materials/Drive/ | "蓝牙" |
| PairingPanel | 添加新设备面板 | 点击蓝牙配对/WiFi连接按钮模拟配对流程 | 发现设备列表动态渲染 | 是（WiFi/蓝牙图标） | device-wifi-icon-placeholder / device-battery-icon-placeholder / device-signal-icon-placeholder | 20px×20px | /Materials/Drive/ | "WiFi"/"电量"/"信号" |
| 底部吉祥物/实验器材 | 右下角装饰 | 无交互 | — | 是 | device-bottom-mascot-placeholder / device-lab-flask-placeholder | 100px×100px / 80px×80px | /Materials/Drive/ | "吉祥物"/"烧杯" |

## 七、图片与图标占位符总表

| 页面 | 占位符名称 | 推荐素材文件名 | 未来素材路径 | 类型 | 用途 | 页面位置 | 所属组件 | 推荐宽度 | 推荐高度 | 是否保持比例 | 是否需要透明背景 | 当前占位符样式 | 缺失素材fallback文案 | 备注 |
|------|-----------|---------------|-------------|------|------|----------|----------|----------|----------|-------------|---------------|---------------|----------------------|------|
| 通用 | logo-ocean-placeholder | logo-ocean.png | /Materials/General/ | logo | 平台Logo | AppHeader左侧 | AppHeader | 48px | 48px | 是 | 是 | 浅蓝虚线框圆角内写"LOGO" | "LOGO" | — |
| 通用 | header-user-avatar-placeholder | avatar-default.png | /Materials/General/ | icon | 用户头像 | AppHeader右侧用户胶囊内 | AppHeader | 28px | 28px | 是 | 是 | 灰色圆形虚线框内写"头像" | "头像" | — |
| 通用 | notification-icon-placeholder | icon-notification.png | /Materials/General/ | icon | 通知铃铛 | AppHeader右侧 | AppHeader | 20px | 20px | 是 | 是 | lucide-react Bell fallback | "铃铛" | 优先使用lucide-react Bell |
| 通用 | nav-overview-icon-placeholder | nav-overview.png | /Materials/General/ | icon | 总览导航图标 | SidebarNav/AppHeader | SidebarNav/AppHeader | 20px | 20px | 是 | 是 | lucide-react Home fallback | "总览" | 优先使用lucide-react Home |
| 通用 | nav-map-icon-placeholder | nav-map.png | /Materials/General/ | icon | 地图导航图标 | SidebarNav/AppHeader | SidebarNav/AppHeader | 20px | 20px | 是 | 是 | lucide-react MapPin fallback | "地图" | 优先使用lucide-react MapPin |
| 通用 | nav-data-icon-placeholder | nav-data.png | /Materials/General/ | icon | 数据导航图标 | SidebarNav/AppHeader | SidebarNav/AppHeader | 20px | 20px | 是 | 是 | lucide-react BarChart3 fallback | "数据" | 优先使用lucide-react BarChart3 |
| 通用 | nav-device-icon-placeholder | nav-device.png | /Materials/General/ | icon | 设备导航图标 | SidebarNav/AppHeader | SidebarNav/AppHeader | 20px | 20px | 是 | 是 | lucide-react Cpu fallback | "设备" | 优先使用lucide-react Cpu |
| 通用 | bubble-decoration-placeholder | bubble.png | /Materials/General/ | decoration | 气泡装饰 | Sidebar中下部/页面角落 | SidebarNav/PageFrame | 16px | 16px | 是 | 是 | 浅蓝半透明圆opacity 0.3 | "●" | 多个实例散布排列 |
| 通用 | wave-decoration-placeholder | wave.png | /Materials/General/ | decoration | 水波装饰 | Sidebar底部/页面底部 | SidebarNav/PageFrame | 180px | 40px | 否 | 是 | 浅蓝波浪线SVG fallback | "〰" | 可复用SVG组件替代 |
| 通用 | header-mascot-small-placeholder | mascot-header-small.png | /Materials/General/ | mascot | Header小吉祥物 | AppHeader右上角溢出边界 | AppHeader | 84px | 84px | 是 | 是 | 浅蓝虚线框圆角内写"吉祥物" | "吉祥物" | 父容器必须overflow-visible |
| 通用 | sidebar-mascot-large-placeholder | mascot-sidebar-large.png | /Materials/General/ | mascot | Sidebar大吉祥物 | SidebarNav底部 | SidebarNav | 160px | 220px | 是 | 是 | 浅蓝虚线框圆角内写"吉祥物" | "吉祥物" | 父容器必须overflow-visible |
| 总览页 | overview-system-shield-icon-placeholder | icon-shield.png | /Materials/Overview/ | icon | 系统状态盾牌 | SystemStatusPanel左侧 | SystemStatusPanel | 64px | 64px | 是 | 是 | lucide-react ShieldCheck fallback | "状态" | 优先使用lucide-react |
| 总览页 | overview-online-icon-placeholder | icon-online.png | /Materials/Overview/ | icon | 在线设备图标 | 在线设备MetricSummaryCard内 | MetricSummaryCard | 48px | 48px | 是 | 是 | lucide-react Wifi fallback | "在线" | — |
| 总览页 | overview-idle-icon-placeholder | icon-idle.png | /Materials/Overview/ | icon | 空闲设备图标 | 空闲设备MetricSummaryCard内 | MetricSummaryCard | 48px | 48px | 是 | 是 | lucide-react Clock fallback | "空闲" | — |
| 总览页 | overview-offline-icon-placeholder | icon-offline.png | /Materials/Overview/ | icon | 离线设备图标 | 离线设备MetricSummaryCard内 | MetricSummaryCard | 48px | 48px | 是 | 是 | lucide-react Unplug fallback | "离线" | — |
| 总览页 | overview-average-toxin-icon-placeholder | icon-toxin.png | /Materials/Overview/ | icon | 平均毒素图标 | 平均藻毒素MetricSummaryCard内 | MetricSummaryCard | 48px | 48px | 是 | 是 | lucide-react Droplets fallback | "平均" | — |
| 总览页 | overview-risk-icon-placeholder | icon-risk.png | /Materials/Overview/ | icon | 最高风险图标 | 最高风险MetricSummaryCard内 | MetricSummaryCard | 48px | 48px | 是 | 是 | lucide-react TriangleAlert fallback | "风险" | — |
| 总览页 | overview-alert-icon-placeholder | icon-alert.png | /Materials/Overview/ | icon | 告警摘要图标 | AlertSummaryPanel每行左侧 | AlertSummaryPanel | 24px | 24px | 是 | 是 | lucide-react AlertTriangle fallback | "!" | 多色版本按级别变化 |
| 地图监视页 | map-header-mascot-placeholder | mascot-map-header.png | /Materials/Map/ | mascot | 地图页Header吉祥物 | AppHeader右上角（复用通用） | AppHeader | 84px | 84px | 是 | 是 | 复用header-mascot-small-placeholder | "吉祥物" | 可复用通用占位符 |
| 地图监视页 | map-marker-normal-placeholder | marker-normal.png | /Materials/Map/ | map-marker | 正常风险标记 | 地图上设备坐标点 | LakeRiskMap | 36px | 48px | 是 | 是 | 绿色圆形+定位针形状fallback | "●" | 可用CSS绘制fallback |
| 地图监视页 | map-marker-attention-placeholder | marker-attention.png | /Materials/Map/ | map-marker | 关注风险标记 | 地图上设备坐标点 | LakeRiskMap | 36px | 48px | 是 | 是 | 黄色圆形+定位针形状fallback | "●" | — |
| 地图监视页 | map-marker-warning-placeholder | marker-warning.png | /Materials/Map/ | map-marker | 警戒风险标记 | 地图上设备坐标点 | LakeRiskMap | 36px | 48px | 是 | 是 | 橙色圆形+定位针形状fallback | "●" | — |
| 地图监视页 | map-marker-danger-placeholder | marker-danger.png | /Materials/Map/ | map-marker | 高风险标记 | 地图上设备坐标点 | LakeRiskMap | 36px | 48px | 是 | 是 | 红色圆形+定位针形状fallback | "●" | — |
| 地图监视页 | map-selected-device-illustration-placeholder | device-illustration.png | /Materials/Map/ | device-illustration | 选中设备插画 | SelectedDevicePanel标题区旁 | SelectedDevicePanel | 80px | 80px | 是 | 是 | 浅蓝虚线框内写"设备图" | "设备" | 按设备类型动态切换更好 |
| 地图监视页 | map-bottom-mascot-placeholder | mascot-map-bottom.png | /Materials/Map/ | mascot | 地图页右下角装饰 | 地图页右下角或SelectedDevicePanel底部 | MapMonitorPage | 100px | 100px | 是 | 是 | 浅蓝虚线框内写"吉祥物" | "吉祥物" | — |
| 地图监视页 | map-layer-icon-placeholder | icon-layer.png | /Materials/Map/ | icon | 图层切换图标 | MapLayerToggle按钮内 | MapLayerToggle | 20px | 20px | 是 | 是 | lucide-react Layers fallback | "图层" | — |
| 地图监视页 | map-location-icon-placeholder | icon-location.png | /Materials/Map/ | icon | 位置图标 | SelectedDevicePanel位置行 | SelectedDevicePanel | 20px | 20px | 是 | 是 | lucide-react MapPin fallback | "位置" | — |
| 数据分析页 | data-sidebar-microscope-placeholder | microscope-decoration.png | /Materials/Data/ | decoration | 显微镜装饰 | 数据分析页左下角或Sidebar底部 | DataAnalysisPage/SidebarNav | 120px | 120px | 是 | 是 | 浅蓝虚线框内写"显微镜" | "显微镜" | 父容器overflow-visible |
| 数据分析页 | data-trend-warning-icon-placeholder | icon-warning-triangle.png | /Materials/Data/ | chart-icon | 趋势图告警三角 | MultiMetricTrendChart超阈值数据点上 | MultiMetricTrendChart | 16px | 16px | 是 | 是 | CSS红色三角绘制fallback | "▲" | 优先用CSS绘制 |
| 数据分析页 | data-export-icon-placeholder | icon-export.png | /Materials/Data/ | icon | 导出图标 | DataFilterBar导出按钮内 | DataFilterBar | 20px | 20px | 是 | 是 | lucide-react Download fallback | "导出" | — |
| 数据分析页 | data-confidence-icon-placeholder | icon-confidence.png | /Materials/Data/ | icon | 置信度图标 | 模型置信度卡标题左侧 | ToxinPredictionPanel | 24px | 24px | 是 | 是 | lucide-react Brain fallback | "置信" | — |
| 数据分析页 | data-prediction-icon-placeholder | icon-prediction.png | /Materials/Data/ | icon | 预测图标 | AI预测面板标题左侧 | ToxinPredictionPanel | 20px | 20px | 是 | 是 | lucide-react TrendingUp fallback | "AI" | — |
| 数据分析页 | data-wave-decoration-placeholder | wave-data.png | /Materials/Data/ | decoration | 数据分析页水波 | 页面底部背景 | DataAnalysisPage | 200px | 40px | 否 | 是 | 复用通用wave-decoration | "〰" | — |
| 设备配对页 | device-card-buoy-placeholder | device-buoy.png | /Materials/Drive/ | device-illustration | 浮标设备插画 | DeviceCard左上角 | DeviceCard | 92px | 92px | 是 | 是 | 浅蓝虚线框内写"浮标" | "浮标" | type===buoy时渲染 |
| 设备配对页 | device-card-probe-placeholder | device-probe.png | /Materials/Drive/ | device-illustration | 探针设备插画 | DeviceCard左上角 | DeviceCard | 92px | 92px | 是 | 是 | 浅蓝虚线框内写"探针" | "探针" | type===probe时渲染 |
| 设备配对页 | device-card-offline-placeholder | device-offline.png | /Materials/Drive/ | device-illustration | 离线设备插画 | DeviceCard左上角（离线状态） | DeviceCard | 92px | 92px | 是 | 是 | 灰色虚线框内写"离线" | "离线" | status===offline时渲染 |
| 设备配对页 | device-scan-bluetooth-placeholder | icon-bluetooth-large.png | /Materials/Drive/ | icon | 雷达中心蓝牙图标 | RadarScanner几何圆心正中 | RadarScanner | 72px | 72px | 是 | 是 | lucide-react Bluetooth fallback放大版 | "蓝牙" | — |
| 设备配对页 | device-bottom-mascot-placeholder | mascot-device-bottom.png | /Materials/Drive/ | mascot | 设备页右下角吉祥物 | 设备页右下角 | DevicePairingPage | 100px | 100px | 是 | 是 | 浅蓝虚线框内写"吉祥物" | "吉祥物" | — |
| 设备配对页 | device-lab-flask-placeholder | lab-flask.png | /Materials/Drive/ | decoration | 实验烧杯装饰 | 设备页右下角（可与吉祥物并存） | DevicePairingPage | 80px | 80px | 是 | 是 | 浅蓝虚线框内写"烧杯" | "烧杯" | — |
| 设备配对页 | device-add-icon-placeholder | icon-add.png | /Materials/Drive/ | icon | 添加设备图标 | DeviceToolbar添加按钮内 | DeviceToolbar | 20px | 20px | 是 | 是 | lucide-react Plus fallback | "+" | — |
| 设备配对页 | device-refresh-icon-placeholder | icon-refresh.png | /Materials/Drive/ | icon | 刷新图标 | DeviceToolbar刷新按钮内 | DeviceToolbar | 20px | 20px | 是 | 是 | lucide-react RefreshCw fallback | "↻" | — |
| 设备配对页 | device-drag-icon-placeholder | icon-drag.png | /Materials/Drive/ | icon | 拖拽手柄图标 | DeviceSortDropZone中央 | DeviceSortDropZone | 24px | 24px | 是 | 是 | lucide-react GripVertical fallback | "⇅" | — |
| 设备配对页 | device-wifi-icon-placeholder | icon-wifi.png | /Materials/Drive/ | icon | WiFi连接图标 | DeviceCard/PairingPanel | DeviceCard/PairingPanel | 20px | 20px | 是 | 是 | lucide-react Wifi fallback | "WiFi" | — |
| 设备配对页 | device-battery-icon-placeholder | icon-battery.png | /Materials/Drive/ | icon | 电量图标 | DeviceCard电量行 | DeviceCard | 20px | 20px | 是 | 是 | lucide-react Battery fallback | "电量" | — |
| 设备配对页 | device-signal-icon-placeholder | icon-signal.png | /Materials/Drive/ | icon | 信号图标 | DeviceCard信号行 | DeviceCard | 20px | 20px | 是 | 是 | lucide-react Signal fallback | "信号" | — |

## 八、页面 1：总览页详细规格

### 路由

`/`

### 页面组件名

`OverviewPage`

### 素材目录

`/iGEM-dry/web/Materials/Overview`

### 1. Header 区域

沿用全局 AppHeader 规范。当前页激活导航项为"总览"。

- **Logo**：左侧，48px × 48px，占位符 `logo-ocean-placeholder`。
- **标题**："水体藻毒素监测平台"，位于 Logo 右侧 12px。
- **顶部导航**：中部胶囊，"总览"激活态（浅蓝背景 + 主色文字）。
- **通知按钮**：右侧铃铛图标，40px × 40px 点击区域。
- **用户胶囊**："iGEM Team" + 头像占位符 28px × 28px。
- **右上角吉祥物占位符**：84px × 84px，`header-mascot-small-placeholder`，向下溢出 Header 下边界约 20px，z-index 30。

### 2. Sidebar 区域

沿用全局 SidebarNav 规范。当前页激活项为"总览"（左侧边框发光 + 浅蓝背景）。

- **四个导航项**：总览、地图监视、数据分析、设备配对。
- **气泡装饰**：Sidebar 中下部散布 3-5 个气泡占位符，16px 圆形，opacity 0.3。
- **大吉祥物占位符**：Sidebar 底部居中，`sidebar-mascot-large-placeholder`，160px × 220px，z-index 20，父容器 `overflow-visible`。
- **水波装饰**：吉祥物下方，`wave-decoration-placeholder`，180px × 40px。

### 3. 顶部指标卡行

横向 5 张卡片等分排列，gap 16px，整体宽度 100%。

**在线设备卡**
- 卡片名：在线设备
- 组件名：`MetricSummaryCard`
- 宽度：`calc(20% - 13px)`，高度 120px-140px
- 内边距：20px
- 标题位置：左上角，12px-13px 辅助说明字
- 数字位置：标题下方，32px-40px 超大字，`{online} / {total} 台`
- 说明文字：数字下方，"数据正常传输中"
- 图标占位符位置：卡片右侧居中，`overview-online-icon-placeholder`，48px × 48px
- 风险颜色：数字 `--color-text`，说明 `--color-muted`
- 数据字段：`demoSummary.onlineDevices` / `demoSummary.totalDevices`
- 交互：hover 轻微上浮 `shadow-hover`

**空闲设备卡**
- 数字：`{idle} / {total} 台`
- 说明："设备待机中"
- 图标：`overview-idle-icon-placeholder`
- 数字颜色：`--color-attention` (橙色)

**离线设备卡**
- 数字：`{offline} / {total} 台`
- 说明："设备离线"
- 图标：`overview-offline-icon-placeholder`
- 数字颜色：`--color-muted` (灰色)

**平均藻毒素卡**
- 数字：`{averageToxinUgL.toFixed(2)} µg/L`
- 说明："较昨日 -0.18 µg/L"（模拟变化值）
- 图标：`overview-average-toxin-icon-placeholder`
- 数字颜色：`--color-primary` (蓝色)

**最高风险卡**
- 数字：`{maxToxinReading.toxinUgL.toFixed(2)} µg/L`
- 说明：`{maxToxinReading.name}`
- 图标：`overview-risk-icon-placeholder`
- 数字颜色：`--color-danger` (红色)
- 交互：点击跳转 `/map?device={maxToxinReading.id}`（前端模拟）

### 4. 中部内容区

三列布局，gap 24px，高度 360px-400px。

**系统状态面板（左，28%）**
- 组件名：`SystemStatusPanel`
- 标题："系统状态"
- 左侧图标占位符：`overview-system-shield-icon-placeholder`，64px × 64px，绿色盾牌或对勾
- 状态文字："运行正常"（或"需关注"）
- 副标题："所有系统功能正常运行"
- 底部三列小指标：数据采集（正常）、数据传输（正常）、设备在线率（64%）
- 背景：`--color-surface`，圆角 16px，padding 20px-24px

**告警摘要面板（中，32%）**
- 组件名：`AlertSummaryPanel`
- 标题："告警摘要"
- 四行列表：高风险告警（红色三角+文字+数字+右箭头）、警戒告警（橙色）、关注告警（黄色）、设备离线（蓝色信息图标）
- 每行高度：48px-52px
- 点击交互：跳转 `/data` 并带上对应筛选条件（前端模拟）
- 数据来源：`demoReadings` 按风险级别和状态统计

**趋势概览面板（右，36%）**
- 组件名：`OverviewTrendChart`
- 标题："趋势概览（平均藻毒素）"
- 右上角下拉："近 7 天"
- 图表类型：Recharts AreaChart 或 LineChart
- 数据：近 7 天每天所有设备 `toxinUgL` 的平均值
- 折线颜色：`--color-primary`
- 面积填充：`rgba(14,165,233,0.1)`
- 右侧终点标注：当前平均值大字号
- 高度：面板高度减去标题区后全部给图表

### 5. 底部最新采样表格

- 组件名：`LatestReadingsTable`
- 位置：中部内容区下方，margin-top 24px
- 表格标题行：左侧"最新采样（近 5 条）"，右侧"查看全部"按钮
- 表格列名：设备名称、采样时间、藻毒素(µg/L)、电量、信号强度、状态、位置
- 表格行高：48px-52px
- 每列宽度比例：设备名 20%、时间 15%、藻毒素 15%、电量 10%、信号 12%、状态 13%、位置 15%
- 彩色状态圆点：直径 8px-10px，与文字间距 8px
- 数值颜色规则：藻毒素列按风险等级着色（normal绿/attention黄/warning橙/danger红）
- "查看全部"按钮位置：表格标题行右侧，点击跳转 `/data`
- 数据来源：`demoReadings` 前 5 条（或按 updatedAt 排序取最新）

### 6. 总览页所有图片与图标占位符

已在第七章总表列出，此处不再重复。所有占位符必须参与排版，尺寸固定，不可因缺失而塌陷。

## 九、页面 2：地图监视页详细规格

### 路由

`/map`

### 页面组件名

`MapMonitorPage`

### 素材目录

`/iGEM-dry/web/Materials/Map`

### 1. Header 与 Sidebar

- 沿用全局规范。
- 顶部导航与侧边栏当前激活项均为"地图监视"。

### 2. 主地图面板 LakeRiskMap

- **位置**：MainContent 左侧主区域。
- **宽度**：`calc(100% - 360px - 24px)`。
- **高度**：640px-680px（推荐 640px）。
- **圆角**：16px-20px。
- **背景**：`--color-surface`。
- **边框**：`1px solid var(--color-border-subtle)`。
- **阴影**：`shadow-card`。
- **地图底图区域**：内部 padding 4px-8px，地图本身圆角略小于容器。
- **地图控件**：
  - 缩放按钮：Leaflet 默认，置于左下角或左上角（避免与图层切换重叠）。
  - 定位按钮：自定义，置于缩放按钮下方，40px × 40px，圆角 8px，图标 `MapPin`。
- **图层切换按钮**：
  - 位置：地图上方偏左，悬浮于地图之上，z-index 450+。
  - "设备图层"胶囊按钮：宽 auto，高 36px，圆角 18px，激活态浅蓝背景。
  - "热力图层"胶囊按钮：同上，与设备图层按钮间距 8px。
- **热力图层**：
  - 默认开启。
  - 使用 `leaflet.heat`，渐变从绿 → 黄 → 橙 → 红。
  - 数据来自 `demoReadings` 的 `lat`/`lng`/`toxinUgL`。
- **设备点位**：
  - 14 个 CircleMarker，颜色跟随 `getRiskColor(toxinUgL)`。
  - 正常半径 11px，选中半径 15px，离线半径 8px。
  - 选中时边框加粗到 4px。
- **风险图例**：见下方 RiskLegend 规格。

### 3. 地图 marker 占位符

| marker 类型 | 尺寸 | 颜色 | 交互状态 |
|-------------|------|------|----------|
| normal | 半径11px (36px×48px占位符) | `#22c55e` | hover放大1.1倍 |
| attention | 半径11px | `#f59e0b` | hover放大1.1倍 |
| warning | 半径11px | `#f97316` | hover放大1.1倍 |
| danger | 半径11px | `#ef4444` | hover放大1.1倍 pulse动画 |
| selected | 半径15px | 继承原风险色 | 边框4px白色+风险色 z-index提升 |

> 占位符缺失时，用 CSS 绘制的定位针形状 fallback，保持相同尺寸和颜色。

### 4. 右侧设备详情面板 SelectedDevicePanel

- **位置**：地图面板右侧，固定宽栏。
- **宽度**：360px。
- **高度**：与地图面板等高（640px-680px）。
- **背景**：`--color-surface`。
- **圆角**：16px-20px。
- **边框**：`1px solid var(--color-border-subtle)`。
- **padding**：20px-24px。
- **内部滚动**：`overflow-y: auto`。

**未选中设备时显示**：
- 湖泊概况：名称 + 描述
- 最高风险点：设备名 + 浓度大字号红色
- 风险等级图例
- 采样节点列表（14 个设备，点击选中）

**选中设备时显示**：
- 标题区："历史采样"标签 + 设备名 + 返回总览按钮
- 风险状态：红色/橙色/黄色 Badge
- 在线状态：绿色圆点 + "在线"
- 藻毒素浓度卡：大字号 `toxinUgL`，颜色跟随风险等级
- 更新时间：`updatedAt`
- 四宫格指标卡：电量、信号强度、水温、pH
- 查看历史数据按钮：100% 宽，44px 高，蓝色主按钮，点击跳转 `/data`
- 底部设备/吉祥物占位符：`map-bottom-mascot-placeholder`，100px × 100px，位于面板最底部或独立于页面右下角

### 5. 风险图例 RiskLegend

- **位置**：地图底部中央浮层，z-index 440+。
- **宽度**：480px-520px。
- **高度**：48px-56px。
- **背景**：`rgba(255,255,255,0.9)`，backdrop-blur，圆角 12px。
- **每个图例项**：
  - 圆点：直径 12px-14px，与文字间距 8px。
  - 文字："正常 < 0.5 µg/L"、"关注 0.5 - 1.0 µg/L"、"警戒 1.0 - 5.0 µg/L"、"高风险 > 5.0 µg/L"
  - 项之间间距：20px-24px。
- **布局**：横向 flex，居中排列。

### 6. 地图页交互与架构防御（硬性要求说明）

- **点击设备点位**：更新 `selectedDeviceId` state，右侧 SelectedDevicePanel 切换为选中设备详情。
- **热力图层开关**：通过 MapLayerToggle 控制本地 state，决定是否渲染 `<HeatLayer>`。
- **设备图层开关**：控制 CircleMarker 的渲染与否。
- **查看历史数据**：点击按钮跳转 `/data`，可通过 URL query 或全局 state 传递设备 ID（当前仅前端模拟）。
- **地图加载失败 fallback**：地图容器内显示 "地图加载失败，请检查网络连接" + 重试按钮。
- **无设备数据 fallback**：显示 "暂无设备数据"。
- **单页应用(SPA)防御规约**：
  - 使用 `react-leaflet` 渲染插值热力图时，热力图数据必须利用 `useMemo` 缓存。
  - 在生命周期结束或重新挂载时，必须在 React 清理函数中显式执行 `map.removeLayer`，防止后续 Agent 编写组件时由于单页路由频繁切换导致地图重叠、重复渲染或 Canvas 内存泄漏。
  - **Leaflet 样式和默认 Marker 路径崩溃 Bug（硬性代码安全要求）**：必须在新项目的地图模块初始化代码中显式调用 `L.Icon.Default.mergeOptions` 并显式导入本地或静态占位符图标图源，或统一自定义全量 Marker 的 `L.icon` 结构，彻底断绝地图 Marker 加载出 404 碎片报错的问题。

## 十、页面 3：数据分析页详细规格

### 路由

`/data`

### 页面组件名

`DataAnalysisPage`

### 素材目录

`/iGEM-dry/web/Materials/Data`

### 1. 顶部筛选栏 DataFilterBar

- **位置**：页面最顶部。
- **高度**：56px-64px。
- **背景**：透明或与页面背景一致。
- **布局**：横向 flex，gap 16px。

**时间范围选择器**
- 宽度：220px-260px。
- 高度：40px。
- 默认值："2025-05-20 ~ 2025-05-27"（日历图标 + 文字）。
- 交互：点击弹出日期范围选择（当前前端模拟，可用两个 `<input type="date">` 组合）。

**设备筛选器**
- 宽度：180px-200px。
- 高度：40px。
- 默认值："全部设备"。
- 选项：全部设备 + 14 台设备名称。
- 图标：`nav-device-icon-placeholder` 或 lucide-react `Cpu`。

**传感器筛选器**
- 宽度：200px-240px。
- 高度：40px。
- 默认值："藻毒素 + 水温 + pH"。
- 选项：藻毒素、水温、pH 的多选组合。
- 图标：lucide-react `Activity`。

**导出数据按钮**
- 位置：筛选栏最右侧，`margin-left: auto`。
- 宽高：auto × 40px，padding 8px 20px。
- 文字："导出数据"。
- 图标：`data-export-icon-placeholder` 或 lucide-react `Download`。
- 交互：点击弹出 "导出成功" toast（前端模拟）。

### 2. 趋势分析面板 MultiMetricTrendChart

- **位置**：筛选栏下方，左侧主区域。
- **宽度**：`calc(100% - 320px - 24px)`。
- **高度**：420px-460px（图表区固定 `h-[380px]`，加上标题和图例）。
- **背景**：`--color-surface`，圆角 16px，padding 20px。

**标题与图例**
- 标题："趋势分析"，左侧。
- 图例：右侧横向排列，藻毒素(µg/L) 蓝色圆点、水温(°C) 绿色圆点、pH 紫色圆点。

**三 Y 轴独立刻度映射系统（图表还原硬性指标）**
- 必须显式配置 Recharts 的三个具有不同 `yAxisId` 的 `<YAxis />` 组件：
  - 左轴 `yAxisId="toxin"`：对应藻毒素刻度范围 **0 - 5 µg/L**。
  - 右轴内侧 `yAxisId="temp"`：对应水温范围 **18 - 30 °C**。
  - 右轴外侧独立悬空 `yAxisId="ph"`：对应 pH 轴线刻度 **6.0 - 8.5**。
- 每条折线必须严丝合缝地绑定到自己的 `yAxisId`：
  - 藻毒素折线：蓝色，`yAxisId="toxin"`。
  - 水温折线：绿色，`yAxisId="temp"`。
  - pH 折线：紫色，`yAxisId="ph"`。
- 高风险阈值线：红色虚线，y=5.0，标注"高风险阈值 (5.0 µg/L)"。
- 警戒阈值线：橙色虚线，y=1.0，标注"警戒阈值 (1.0 µg/L)"。
- **异常点图标占位符**：在折线峰值超过安全阈值（>1.0）的特殊数据点位上，绑定定制化的红色三角形告警 Marker（▲），尺寸 16px × 16px。

**Recharts 高度塌陷防御规约**
- 图表的父级包裹容器必须显式声明固定的物理高度（或通过 Tailwind 网格/比例锁定 `h-[380px]` 等明确范围）和 `relative` 定位。
- **严禁直接将 `<ResponsiveContainer>` 置于不确定高度的弹性 flex/grid 容器中**，以防图表高度塌陷至 0px 或无限制无限纵向伸展。

**Tooltip**
- 背景：`--color-surface-strong`，边框 `1px solid --color-border`，圆角 10px。
- 文字颜色：`--color-text`。

**空状态**
- 无数据时显示 "暂无趋势数据" + 图表占位符图标。

### 3. 传感器对比面板 SensorComparisonPanel

- **位置**：趋势分析图右侧，固定宽侧边栏。
- **宽度**：320px。
- **高度**：与趋势分析图等高（420px-460px）。
- **背景**：`--color-surface`，圆角 16px，padding 20px。

**标题**："传感器对比"
- 副标题："藻毒素 (µg/L) · 最新值"

**对比列表**
- 每个设备对比项高度：56px-64px。
- 每项内容：彩色圆点（8px）+ 设备名 + 最新 toxinUgL 数值（右对齐，大字号，颜色跟随风险等级）。
- 排序规则：按 `toxinUgL` 降序排列。
- 项之间分隔线：1px solid `--color-border-subtle`。
- 点击交互：点击设备名跳转 `/map?device={id}`（前端模拟）。

### 4. AI 预测模块 ToxinPredictionPanel

- **位置**：页面下半部分，趋势分析区下方。
- **布局**：左右两栏，左侧预测图，右侧置信度卡片列。

**主预测图（左侧）**
- 宽度：`calc(100% - 280px - 24px)`。
- 高度：380px-420px。
- 图表类型：Recharts AreaChart。
- 历史数据线（实线）：蓝色 `#0ea5e9`，过去 7 天。
- 预测数据线（虚线）：紫色 `#6366f1`，未来 7 天，`strokeDasharray="5 5"`。
- 95% 置信区间：半透明 Area 阴影覆盖，`rgba(99,102,241,0.15)`。
- X 轴：日期（月-日）。
- Y 轴：藻毒素浓度 0 - 6 µg/L。
- 右上角下拉："预测未来 7 天"。

**右侧置信度信息卡列（宽度 280px）**
- 垂直堆叠 3 张 AquaCard，gap 12px。

**模型置信度卡**
- 标题："模型置信度"
- 数值：大字号 `87%`，颜色 `--color-primary`。
- 图标：`data-confidence-icon-placeholder`。

**预测区间卡**
- 标题："预测区间 (95%)"
- 数值：`0.45 - 3.20 µg/L`。

**下一高风险时间卡**
- 标题："下一高风险时间"
- 数值：`5月29日`，大字号。

### 5. 数据分析页装饰占位符

- **左下角显微镜**：`data-sidebar-microscope-placeholder`，120px × 120px，位于页面左下角，可溢出边界，z-index 15。
- **气泡**：复用通用 `bubble-decoration-placeholder`，散布在页面左侧边缘。
- **水波**：`data-wave-decoration-placeholder`，200px × 40px，位于页面底部。
- **图表警告图标**：`data-trend-warning-icon-placeholder`，16px × 16px，用于超阈值数据点。
- **导出图标**：`data-export-icon-placeholder`，20px × 20px，导出按钮内。

## 十一、页面 4：设备配对页详细规格

### 路由

`/device`

### 页面组件名

`DevicePairingPage`

### 素材目录

`/iGEM-dry/web/Materials/Drive`

### 1. 顶部操作栏 DeviceToolbar

- **位置**：页面最顶部。
- **高度**：48px。
- **布局**：横向 flex，gap 12px。

**添加设备按钮**
- 文字："添加设备"（加号图标在前）。
- 宽高：auto × 40px，padding 8px 20px。
- 背景：`--color-primary`，文字白色，圆角 10px。
- 图标：`device-add-icon-placeholder` 或 lucide-react `Plus`。
- 交互：点击弹出 DeviceFormModal（添加模式）。

**刷新列表按钮**
- 文字："刷新列表"（刷新图标在前）。
- 宽高：auto × 40px，padding 8px 16px。
- 背景：`--color-surface-strong`，边框 `1px solid --color-border`，圆角 10px。
- 图标：`device-refresh-icon-placeholder` 或 lucide-react `RefreshCw`。
- 交互：点击触发旋转动画，1.2 秒后列表重置（前端模拟）。

**批量操作按钮**
- 文字："批量操作"（下拉箭头）。
- 宽高：auto × 40px，padding 8px 16px。
- 背景：`--color-surface-strong`，边框 `1px solid --color-border`，圆角 10px。
- 交互：点击下拉菜单（批量删除、批量导出）。

### 2. 设备卡片网格 DeviceCardGrid

- **位置**：操作栏下方。
- **列数**：桌面端 3 列。
- **行间距**：20px。
- **列间距**：20px。
- **单张卡片宽度**：`calc((100% - 40px) / 3)`。
- **单张卡片高度**：280px-300px。
- **选中态边框**：2px solid `--color-primary`，`shadow-hover`。
- **拖拽态样式**：opacity 0.8，z-index 10，轻微旋转（`rotate(2deg)`）。

### 3. 单张设备卡片 DeviceCard

**设备插画动态条件渲染规约（硬性要求）**
- 必须根据 `MonitoringDevice` 数据结构中的 `type` 字段，动态条件渲染不同的图片占位符。
- `type === 'buoy'` → 渲染 `device-card-buoy-placeholder`（水面浮标模型）。
- `type === 'probe'` → 渲染 `device-card-probe-placeholder`（管状探针模型）。
- `type === 'offline' || status === 'offline'` → 渲染 `device-card-offline-placeholder`（灰色离线模型）。
- **严禁全量渲染单一重复素材**，以确保视觉还原度。

> **注意**：旧项目 `demoReadings.ts` 中无 `type` 字段。重构时需新增 `type` 字段或通过 `name` 字段推断（见数据模型章节）。

**卡片内部元素布局**
- 设备插画占位符：左上角，92px × 92px。
- 设备名称：插画右侧，16px 粗体，`--color-text`。
- 状态圆点：名称左侧或下方，8px-10px 圆形。
- 状态文本：圆点右侧，12px-13px。
- WiFi / 蓝牙图标：状态文本右侧，20px × 20px。
- 电量图标 + 百分比：卡片右上区域，20px 图标 + 14px 文字。
- 分割线：1px solid `--color-border-subtle`，margin 12px 0。
- 藻毒素指标：左下，"藻毒素"标签 + 数值（大字号，颜色跟随风险等级）+ "µg/L"。
- 水温指标：中下，"水温"标签 + 数值 + "°C"。
- pH 指标：右下，"pH"标签 + 数值。
- 卡片右上角选中勾：选中时显示，20px × 20px，蓝色对勾，圆形蓝底。

**高风险、待机、离线状态样式**
- 在线：绿色圆点，名称正常色，全部数据正常显示。
- 待机（idle）：黄色圆点，名称正常色。
- 离线：灰色圆点，名称 `--color-muted`，插画用离线占位符，数据部分显示 "--"。
- 高风险（toxin > 5）：藻毒素数值红色，卡片边框可带淡红色 glow。

### 4. 拖拽排序提示区 DeviceSortDropZone

- **位置**：设备卡片网格下方。
- **宽度**：与卡片网格同宽（`calc(100% - 340px - 24px)`）。
- **高度**：64px-80px。
- **边框**：2px dashed `--color-primary`，opacity 0.4，圆角 12px。
- **背景**：`rgba(14,165,233,0.02)`。
- **图标占位符**：`device-drag-icon-placeholder`，24px × 24px，居中。
- **文案**："拖拽设备卡片可调整顺序"，13px，`--color-muted`。
- **与设备卡片网格间距**：20px margin-top。
- **交互**：拖拽过程中虚线边框 opacity 提升至 0.8，背景变浅蓝。

### 5. 右侧添加新设备 / 扫描面板 PairingPanel

- **位置**：页面右侧固定栏。
- **宽度**：340px。
- **高度**：跟随左侧内容高度（`align-self: stretch`）。
- **背景**：`--color-surface`，圆角 16px，padding 20px-24px。

**标题**
- "添加新设备"，18px 粗体，顶部。
- 副标题："扫描附近设备"，13px，`--color-muted`。

**雷达无线扫描组件几何布局（硬性视觉层级要求）**
- **RadarScanner** 必须由纯 Tailwind 样式构建。
- 使用绝对定位（`absolute`）和宽高居中（`inset-0 m-auto`）。
- 3 层 `border-dashed` 且带有淡蓝半透明环境光的圆环进行等间距等比堆叠嵌套：
  - 第 1 层（外）：直径 280px，border 2px dashed `rgba(14,165,233,0.2)`。
  - 第 2 层（中）：直径 200px，border 2px dashed `rgba(14,165,233,0.35)`。
  - 第 3 层（内）：直径 120px，border 2px dashed `rgba(14,165,233,0.5)`。
- 在几何圆心正中央放置独立的蓝牙状态占位符：
  - 尺寸：**72px × 72px**。
  - 内容：`device-scan-bluetooth-placeholder` 或 lucide-react `Bluetooth`。
  - 颜色：`--color-primary`。
- 扫描动画：3 层圆环以不同速度旋转（CSS animation），或一层脉冲扩散效果。

**发现设备列表**
- 雷达下方，margin-top 20px。
- 标题："已发现设备 (2)"，14px 粗体。
- 每个发现设备项高度：64px-72px。
- 每项内容：设备名 + RSSI 信息（如 "RSSI -48 dBm"）+ 蓝牙配对按钮 / WiFi 连接按钮。
- 按钮尺寸：auto × 32px，padding 6px 12px，圆角 8px。
- 数据来源：模拟 `DiscoveredDevice[]`。

**底部吉祥物 / 实验器材占位符**
- 位于 PairingPanel 最底部或页面右下角。
- `device-bottom-mascot-placeholder`：100px × 100px。
- `device-lab-flask-placeholder`：80px × 80px，可与吉祥物并排或叠加。

### 6. 设备页交互

| 交互 | 触发元素 | 触发条件 | 状态变化 | UI 反馈 | 涉及的数据 | 是否只做前端模拟 |
|------|----------|----------|----------|---------|------------|-----------------|
| 添加设备 | 添加设备按钮 | click | 弹出DeviceFormModal | Modal遮罩+表单 | 本地devices state | 是 |
| 编辑设备 | 设备卡片内编辑图标 | click | 弹出DeviceFormModal（编辑模式） | Modal预填充数据 | 选中device | 是 |
| 删除设备 | 批量操作/单卡片删除 | click→二次确认 | 从devices数组移除 | 卡片淡出动画 | 选中device IDs | 是 |
| 详情查看 | 设备卡片点击（非拖拽手柄） | click | 卡片选中态切换 | 蓝色边框+选中勾 | selectedDeviceIds | 是 |
| 刷新列表 | 刷新列表按钮 | click | 触发loading状态1.2s | 按钮旋转动画 | devices state重置 | 是 |
| 批量操作 | 批量操作下拉 | select | 进入批量选择模式 | 卡片显示复选框 | selectedDeviceIds | 是 |
| 拖拽排序 | 拖拽手柄 | drag end（@dnd-kit） | devices数组reorder | 卡片位置动画交换 | devices数组顺序 | 是 |
| 扫描设备 | PairingPanel自动加载/手动刷新 | mount/click | discoveredDevices数组变化 | 雷达动画+列表更新 | mock DiscoveredDevice[] | 是 |
| 蓝牙配对 | 发现设备项的蓝牙配对按钮 | click | 模拟配对流程1.2s | loading spinner→成功提示 | devices state新增 | 是 |
| WiFi连接 | 发现设备项的WiFi连接按钮 | click | 模拟连接流程1.2s | loading spinner→成功提示 | devices state新增 | 是 |
| 断开连接 | 在线/待机设备卡片的断开按钮 | click | 设备状态变offline | 状态圆点变灰 | devices state | 是 |

## 十二、数据模型与字段规范

新项目应当直接继承、完整平移旧项目数据文件中的核心静态数据与判定计算工具函数（如原 `getRiskLevel`、`getRiskColor`、`getSignalLabel` 等），新页面组件需直接调用这些统一工具函数，严禁在组件内部重复进行魔法数字或颜色硬编码。

### 1. DeviceStatus

| 字段名 | 类型 | 含义 | 示例值 | 是否必填 | 对应页面 |
|--------|------|------|--------|----------|----------|
| — | `'online' \| 'idle' \| 'offline'` | 设备运行状态枚举 | `'online'` | 是 | 全部 |

### 2. RiskLevel

| 字段名 | 类型 | 含义 | 示例值 | 是否必填 | 对应页面 |
|--------|------|------|--------|----------|----------|
| — | `'normal' \| 'attention' \| 'warning' \| 'danger'` | 藻毒素风险等级（重构后对齐 prompt 要求） | `'danger'` | 是 | 全部 |

> **注意**：旧项目使用 `'normal' | 'watch' | 'warning' | 'critical'`，新项目按 prompt 要求统一为 `'normal' | 'attention' | 'warning' | 'danger'`。迁移时需将 `watch` 映射为 `attention`，`critical` 映射为 `danger`。

### 3. MonitoringDevice

| 字段名 | 类型 | 含义 | 示例值 | 是否必填 | 对应页面 |
|--------|------|------|--------|----------|----------|
| id | `string` | 设备唯一标识 | `'aq-001'` | 是 | 全部 |
| name | `string` | 设备显示名称 | `'湖心浮标-01'` | 是 | 全部 |
| type | `'buoy' \| 'probe' \| 'sensor' \| 'other'` | 设备类型，决定占位符插画 | `'buoy'` | 是 | 设备页、地图页 |
| locationName | `string` | 采样位置名称 | `'东湖湖心采样点'` | 是 | 全部 |
| latitude | `number` | 纬度 | `30.5558` | 是 | 地图页 |
| longitude | `number` | 经度 | `114.3991` | 是 | 地图页 |
| status | `DeviceStatus` | 设备状态 | `'online'` | 是 | 全部 |
| connectionType | `'bluetooth' \| 'wifi' \| 'none'` | 连接方式 | `'wifi'` | 是 | 设备页、地图页 |
| battery | `number` | 电量百分比 0-100 | `86` | 是 | 全部 |
| signalDbm | `number` | 信号强度 dBm | `-61` | 是 | 全部 |
| lastUpdated | `string` | 最后更新时间 | `'09:42'` / ISO 字符串 | 是 | 全部 |
| note | `string` | 备注 | `'东湖湖心浮标点'` | 否 | 设备页、地图页 |

> **type 字段推断规则**（旧数据缺失时的 fallback）：
> - 名称包含 "浮标" → `'buoy'`
> - 名称包含 "探针" / "巡检器" → `'probe'`
> - 名称包含 "传感器" / "监测" → `'sensor'`
> - 其他 → `'other'`

### 4. DeviceReading

| 字段名 | 类型 | 含义 | 示例值 | 是否必填 | 对应页面 |
|--------|------|------|--------|----------|----------|
| id | `string` | 读数记录 ID | `'reading-001'` | 是 | 全部 |
| deviceId | `string` | 所属设备 ID | `'aq-001'` | 是 | 全部 |
| deviceName | `string` | 设备名称（冗余，便于展示） | `'湖心浮标-01'` | 是 | 全部 |
| sampledAt | `string` | 采样时间戳 | `'2025-05-27T09:42:00Z'` | 是 | 全部 |
| toxin | `number` | 藻毒素浓度 µg/L | `0.42` | 是 | 全部 |
| waterTemp | `number` | 水温 °C | `24.8` | 是 | 全部 |
| ph | `number` | pH 值 | `7.4` | 是 | 全部 |
| battery | `number` | 电量百分比 | `86` | 是 | 全部 |
| signalDbm | `number` | 信号强度 | `-61` | 是 | 全部 |
| status | `DeviceStatus` | 设备状态 | `'online'` | 是 | 全部 |
| locationName | `string` | 位置名称 | `'东湖湖心采样点'` | 是 | 全部 |
| latitude | `number` | 纬度 | `30.5558` | 是 | 地图页 |
| longitude | `number` | 经度 | `114.3991` | 是 | 地图页 |

> 新旧字段映射：`toxinUgL` → `toxin`，`waterTempC` → `waterTemp`，`batteryPercent` → `battery`，`updatedAt` → `sampledAt` / `lastUpdated`，`locationLabel` → `locationName`，`lat` → `latitude`，`lng` → `longitude`。

### 5. AlertSummary

| 字段名 | 类型 | 含义 | 示例值 | 是否必填 | 对应页面 |
|--------|------|------|--------|----------|----------|
| level | `RiskLevel` | 告警级别 | `'danger'` | 是 | 总览页 |
| label | `string` | 告警名称 | `'高风险告警'` | 是 | 总览页 |
| count | `number` | 该级别设备数量 | `1` | 是 | 总览页 |
| deviceIds | `string[]` | 涉及设备 ID 列表 | `['aq-006']` | 否 | 总览页 |

### 6. TrendPoint

| 字段名 | 类型 | 含义 | 示例值 | 是否必填 | 对应页面 |
|--------|------|------|--------|----------|----------|
| date | `string` | 日期标签 | `'05-21'` | 是 | 总览页、数据分析页 |
| toxin | `number` | 平均藻毒素 | `2.50` | 是 | 总览页、数据分析页 |
| waterTemp | `number` | 平均水温 | `25.5` | 否 | 数据分析页 |
| ph | `number` | 平均 pH | `7.5` | 否 | 数据分析页 |

### 7. PredictionPoint

| 字段名 | 类型 | 含义 | 示例值 | 是否必填 | 对应页面 |
|--------|------|------|--------|----------|----------|
| date | `string` | 日期标签 | `'05-27'` | 是 | 数据分析页 |
| value | `number` | 预测浓度 | `3.20` | 是 | 数据分析页 |
| isPrediction | `boolean` | 是否为预测值 | `true` | 是 | 数据分析页 |
| upperBound | `number` | 95% 置信区间上界 | `3.80` | 否 | 数据分析页 |
| lowerBound | `number` | 95% 置信区间下界 | `2.60` | 否 | 数据分析页 |

### 8. DiscoveredDevice

| 字段名 | 类型 | 含义 | 示例值 | 是否必填 | 对应页面 |
|--------|------|------|--------|----------|----------|
| id | `string` | 发现设备临时 ID | `'WaterProbe-7F2A'` | 是 | 设备页 |
| name | `string` | 设备广播名 | `'WaterProbe-7F2A'` | 是 | 设备页 |
| rssi | `number` | 信号强度 RSSI | `-48` | 是 | 设备页 |
| connectionType | `'bluetooth' \| 'wifi'` | 发现时的连接类型 | `'bluetooth'` | 是 | 设备页 |

### 9. FilterState

| 字段名 | 类型 | 含义 | 示例值 | 是否必填 | 对应页面 |
|--------|------|------|--------|----------|----------|
| timeRangeStart | `string` | 时间范围开始 | `'2025-05-20'` | 否 | 数据分析页 |
| timeRangeEnd | `string` | 时间范围结束 | `'2025-05-27'` | 否 | 数据分析页 |
| deviceIds | `string[]` | 筛选设备 ID | `['aq-001']` | 否 | 数据分析页 |
| sensors | `('toxin' \| 'waterTemp' \| 'ph')[]` | 选中传感器 | `['toxin', 'waterTemp']` | 否 | 数据分析页 |

### 10. DeviceAction

| 字段名 | 类型 | 含义 | 示例值 | 是否必填 | 对应页面 |
|--------|------|------|--------|----------|----------|
| type | `'add' \| 'edit' \| 'delete' \| 'connect' \| 'disconnect' \| 'sort'` | 操作类型 | `'add'` | 是 | 设备页 |
| deviceId | `string` | 目标设备 ID | `'aq-001'` | 否 | 设备页 |
| payload | `Partial<MonitoringDevice>` | 操作载荷 | `{ name: '新名称' }` | 否 | 设备页 |

## 十三、风险规则与状态规则

### 1. 藻毒素浓度风险分级

| 级别 | 数值范围 | 颜色 | 标签 |
|------|----------|------|------|
| normal | < 0.5 µg/L | `#22c55e` (green-500) | 正常 |
| attention | 0.5 - 1.0 µg/L | `#f59e0b` (amber-500) | 关注 |
| warning | 1.0 - 5.0 µg/L | `#f97316` (orange-500) | 警戒 |
| danger | > 5.0 µg/L | `#ef4444` (red-500) | 高风险 |

> 统一使用 `src/utils/risk.ts` 中的工具函数，禁止组件内硬编码。

### 2. 状态映射

| 状态值 | 显示颜色 | 显示文字 |
|--------|----------|----------|
| online | `#22c55e` | 在线 |
| idle | `#f59e0b` | 待机 |
| offline | `#94a3b8` | 离线 |

### 3. 数值颜色

| 场景 | 颜色 |
|------|------|
| 高风险藻毒素 | `#ef4444` |
| 警戒 | `#f97316` |
| 关注 | `#f59e0b` |
| 正常 | `#22c55e` |
| 平均值和主强调 | `#0ea5e9` |

### 4. 表格状态圆点

| 属性 | 数值 |
|------|------|
| 直径 | 8px - 10px |
| 颜色 | 跟随风险等级 |
| 与文字间距 | 8px |

### 5. Badge 规范

| 属性 | 数值 |
|------|------|
| 尺寸 | padding 4px 10px |
| 背景色 | 跟随状态色，opacity 0.12 |
| 文字颜色 | 跟随状态色 |
| 圆角 | 6px |
| 字号 | 11px - 12px |

## 十四、交互流程

### 1. 导航切换
- **触发元素**：AppHeader 顶部胶囊 或 SidebarNav 纵向菜单。
- **触发条件**：click。
- **状态变化**：`react-router-dom` 路由变更，`pathname` 更新。
- **UI 反馈**：两边导航同步高亮；页面内容切换（`Outlet` 或条件渲染）。
- **涉及数据**：路由状态。
- **当前阶段**：前端路由模拟。

### 2. 总览页查看全部
- **触发元素**：LatestReadingsTable 右上角"查看全部"按钮。
- **触发条件**：click。
- **状态变化**：`navigate('/data')`。
- **UI 反馈**：页面切换至数据分析页。
- **涉及数据**：无。
- **当前阶段**：前端模拟。

### 3. 总览页点击告警摘要
- **触发元素**：AlertSummaryPanel 某一行。
- **触发条件**：click。
- **状态变化**：`navigate('/data')`，可附带 query 参数如 `?alertLevel=danger`。
- **UI 反馈**：数据分析页加载，筛选项自动匹配（前端模拟）。
- **涉及数据**：alertLevel。
- **当前阶段**：前端模拟。

### 4. 地图页点击设备点
- **触发元素**：LakeRiskMap 上的 CircleMarker / MapMarkerPlaceholder。
- **触发条件**：click。
- **状态变化**：`selectedDeviceId` state 更新为对应设备 ID。
- **UI 反馈**：marker 放大 + 加粗边框；右侧 SelectedDevicePanel 切换为详情；地图可能轻微 pan 居中。
- **涉及数据**：`demoReadings` 对应设备。
- **当前阶段**：前端模拟。

### 5. 地图页切换热力图
- **触发元素**：MapLayerToggle 的"热力图层"按钮。
- **触发条件**：click。
- **状态变化**：`showHeatLayer` boolean state 切换。
- **UI 反馈**：按钮激活态变化；地图上热力图显示/隐藏。
- **涉及数据**：`demoReadings`。
- **当前阶段**：前端模拟。

### 6. 地图页切换设备图层
- **触发元素**：MapLayerToggle 的"设备图层"按钮。
- **触发条件**：click。
- **状态变化**：`showDevices` boolean state 切换。
- **UI 反馈**：按钮激活态变化；设备 marker 显示/隐藏。
- **涉及数据**：`demoReadings`。
- **当前阶段**：前端模拟。

### 7. 地图页查看历史数据
- **触发元素**：SelectedDevicePanel 底部"查看历史数据"按钮。
- **触发条件**：click。
- **状态变化**：`navigate('/data?deviceId=' + selectedDeviceId)`。
- **UI 反馈**：跳转数据分析页，设备筛选器自动选中该设备（前端模拟）。
- **涉及数据**：`selectedDeviceId`。
- **当前阶段**：前端模拟。

### 8. 数据分析页筛选时间范围
- **触发元素**：DataFilterBar 时间范围选择器。
- **触发条件**：change / 日期选择完成。
- **状态变化**：`filterState.timeRangeStart/End` 更新。
- **UI 反馈**：趋势图数据重新过滤渲染；如无可显示 toast。
- **涉及数据**：`demoDeviceHistory` 按时间过滤。
- **当前阶段**：前端模拟。

### 9. 数据分析页筛选设备
- **触发元素**：DataFilterBar 设备筛选器。
- **触发条件**：change。
- **状态变化**：`filterState.deviceIds` 更新。
- **UI 反馈**：趋势图和对比面板数据更新。
- **涉及数据**：`demoReadings` / `demoDeviceHistory`。
- **当前阶段**：前端模拟。

### 10. 数据分析页筛选传感器
- **触发元素**：DataFilterBar 传感器筛选器。
- **触发条件**：change。
- **状态变化**：`filterState.sensors` 更新。
- **UI 反馈**：趋势图折线显示/隐藏对应 Y 轴。
- **涉及数据**：`filterState.sensors`。
- **当前阶段**：前端模拟。

### 11. 数据分析页导出数据
- **触发元素**：DataFilterBar"导出数据"按钮。
- **触发条件**：click。
- **状态变化**：触发下载模拟。
- **UI 反馈**：按钮 loading 态 1s → toast "数据导出成功"。
- **涉及数据**：当前筛选后的数据。
- **当前阶段**：前端模拟（生成 CSV Blob 下载真实体验更佳）。

### 12. 设备页添加设备
- **触发元素**：DeviceToolbar"添加设备"按钮。
- **触发条件**：click。
- **状态变化**：`DeviceFormModal` 打开（mode: 'add'）。
- **UI 反馈**：Modal 遮罩 + 表单（名称、类型、位置等）。
- **涉及数据**：表单输入 → 追加到 devices state。
- **当前阶段**：前端模拟。

### 13. 设备页编辑设备
- **触发元素**：设备卡片内编辑按钮（设计图中未明确，建议卡片右上角菜单）。
- **触发条件**：click。
- **状态变化**：`DeviceFormModal` 打开（mode: 'edit'），预填充数据。
- **UI 反馈**：Modal 表单带当前值。
- **涉及数据**：选中 device。
- **当前阶段**：前端模拟。

### 14. 设备页删除设备
- **触发元素**：批量操作 → 批量删除 / 单卡片删除菜单。
- **触发条件**：click → 二次确认。
- **状态变化**：从 devices state 移除。
- **UI 反馈**：卡片淡出动画。
- **涉及数据**：选中 device IDs。
- **当前阶段**：前端模拟。

### 15. 设备页拖拽排序
- **触发元素**：DeviceCard 顶部拖拽手柄。
- **触发条件**：drag end（@dnd-kit）。
- **状态变化**：`devices` 数组 reorder（`arrayMove`）。
- **UI 反馈**：卡片位置动画交换；拖拽时 opacity 0.8 + rotate(2deg)。
- **涉及数据**：`devices` 数组顺序。
- **当前阶段**：前端模拟。

### 16. 设备页扫描附近设备
- **触发元素**：PairingPanel 自动加载 / 手动刷新。
- **触发条件**：mount / click。
- **状态变化**：`discoveredDevices` 数组更新。
- **UI 反馈**：RadarScanner 动画启动；2-3 秒后列表出现模拟设备。
- **涉及数据**：`mockDiscoveredDevices`。
- **当前阶段**：前端模拟。

### 17. 设备页蓝牙配对
- **触发元素**：DiscoveredDeviceItem 的"蓝牙配对"按钮。
- **触发条件**：click。
- **状态变化**：按钮 loading → 1.2s 后设备添加到 `devices`（status: idle, connectionType: bluetooth）。
- **UI 反馈**：按钮 spinner → "已配对" → 新卡片出现在网格。
- **涉及数据**：`DiscoveredDevice` → `MonitoringDevice`。
- **当前阶段**：前端模拟。

### 18. 设备页 WiFi 连接
- **触发元素**：DiscoveredDeviceItem 的"WiFi 连接"按钮。
- **触发条件**：click。
- **状态变化**：按钮 loading → 1.2s 后设备添加到 `devices`（status: online, connectionType: wifi）。
- **UI 反馈**：同上。
- **涉及数据**：`DiscoveredDevice` → `MonitoringDevice`。
- **当前阶段**：前端模拟。

### 19. 设备页断开连接
- **触发元素**：在线/待机设备卡片的"断开"按钮（如有）。
- **触发条件**：click。
- **状态变化**：设备 status → offline，connectionType → none。
- **UI 反馈**：状态圆点变灰，连接图标消失。
- **涉及数据**：选中 device。
- **当前阶段**：前端模拟。

### 20. 加载态、空状态、错误态

| 场景 | 加载态 | 空状态 | 错误态 |
|------|--------|--------|--------|
| 页面首次加载 | 骨架屏或全局 spinner | 无数据提示卡片 | "加载失败，请刷新重试" |
| 地图加载 | "地图加载中..." 脉冲文字 | 无设备提示 | "地图加载失败" + 重试按钮 |
| 图表数据 | 图表区域 skeleton | "暂无数据" 居中 | — |
| 设备列表 | 卡片网格 skeleton | "暂无设备" | — |
| 扫描设备 | RadarScanner 旋转动画 | "未发现设备" | — |

## 十五、组件拆分方案

### common 目录

| 组件名 | 文件路径 | 所属页面 | 功能 | props | state | 可复用 | 依赖数据 | 依赖图片占位符 | 子组件 | 父组件 |
|--------|----------|----------|------|-------|-------|--------|----------|----------------|--------|--------|
| AquaPanel | `components/common/AquaPanel.tsx` | 全部 | 通用面板容器（背景、圆角、阴影、边框） | `children, className, title, subtitle` | 无 | 是 | 否 | 否 | — | 各页面 |
| AquaCard | `components/common/AquaCard.tsx` | 全部 | 通用卡片容器 | `children, className, hoverable, selected` | 无 | 是 | 否 | 否 | — | 各页面 |
| IconPlaceholder | `components/common/IconPlaceholder.tsx` | 全部 | 图标占位符（固定 20px-48px） | `name, size, fallback` | 无 | 是 | 否 | 否 | — | 各组件 |
| ImagePlaceholder | `components/common/ImagePlaceholder.tsx` | 全部 | 图片占位符（固定任意宽高） | `name, width, height, src, fallback` | `error` | 是 | 否 | 是 | — | 各组件 |
| StatusBadge | `components/common/StatusBadge.tsx` | 全部 | 在线/待机/离线状态 Badge | `status` | 无 | 是 | 否 | 否 | — | DeviceCard, SelectedDevicePanel 等 |
| RiskBadge | `components/common/RiskBadge.tsx` | 全部 | 风险等级 Badge | `toxin` 或 `level` | 无 | 是 | 否 | 否 | — | MetricSummaryCard, DeviceCard 等 |
| EmptyAssetSlot | `components/common/EmptyAssetSlot.tsx` | 全部 | 素材缺失时的 fallback 插槽 | `label, width, height` | 无 | 是 | 否 | 否 | — | 各占位符组件 |
| AppButton | `components/common/AppButton.tsx` | 全部 | 统一按钮（primary/secondary/ghost） | `variant, size, children, onClick, icon` | 无 | 是 | 否 | 否 | — | 各页面 |
| AppSelect | `components/common/AppSelect.tsx` | 全部 | 统一选择器 | `options, value, onChange, placeholder` | `open` | 是 | 否 | 否 | — | DataFilterBar 等 |

### layout 目录

| 组件名 | 文件路径 | 所属页面 | 功能 | props | state | 可复用 | 依赖数据 | 依赖图片占位符 | 子组件 | 父组件 |
|--------|----------|----------|------|-------|-------|--------|----------|----------------|--------|--------|
| AppShell | `layouts/AppShell.tsx` | 全部 | 全局布局壳（PageFrame + Header + Sidebar + MainContent） | `children` | 无 | 是 | 否 | 是 | AppHeader, SidebarNav, PageFrame | App |
| AppHeader | `layouts/AppHeader.tsx` | 全部 | 顶部导航栏（Logo + 标题 + 胶囊导航 + 用户区 + 吉祥物） | — | 无 | 是 | 否 | 是 | IconPlaceholder, ImagePlaceholder | AppShell |
| SidebarNav | `layouts/SidebarNav.tsx` | 全部 | 左侧边栏导航 + 气泡/吉祥物/水波装饰 | — | 无 | 是 | 否 | 是 | IconPlaceholder, ImagePlaceholder | AppShell |
| PageFrame | `layouts/PageFrame.tsx` | 全部 | 页面最外层容器（背景、圆角、水波装饰） | `children` | 无 | 是 | 否 | 是 | — | AppShell |

### overview 目录

| 组件名 | 文件路径 | 所属页面 | 功能 | props | state | 可复用 | 依赖数据 | 依赖图片占位符 | 子组件 | 父组件 |
|--------|----------|----------|------|-------|-------|--------|----------|----------------|--------|--------|
| MetricSummaryCard | `components/overview/MetricSummaryCard.tsx` | 总览页 | 顶部 5 张指标卡之一 | `title, value, unit, subtitle, iconPlaceholder, color` | 无 | 是 | 是 | 是 | IconPlaceholder | OverviewPage |
| SystemStatusPanel | `components/overview/SystemStatusPanel.tsx` | 总览页 | 系统运行状态展示 | `summary` | 无 | 否 | 是 | 是 | IconPlaceholder | OverviewPage |
| AlertSummaryPanel | `components/overview/AlertSummaryPanel.tsx` | 总览页 | 四级告警统计列表 | `readings` | 无 | 否 | 是 | 是 | IconPlaceholder | OverviewPage |
| OverviewTrendChart | `components/overview/OverviewTrendChart.tsx` | 总览页 | 近7天平均毒素趋势图 | `historyData` | 无 | 否 | 是 | 否 | — | OverviewPage |
| LatestReadingsTable | `components/overview/LatestReadingsTable.tsx` | 总览页 | 最新采样表格 | `readings, maxRows` | 无 | 否 | 是 | 否 | — | OverviewPage |

### map 目录

| 组件名 | 文件路径 | 所属页面 | 功能 | props | state | 可复用 | 依赖数据 | 依赖图片占位符 | 子组件 | 父组件 |
|--------|----------|----------|------|-------|-------|--------|----------|----------------|--------|--------|
| LakeRiskMap | `components/map/LakeRiskMap.tsx` | 地图页 | 地图主容器（MapContainer + TileLayer + HeatLayer + Markers） | `readings, selectedId, onSelect` | `showHeat, showDevices` | 否 | 是 | 是 | MapMarkerPlaceholder, MapLayerToggle, RiskLegend | MapMonitorPage |
| RiskLegend | `components/map/RiskLegend.tsx` | 地图页 | 地图底部风险图例浮层 | — | 无 | 是 | 否 | 否 | — | LakeRiskMap |
| SelectedDevicePanel | `components/map/SelectedDevicePanel.tsx` | 地图页 | 右侧设备详情 / 湖泊概况 | `reading, history, onBack` | 无 | 否 | 是 | 是 | ImagePlaceholder, AquaCard | MapMonitorPage |
| MapLayerToggle | `components/map/MapLayerToggle.tsx` | 地图页 | 设备图层/热力图层开关 | `showHeat, showDevices, onToggle` | 无 | 是 | 否 | 是 | IconPlaceholder | LakeRiskMap |
| MapMarkerPlaceholder | `components/map/MapMarkerPlaceholder.tsx` | 地图页 | 自定义 Marker（解决 Leaflet 默认图标 404） | `reading, selected, onClick` | 无 | 是 | 否 | 是 | — | LakeRiskMap |
| MapController | `components/map/MapController.tsx` | 地图页 | 地图大小控制/定位按钮 | — | 无 | 是 | 否 | 否 | — | LakeRiskMap |

### data 目录

| 组件名 | 文件路径 | 所属页面 | 功能 | props | state | 可复用 | 依赖数据 | 依赖图片占位符 | 子组件 | 父组件 |
|--------|----------|----------|------|-------|-------|--------|----------|----------------|--------|--------|
| DataFilterBar | `components/data/DataFilterBar.tsx` | 数据分析页 | 顶部筛选栏 | `filter, onChange, devices` | 无 | 否 | 是 | 是 | AppSelect, AppButton, IconPlaceholder | DataAnalysisPage |
| MultiMetricTrendChart | `components/data/MultiMetricTrendChart.tsx` | 数据分析页 | 三Y轴趋势折线图 | `data, sensors` | 无 | 否 | 是 | 是 | — | DataAnalysisPage |
| SensorComparisonPanel | `components/data/SensorComparisonPanel.tsx` | 数据分析页 | 传感器对比排行 | `readings` | 无 | 否 | 是 | 否 | — | DataAnalysisPage |
| ToxinPredictionPanel | `components/data/ToxinPredictionPanel.tsx` | 数据分析页 | AI 预测 AreaChart + 置信度卡 | `predictionData` | `timeRange` | 否 | 是 | 是 | IconPlaceholder | DataAnalysisPage |

### device 目录

| 组件名 | 文件路径 | 所属页面 | 功能 | props | state | 可复用 | 依赖数据 | 依赖图片占位符 | 子组件 | 父组件 |
|--------|----------|----------|------|-------|-------|--------|----------|----------------|--------|--------|
| DeviceToolbar | `components/device/DeviceToolbar.tsx` | 设备页 | 顶部操作栏 | `onAdd, onRefresh, onBatch` | 无 | 否 | 否 | 是 | AppButton, IconPlaceholder | DevicePairingPage |
| DeviceCardGrid | `components/device/DeviceCardGrid.tsx` | 设备页 | DndContext + SortableContext 容器 | `devices, selectedIds, onSelect` | 无 | 否 | 是 | 否 | DeviceCard | DevicePairingPage |
| DeviceCard | `components/device/DeviceCard.tsx` | 设备页 | 单台设备信息卡 | `device, selected, dragHandleProps` | 无 | 是 | 是 | 是 | ImagePlaceholder, StatusBadge, RiskBadge, IconPlaceholder | DeviceCardGrid |
| DeviceSortDropZone | `components/device/DeviceSortDropZone.tsx` | 设备页 | 拖拽排序提示区 | — | 无 | 是 | 否 | 是 | IconPlaceholder | DevicePairingPage |
| PairingPanel | `components/device/PairingPanel.tsx` | 设备页 | 右侧添加新设备/扫描面板 | `discoveredDevices, onPair` | `scanning` | 否 | 是 | 是 | RadarScanner, DiscoveredDeviceItem, ImagePlaceholder | DevicePairingPage |
| DeviceFormModal | `components/device/DeviceFormModal.tsx` | 设备页 | 添加/编辑设备弹窗 | `mode, device, onSave, onClose` | `form` | 是 | 否 | 否 | — | DevicePairingPage |
| DiscoveredDeviceItem | `components/device/DiscoveredDeviceItem.tsx` | 设备页 | 单个发现设备项 | `device, onPairBluetooth, onPairWifi` | 无 | 是 | 否 | 是 | AppButton | PairingPanel |
| RadarScanner | `components/device/RadarScanner.tsx` | 设备页 | 雷达扫描动画区域 | `scanning` | 无 | 是 | 否 | 是 | ImagePlaceholder | PairingPanel |

## 十六、素材占位符实现规范

由于 `./Materials/{对应页面名称}` 目前没有任何图片，必须规定如何实现占位符。

### 1. 占位符组件体系

所有图片和图标先用占位符组件显示。占位符组件名称：
- `ImagePlaceholder` — 用于大尺寸图片（设备插画、吉祥物、装饰图）。
- `IconPlaceholder` — 用于小尺寸图标（24px-48px 的功能图标）。
- `EmptyAssetSlot` — 最底层 fallback，显示文字标签。

### 2. 占位符必须具备的属性

- **固定宽高**：通过 props `width` `height` 或 Tailwind 类严格限定，不得使用 `auto` 导致布局塌陷。
- **参与正常排版**：占位符是真实 DOM 节点，占满规定空间，margin/padding 与其他元素一致。
- **缺失不改变布局**：无论真实图片是否存在，外层容器尺寸不变。
- **内部显示**：素材名称、推荐文件名、推荐尺寸，使用 10px-11px 文字居中显示。
- **外观**：浅蓝半透明背景 `rgba(14,165,233,0.06)`，虚线边框 `1px dashed rgba(14,165,233,0.3)`，圆角 12px，文字颜色 `--color-muted`，可选 lucide-react `Image` 小图标。

### 3. 真实图片替换机制

未来真实图片放入 Materials 后，只需要替换 `assetMap` 中的路径即可，无需修改组件代码。

### 4. 图片加载失败处理

- 图片加载失败时继续显示占位符（`onError` 事件将 `img` 隐藏，显示底层占位符）。
- 不允许代码直接假设图片一定存在（不得使用无 fallback 的裸 `<img>`）。

### 5. 建议 assetMap 结构

```typescript
// src/assets/assetMap.ts
export const assetMap = {
  common: {
    logoOcean: '/Materials/General/logo-ocean.png',
    headerMascotSmall: '/Materials/General/mascot-header-small.png',
    sidebarMascotLarge: '/Materials/General/mascot-sidebar-large.png',
    bubbleDecoration: '/Materials/General/bubble.png',
    waveDecoration: '/Materials/General/wave.png',
  },
  overview: {
    systemShieldIcon: '/Materials/Overview/icon-shield.png',
    onlineIcon: '/Materials/Overview/icon-online.png',
    idleIcon: '/Materials/Overview/icon-idle.png',
    offlineIcon: '/Materials/Overview/icon-offline.png',
    averageToxinIcon: '/Materials/Overview/icon-toxin.png',
    riskIcon: '/Materials/Overview/icon-risk.png',
    alertIcon: '/Materials/Overview/icon-alert.png',
  },
  map: {
    markerNormal: '/Materials/Map/marker-normal.png',
    markerAttention: '/Materials/Map/marker-attention.png',
    markerWarning: '/Materials/Map/marker-warning.png',
    markerDanger: '/Materials/Map/marker-danger.png',
    selectedDeviceIllustration: '/Materials/Map/device-illustration.png',
    bottomMascot: '/Materials/Map/mascot-map-bottom.png',
    layerIcon: '/Materials/Map/icon-layer.png',
    locationIcon: '/Materials/Map/icon-location.png',
  },
  data: {
    microscopeDecoration: '/Materials/Data/microscope-decoration.png',
    trendWarningIcon: '/Materials/Data/icon-warning-triangle.png',
    exportIcon: '/Materials/Data/icon-export.png',
    confidenceIcon: '/Materials/Data/icon-confidence.png',
    predictionIcon: '/Materials/Data/icon-prediction.png',
    waveDecoration: '/Materials/Data/wave-data.png',
  },
  drive: {
    cardBuoy: '/Materials/Drive/device-buoy.png',
    cardProbe: '/Materials/Drive/device-probe.png',
    cardOffline: '/Materials/Drive/device-offline.png',
    scanBluetooth: '/Materials/Drive/icon-bluetooth-large.png',
    bottomMascot: '/Materials/Drive/mascot-device-bottom.png',
    labFlask: '/Materials/Drive/lab-flask.png',
    addIcon: '/Materials/Drive/icon-add.png',
    refreshIcon: '/Materials/Drive/icon-refresh.png',
    dragIcon: '/Materials/Drive/icon-drag.png',
    wifiIcon: '/Materials/Drive/icon-wifi.png',
    batteryIcon: '/Materials/Drive/icon-battery.png',
    signalIcon: '/Materials/Drive/icon-signal.png',
  },
};
```

> 当前文件不存在时必须 fallback 到占位符组件。

## 十七、Vite 重构迁移步骤

### 步骤 1：审计旧项目
- **目标**：梳理可复用代码、需重写代码、需废弃代码。
- **涉及文件**：全部旧项目文件。
- **注意事项**：标记所有 `next/*` 导入、`app router` 文件、`ssr: false` 模式。
- **验收方式**：产出审计清单。

### 步骤 2：初始化 Vite React TypeScript 项目
- **目标**：创建空白 Vite 项目，选用 React 18 稳定版本。
- **涉及文件**：`package.json`, `vite.config.ts`, `tsconfig.json`, `index.html`。
- **注意事项**：`npm create vite@latest web -- --template react-ts`；将 React 版本手动锁定为 `^18.3.1`。
- **验收方式**：`npm install` 成功，`npm run dev` 能打开默认页面。

### 步骤 3：安装依赖
- **目标**：安装全部必要依赖。
- **涉及文件**：`package.json`。
- **注意事项**：使用 `--legacy-peer-deps` 确保低版本图表组件稳定兼容。
- **验收方式**：`node_modules` 完整，无安装报错。

### 步骤 4：建立 src 目录结构
- **目标**：按规范创建全部目录和空文件。
- **涉及文件**：`src/**` 全部目录。
- **验收方式**：目录树与规范一致。

### 步骤 5：迁移并对齐旧项目 mock data 与算法逻辑
- **目标**：完整平移 `demoReadings.ts` 的数据和工具函数，并对齐新类型定义。
- **涉及文件**：`src/data/demoReadings.ts`, `src/data/mockDevices.ts`, `src/data/mockHistory.ts`。
- **注意事项**：旧 `RiskLevel` 的 `watch` → `attention`，`critical` → `danger`；新增 `type` 字段，按名称规则推断；字段名对齐新规范（`toxinUgL` → `toxin` 等）。
- **验收方式**：所有工具函数（`getRiskLevel`, `getRiskColor`, `getSignalLabel`, `normalizeHeatValue`）在新项目中可用且结果一致。

### 步骤 6：迁移类型定义
- **目标**：建立 `src/types/domain.ts`，包含全部 TypeScript 类型。
- **涉及文件**：`src/types/domain.ts`。
- **注意事项**：类型必须与数据模型章节完全一致。
- **验收方式**：TypeScript 无类型错误。

### 步骤 7：建立风险计算工具函数
- **目标**：创建 `src/utils/risk.ts`，导出所有风险/状态/格式化工具。
- **涉及文件**：`src/utils/risk.ts`, `src/utils/format.ts`, `src/utils/chart.ts`。
- **注意事项**：严禁后续组件内硬编码风险色值。
- **验收方式**：单元测试或手动验证阈值边界。

### 步骤 8：建立全局样式 token
- **目标**：在全局 `globals.css` 中建立符合 Tailwind v4 的 `@theme` 变量层。
- **涉及文件**：`src/styles/tokens.css`, `src/styles/globals.css`, `src/styles/layout.css`。
- **注意事项**：导入 Tailwind CSS v4：`@import "tailwindcss"`；导入 Leaflet CSS：`@import "leaflet/dist/leaflet.css"`；定义浅色主题变量，废弃暗色媒体查询。
- **验收方式**：页面背景为浅蓝色 `#f0f7ff`，文字为深色 `#0f172a`。

### 步骤 9：建立 AppShell
- **目标**：创建全局布局壳，包含 PageFrame + Header + Sidebar。
- **涉及文件**：`src/layouts/AppShell.tsx`, `src/layouts/PageFrame.tsx`。
- **注意事项**：确保 MainContent 独立滚动。
- **验收方式**：四页共享同一套布局，切换页面时 Header/Sidebar 不闪烁不重建。

### 步骤 10：建立 Header 和 Sidebar
- **目标**：实现双导航联动。
- **涉及文件**：`src/layouts/AppHeader.tsx`, `src/layouts/SidebarNav.tsx`。
- **注意事项**：共享 `useLocation().pathname`；吉祥物父容器 `overflow-visible`。
- **验收方式**：点击顶部导航，侧边栏同步高亮；反之亦然。

### 步骤 11：建立 react-router-dom 路由
- **目标**：配置四页路由。
- **涉及文件**：`src/router/routes.tsx`, `src/App.tsx`。
- **注意事项**：使用 `createBrowserRouter` 或 `BrowserRouter + Routes/Route`。
- **验收方式**：`/`、`/map`、`/data`、`/device` 正确渲染对应页面。

### 步骤 12：实现总览页
- **目标**：完成 OverviewPage 及全部子组件。
- **涉及文件**：`src/pages/OverviewPage.tsx` + `components/overview/*`。
- **注意事项**：所有占位符尺寸固定，参与排版。
- **验收方式**：与设计蓝图结构一致，5 张指标卡 + 三面板 + 表格可见。

### 步骤 13：实现地图页
- **目标**：完成 MapMonitorPage 及全部子组件，特别注意 Leaflet 生命周期。
- **涉及文件**：`src/pages/MapMonitorPage.tsx` + `components/map/*`。
- **注意事项**：热力图数据 `useMemo` 缓存；清理函数中显式 `map.removeLayer`；解决 Leaflet 默认 Marker 路径 404：显式 `L.Icon.Default.mergeOptions` 或全量自定义 `L.icon`。
- **验收方式**：地图渲染正常，热力图/设备点可切换，选中设备右侧详情更新。

### 步骤 14：实现数据分析页
- **目标**：完成 DataAnalysisPage 及全部子组件。
- **涉及文件**：`src/pages/DataAnalysisPage.tsx` + `components/data/*`。
- **注意事项**：三 Y 轴独立刻度映射；图表父容器固定高度 `h-[380px]` + `relative`；超阈值红色三角 Marker。
- **验收方式**：三轴趋势图正常显示，无高度塌陷，AI 预测图可见。

### 步骤 15：实现设备配对页
- **目标**：完成 DevicePairingPage 及全部子组件。
- **涉及文件**：`src/pages/DevicePairingPage.tsx` + `components/device/*`。
- **注意事项**：设备插画按 `type` 动态条件渲染；RadarScanner 3 层虚线圆环 + 中心 72px 蓝牙占位符；@dnd-kit 拖拽保持 5px 激活距离。
- **验收方式**：卡片网格 3 列，拖拽可排序，雷达扫描动画正常。

### 步骤 16：替换 Next.js 专属代码
- **目标**：全局移除 Next.js 残留。
- **涉及文件**：全部 `src/**/*.tsx`。
- **注意事项**：移除 `next/link` → `react-router-dom Link`；移除 `next/image` → `<img>` 或 ImagePlaceholder；移除 `next/dynamic` → 普通 `React.lazy` 或直接导入；移除 `usePathname` → `react-router-dom useLocation`。
- **验收方式**：全局搜索 `next/` 无业务代码引用。

### 步骤 17：处理 Leaflet 默认 Marker 路径崩溃 Bug
- **目标**：解决 Vite 静态资源编译散列化后的路径丢失问题。
- **涉及文件**：`src/components/map/LakeRiskMap.tsx` 或地图初始化模块。
- **注意事项**：显式调用 `L.Icon.Default.mergeOptions` 并导入本地图标；或统一自定义全量 Marker 的 `L.icon` 结构，彻底断绝地图 Marker 加载出 404 碎片报错的问题。
- **验收方式**：地图加载后控制台无 404 碎片报错。

### 步骤 18：实现图片占位符系统
- **目标**：确保 Materials 为空时页面完整显示。
- **涉及文件**：`src/components/common/ImagePlaceholder.tsx`, `src/assets/assetMap.ts`。
- **注意事项**：所有图片使用 ImagePlaceholder 包裹，onError fallback。
- **验收方式**：删除 Materials 中所有文件（当前本就是空），页面无错位、无报错。

### 步骤 19：实现 mock service 层
- **目标**：建立 `src/services/*`，当前返回 mock data。
- **涉及文件**：`src/services/readingsService.ts`, `src/services/deviceService.ts`, `src/services/predictionService.ts`。
- **注意事项**：函数签名按真实 API 设计，内部暂时返回 mock data。
- **验收方式**：组件调用 service 而非直接 import data 文件（或两者并存，service 包装 data）。

### 步骤 20：进行构建和验收
- **目标**：`npm run build` 成功，产物可预览。
- **涉及文件**：`dist/`。
- **注意事项**：检查产物中无 Next.js 残留，Leaflet 图片资源正确打包。
- **验收方式**：`npm run preview` 正常，四页可访问。

## 十八、验收标准

### 1. 技术验收

- [ ] `npm install` 成功。
- [ ] `npm run dev` 成功，开发服务器正常启动。
- [ ] `npm run build` 成功，无构建错误。
- [ ] `npm run preview` 成功，可预览生产产物。
- [ ] 无 TypeScript 关键错误（允许 any 类型的临时妥协，但不得有未定义变量等硬错误）。
- [ ] 无明显控制台运行错误（无 404 资源、无 React key warning、无 Leaflet 报错）。

### 2. 页面验收

- [ ] `/` 正常显示总览页。
- [ ] `/map` 正常显示地图监视页。
- [ ] `/data` 正常显示数据分析页。
- [ ] `/device` 正常显示设备配对页。
- [ ] 路由切换流畅，无白屏或闪烁。

### 3. 视觉验收

- [ ] 四页整体接近设计蓝图。
- [ ] 使用浅色青蓝水体实验风（背景 `#f0f7ff`，卡片白色，主色 `#0ea5e9`）。
- [ ] Header、Sidebar、MainContent 一致且稳定。
- [ ] 卡片、按钮、图表、表格风格统一。
- [ ] 所有图片和图标即使缺失，也有正确尺寸的占位符，页面不塌陷。
- [ ] 页面不会因为 Materials 为空而错位或报错。
- [ ] 吉祥物/装饰图溢出边界时完整可见，不被截断。

### 4. 功能验收

- [ ] 总览页：5 项指标、系统状态、告警摘要、趋势图、最新采样表格可见。
- [ ] 地图页：设备点位、热力图、图例、右侧详情可见；点击设备点切换详情。
- [ ] 数据分析页：筛选栏、三轴趋势图、传感器对比、AI 预测可见。
- [ ] 设备页：设备卡片（按 type 不同插画）、拖拽排序、扫描面板、配对按钮可见。
- [ ] 所有交互至少有前端模拟反馈（loading、toast、状态变化）。

### 5. 响应式验收

- [ ] 桌面端 1280px - 1600px 效果最佳。
- [ ] 小屏幕下内容纵向堆叠（地图页右侧面板可下移，设备卡片网格变 2 列或 1 列）。
- [ ] 不出现严重水平溢出（`overflow-x: hidden` 或自动换行）。
- [ ] 关键数据不被装饰图遮挡（吉祥物 `pointer-events-none` 或较低 z-index）。

## 十九、缺失信息与待确认问题

### 问题 1：旧数据缺少 `type` 字段，设备插画动态渲染的 type 值如何确定？

- **当前无法确认的原因**：旧 `demoReadings.ts` 中无 `type` 字段，仅有 `name`（如"湖心浮标-01"）。设计蓝图设备卡片显示不同插画（浮标、探针、巡检器等）。
- **建议默认方案**：在 mock data 中新增 `type` 字段，并通过名称关键词推断（含"浮标"→buoy，含"探针"/"巡检器"→probe，含"传感器"/"监测"→sensor，其他→other）。后续 Agent 按此规则生成 `mockDevices.ts`。
- **是否阻塞重构**：否，可通过命名规则推断解决。

### 问题 2：地图页右下角吉祥物/实验器材的确切尺寸和位置

- **当前无法确认的原因**：设计蓝图中地图页右下角有装饰元素，但截图比例有限，无法精确到像素。
- **建议默认方案**：吉祥物占位符 100px × 100px，实验器材占位符 80px × 80px，位于 `MapMonitorPage` 右下角，`position: absolute; right: 24px; bottom: 24px;`，z-index 25。
- **是否阻塞重构**：否。

### 问题 3：总览页趋势概览的数据来源（近 7 天平均值）在旧数据中未直接提供

- **当前无法确认的原因**：旧 `demoReadings` 只有单条最新读数，`demoDeviceHistory` 是每台设备过去 24 小时数据，没有跨设备日级聚合数据。
- **建议默认方案**：在 `src/data/mockHistory.ts` 中模拟生成近 7 天的日级平均数据（14 台设备每天平均 toxin），或基于 `demoDeviceHistory` 按小时聚合后取每日平均。后续 Agent 自行实现聚合逻辑。
- **是否阻塞重构**：否。

### 问题 4：设备卡片右上角选中勾的交互逻辑

- **当前无法确认的原因**：设计蓝图显示部分卡片有蓝色对勾，但未明确是单选还是多选。
- **建议默认方案**：单选逻辑（点击卡片选中一台设备，显示对勾），批量操作模式切换为多选复选框。默认状态为单选。
- **是否阻塞重构**：否。

### 问题 5：数据分析页"时间范围选择器"的具体组件形态

- **当前无法确认的原因**：设计蓝图显示为一个日期范围输入框，但未明确是自定义双日期输入还是使用第三方日期库。
- **建议默认方案**：使用两个原生 `<input type="date">` 组合，外层用一个圆角容器包裹，显示为 "2025-05-20 ~ 2025-05-27" 样式。不引入 moment/dayjs 等重量级日期库，减少依赖。
- **是否阻塞重构**：否。

### 问题 6：AppHeader 右上角吉祥物的具体设计图缺失

- **当前无法确认的原因**：设计蓝图 Header 中可见小吉祥物，但无独立素材文件。
- **建议默认方案**：使用通用 `header-mascot-small-placeholder`（84px × 84px），后续替换为真实吉祥物 PNG。
- **是否阻塞重构**：否。

---

*文档生成时间：2026-05-24*
*基于设计蓝图与旧项目代码分析编写*
*后续 Agent 可直接据此编码*



