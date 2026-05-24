# viewweb 项目结构与使用规范

## 项目概览

基于 **Next.js 16 (App Router) + React 19 + TypeScript + Tailwind CSS 4** 的"水体藻毒素监测平台"前端项目。

核心依赖：Leaflet（地图）、Recharts（图表）、@dnd-kit（拖拽排序）。

---

## 根目录配置文件

| 文件 | 规范 |
|---|---|
| `package.json` | Next.js 16 项目声明，含 `dev/build/start/lint` 四个脚本；依赖分为 `dependencies`（运行时）和 `devDependencies`（构建时） |
| `next.config.ts` | Next.js 配置入口，当前为空，按需添加 `images`、`rewrites` 等 |
| `tsconfig.json` | TypeScript 主配置，继承 Next.js 的 strict 模式 |
| `eslint.config.mjs` | ESLint 配置，使用 `eslint-config-next` |
| `postcss.config.mjs` | PostCSS 配置，Tailwind CSS 4 的入口 |

---

## `app/` — Next.js App Router 源码目录

核心代码目录，遵循 **Next.js 文件路由 + 共置组件** 模式。

### `app/layout.tsx`

根布局文件。定义全局 HTML 结构：

- 暗色主题 (`dark`)、深蓝黑背景 (`#050714`)
- 科技网格 + 环境光晕背景效果
- 全局挂载 `<Navbar>` 顶部导航
- `<main>` 最大宽度 1400px 居中，顶部留出导航空间 (`mt-32`)
- **页面级组件必须在此布局内渲染**

### `app/page.tsx` — 路由：`/`

首页"总览"页。**服务端组件**（无 `'use client'` 指令）。

展示内容：

- 四个统计卡片（在线设备、平均藻毒素、最高风险、系统状态）
- 最新采样卡片列表（前 4 条）
- 风险说明侧栏
- 数据源来自 `lib/demoReadings`

### `app/globals.css`

全局样式文件：

- 导入 Tailwind CSS 4 (`@import "tailwindcss"`)
- 导入 Leaflet CSS (`@import "leaflet/dist/leaflet.css"`)
- 定义 CSS 变量（`--background`、`--foreground`）和 dark mode 媒体查询
- 覆盖 Leaflet popup 样式（浅色背景）

---

## `app/components/` — 共享组件

存放可复用的 UI 组件，全部为 **客户端组件** (`'use client'`)。

### `Navbar.tsx`

顶部导航栏组件。

- 使用 `usePathname()` 判断当前路由
- 激活项：展开显示完整标签（宽 140px、高亮 cyan 边框 + 内发光）
- 未激活项：收窄为竖排两行文字（宽 70px、灰色）
- 导航项：总览 (`/`) / 地图监视 (`/map`) / 数据分析 (`/data`) / 设备配对 (`/device`)
- 中文双字标签自动从中间拆分为两行（`splitLabel` 函数）

### `DeviceStatus.tsx`

设备状态卡片组件。

- 展示：设备名称、在线状态指示灯（绿/红/琥珀色脉冲）、连接类型图标（蓝牙/WiFi）、采样位置、藻毒素浓度（含风险等级色标 + 进度条）、电量进度条（<20% 变红）、信号强度中文标签、水温、pH
- 离线设备：显示"蓝牙连接"和"无线连接"两个操作按钮
- 底部固定"查看采样详情"按钮（hover 时 cyan 光照扫过效果）
- 支持 `dragHandleProps` 属性用于拖拽集成（顶部拖拽手柄）

### `ToxinPredictionModel.tsx`

AI 毒素爆发预测模型组件（占位版）。

- 使用 Recharts 的 `AreaChart` 展示过去 7 天历史数据 + 未来 7 天预测趋势
- 历史部分：实线 cyan，预测部分：虚线 purple + 置信区间
- 包含一条"危险阈值"参考线 (2.0 µg/L)
- 底部爆发预警提示卡片
- 标注"占位版"，数据为 `useMemo` 内模拟生成

---

## `app/lib/` — 数据层

**纯 TypeScript 逻辑，不含 JSX 和 React 组件。**

### `demoReadings.ts`

项目的核心数据文件，所有页面和组件的数据来源。

**类型定义：**

| 类型 | 说明 |
|---|---|
| `DeviceStatus` | `'online' \| 'offline' \| 'idle'` |
| `ConnectionType` | `'bluetooth' \| 'wifi' \| 'none'` |
| `RiskLevel` | `'normal' \| 'watch' \| 'warning' \| 'critical'` |
| `DeviceReading` | 设备采样读数接口（id、name、status、lat/lng、battery、signal、toxin、temp、pH 等） |
| `DeviceHistoryPoint` | 历史数据点接口（time、toxin、temp、pH、battery、signal） |

**静态数据：**

| 导出 | 说明 |
|---|---|
| `demoLake` | 演示湖泊地理信息（中心坐标 [30.5667, 114.3833]、bounds、名称、描述） |
| `demoReadings` | 14 台模拟采样设备完整数据集（武汉东湖周边坐标） |
| `demoDeviceHistory` | 每台设备过去 24 小时的模拟历史曲线（24 个数据点/台） |
| `demoSummary` | 聚合统计对象（在线数、低电量数、弱信号数、平均毒素、最高毒素设备） |

**工具函数：**

| 函数 | 说明 |
|---|---|
| `getDeviceHistory(deviceId)` | 按设备 ID 获取历史数据 |
| `getLatestReading(deviceId)` | 按设备 ID 获取最新读数 |
| `getRiskLevel(toxinUgL)` | 浓度 → 风险等级枚举（>5 critical, ≥1 warning, ≥0.5 watch, else normal） |
| `getRiskLabel(toxinUgL)` | 浓度 → 中文标签（正常/关注/警戒/高风险） |
| `getRiskColor(toxinUgL)` | 浓度 → 风险颜色（绿/黄/橙/红） |
| `getSignalLabel(signalDbm)` | 信号 → 中文标签（≥-70 良好, ≥-85 一般, else 弱信号） |
| `getStatusText(status)` | 状态枚举 → 中文（在线采样/待机/离线） |
| `normalizeHeatValue(toxinUgL)` | 浓度归一化到 [0.12, 1] 区间供热力图使用 |

---

## `app/data/` — 路由：`/data`

**数据分析页**（服务端组件，无 `'use client'`）。

页面结构：

1. **四个统计卡片**：平均藻毒素、在线设备数、低电量设备数、弱信号设备数
2. **`<ToxinPredictionModel>`**：AI 预测图表组件
3. **左栏 — 藻毒素浓度排行**：所有设备按 `toxinUgL` 降序排列，每项显示名称、风险标签、浓度进度条、数值
4. **右栏上部 — 设备健康**：每个设备的电量、信号标签和更新时间
5. **右栏下部 — 判定阈值**：四级风险等级的中文说明和数值范围

---

## `app/device/` — 路由：`/device`

**设备配对页**（客户端组件）。

核心功能：

- **拖拽排序**：使用 `@dnd-kit/core` + `@dnd-kit/sortable`，`PointerSensor` 设 5px 激活距离防止误触；`SortableDevice` 封装 `useSortable` hook，将 `transform`、`transition`、拖拽状态注入 `DeviceStatus`
- **接入新采样终端**：卡片列表末尾的虚线占位按钮，点击弹出模态框模拟配对流程，1.2 秒后生成临时设备追加到列表
- **离线设备连接**：蓝牙/WiFi 按钮点击后弹出加载模态框，1200ms 后设备状态变为 `idle`，更新信号值
- **查看采样详情**：弹出模态框展示设备完整信息（设备名、位置、毒素、信号、电量、水温、pH）
- 模态框分两种状态：加载中（spinner + "中断连接"按钮）和确认完成（绿色勾 + "确认"按钮）

---

## `app/map/` — 路由：`/map`

**地图监视页**，按职责拆分为三层组件。

### `page.tsx`

路由入口（服务端组件）。渲染页面标题（湖泊名称 + 描述）和 `<MapDashboard>`。

### `MapDashboard.tsx`

地图页主控制器（客户端组件）。

- 管理 `selectedDeviceId` 状态
- 左侧：640px 高地图容器，内嵌 `MapClientLoader`
- 右侧侧栏根据选中状态切换：
  - **未选设备**：湖泊概况 + 最高风险点 + 风险等级图例（四级色标）+ 采样节点列表（点击选中）
  - **已选设备**：设备详情卡片（名称、位置、浓度、风险等级、电量、信号）+ `MetricChart`（藻毒素历史曲线，含警戒/高风险阈值线）+ 水温/pH 历史曲线

### `MapClientLoader.tsx`

SSR 隔离层。

- 使用 `next/dynamic` 动态导入 `MonitoringMap` 并设置 `ssr: false`
- 加载时显示"地图加载中..."脉冲动画占位
- 确保 Leaflet（依赖 `window` 对象）仅在浏览器端执行

### `MonitoringMap.tsx`

地图核心组件（客户端组件）。

- 使用 `react-leaflet` 的 `<MapContainer>`，中心坐标取自 `demoLake.center`，缩放范围 11-17
- OpenStreetMap 瓦片图层
- **自定义热力图 `HeatLayer`**：
  - 原理：反距离加权插值（IDW），74×52 网格覆盖可视区域 + 0.18 padding
  - 每个网格点的毒素值由 14 个采样点加权计算
  - 使用 `leaflet.heat` 插件渲染，渐变从绿 → 黄绿 → 黄 → 橙 → 红
  - 热力图层放在独立 pane（`toxin-heat-pane`），`mixBlendMode: screen`
  - 监听 `moveend`、`zoomend`、`resize` 事件动态刷新
- **设备点位 `CircleMarker`**：颜色跟随风险等级，选中时放大 + 加粗边框
- Popup 显示：设备名、位置、藻毒素浓度 + 风险标签、电量、信号、水温、pH、更新时间

---

## `app/types/` — TypeScript 类型声明

### `leaflet-heat.d.ts`

`leaflet.heat` 插件的 TypeScript 类型声明文件。

- 扩展 `leaflet` 模块的类型定义
- 声明 `HeatLatLngTuple`、`HeatLayerOptions`、`HeatLayer` 类、`heatLayer` 工厂函数
- 声明 `leaflet.heat` 模块入口

---

## `public/` — 静态资源

存放由 Next.js 直接服务的静态文件。当前包含 Next.js 脚手架默认的 SVG 图标（`file.svg`、`globe.svg`、`next.svg`、`vercel.svg`、`window.svg`），项目中未实际引用。

---

## `designe-figure/` — 设计参考图

存放 UI 设计截图，仅供设计对照，不影响运行时：

- `顶部导航栏.webp`
- `地图组件.webp`
- `设备状态组件.webp`

---

## 其他目录

| 目录 | 说明 |
|---|---|
| `.next/` | Next.js 构建缓存和产物，**勿手动修改** |
| `dist/` | 构建输出目录 |
| `node_modules/` | npm 依赖，由 `package.json` 管理 |

---

## 关键约定总结

### 1. 路由模式

每个页面一个独立文件夹（`/`、`/data`、`/device`、`/map`），入口文件统一为 `page.tsx`。

### 2. 客户端 / 服务端边界

| 类型 | 说明 | 示例 |
|---|---|---|
| 服务端组件 | 静态展示、无需交互 | `/` (page.tsx)、`/data` (page.tsx)、`/map` (page.tsx) |
| 客户端组件 | 需交互、使用浏览器 API | `/device` (page.tsx)、所有 `components/`、`MapDashboard`、`MonitoringMap` |

### 3. 地图 SSR 隔离

通过 `MapClientLoader` 配合 `next/dynamic(ssr: false)` 确保 Leaflet（依赖 `window`）仅在客户端加载，避免服务端渲染报错。

### 4. 数据流

所有数据集中定义在 `lib/demoReadings.ts`，通过 ES Module 导出。页面和组件直接 `import` 使用，不作为 props 层层传递。这种模式适合演示和原型阶段；接入真实后端时替换该文件即可。

### 5. 样式体系

- Tailwind CSS 4 原子类优先
- 暗色科技风基调：底色 `#050714` / `#0B1221`，强调色 `cyan` / `blue`，风险色 `emerald` / `yellow` / `orange` / `rose`
- 卡片统一使用 `backdrop-blur` 毛玻璃效果 + `border-slate-700/50` 半透明边框
- 标题使用 `bg-clip-text text-transparent bg-gradient-to-r` 渐变文字
