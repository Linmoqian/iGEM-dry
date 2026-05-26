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

| 来源            | 路径                                                         | 用途                                                 |
| --------------- | ------------------------------------------------------------ | ---------------------------------------------------- |
|                 |                                                              |                                                      |
| 项目说明        | `/iGEM-dry/viewweb/planning/PROJECT.md`                      | 现有功能范围、页面范围、数据来源、交互能力、验收标准 |
| 项目结构说明    | `/iGEM-dry/viewweb/PROJECT_STRUCTURE.md`                     | 旧项目目录结构、组件说明、数据流、样式体系           |
| 依赖清单        | `/iGEM-dry/viewweb/package.json`                             | 分析当前依赖，标记保留/移除/新增                     |
| 总览页代码      | `/iGEM-dry/viewweb/app/page.tsx`                             | 旧总览页实现（暗色风，统计卡+最新采样+风险说明）     |
| 地图页代码      | `/iGEM-dry/viewweb/app/map/page.tsx`                         | 旧地图页入口                                         |
| 地图 Dashboard  | `/iGEM-dry/viewweb/app/map/MapDashboard.tsx`                 | 地图页主控制器、MetricChart、选中设备详情            |
| 地图组件        | `/iGEM-dry/viewweb/app/map/MonitoringMap.tsx`                | react-leaflet 热力图、CircleMarker、Popup 实现       |
| 地图加载器      | `/iGEM-dry/viewweb/app/map/MapClientLoader.tsx`              | next/dynamic SSR 隔离（需替换）                      |
| 数据分析页      | `/iGEM-dry/viewweb/app/data/page.tsx`                        | 旧数据分析页（统计卡+排行+设备健康+阈值）            |
| 设备页代码      | `/iGEM-dry/viewweb/app/device/page.tsx`                      | 旧设备页（拖拽排序、模态框、添加/连接模拟）          |
| 导航栏          | `/iGEM-dry/viewweb/app/components/Navbar.tsx`                | 旧顶部胶囊导航（需迁移为双导航）                     |
| 设备状态卡      | `/iGEM-dry/viewweb/app/components/DeviceStatus.tsx`          | 旧设备卡片组件（暗色风，可迁移逻辑）                 |
| AI 预测组件     | `/iGEM-dry/viewweb/app/components/ToxinPredictionModel.tsx`  | 旧 AreaChart 预测占位版（可迁移图表逻辑）            |
| 核心数据文件    | `/iGEM-dry/viewweb/app/lib/demoReadings.ts`                  | 14 台模拟设备、历史数据、风险计算工具函数            |
| 全局样式        | `/iGEM-dry/viewweb/app/globals.css`                          | Tailwind v4 导入、暗色变量、Leaflet popup 覆盖       |
| 根布局          | `/iGEM-dry/viewweb/app/layout.tsx`                           | 暗色背景、科技网格、环境光晕、Navbar 挂载            |
| TypeScript 配置 | `/iGEM-dry/viewweb/tsconfig.json`                            | 旧 Next.js tsconfig（需替换）                        |
| Next.js 配置    | `/iGEM-dry/viewweb/next.config.ts`                           | 空配置                                               |
| 设计蓝图        | `/iGEM-dry/viewweb/designe-figure/Page_design_objective/总览页目标.png` | 新视觉总览页                                         |
| 设计蓝图        | `/iGEM-dry/viewweb/designe-figure/Page_design_objective/地图监视页目标.png` | 新视觉地图页                                         |
| 设计蓝图        | `/iGEM-dry/viewweb/designe-figure/Page_design_objective/数据分析页目标.png` | 新视觉数据分析页                                     |
| 设计蓝图        | `/iGEM-dry/viewweb/designe-figure/Page_design_objective/设备配对页目标.png` | 新视觉设备配对页                                     |

## 三、技术路线

### 1. 目标技术栈表格

| 类别        | 技术                              | 用途                 | 是否必须 | 备注                                                     |
| ----------- | --------------------------------- | -------------------- | -------- | -------------------------------------------------------- |
| 构建工具    | Vite                              | 前端构建与开发服务器 | 必须     | 替代 Next.js，输出纯静态产物                             |
| UI 框架     | React 18.x                        | 组件化 UI            | 必须     | 稳定版以确保 Leaflet/Recharts 兼容；旧项目为 19.x 需降级 |
| 类型系统    | TypeScript                        | 类型安全             | 必须     | 保持 strict 模式                                         |
| 路由        | react-router-dom                  | SPA 路由             | 必须     | 替代 Next.js App Router                                  |
| 样式        | Tailwind CSS v4                   | 原子化 CSS           | 必须     | 使用 `@import "tailwindcss"` 语法，`@theme` 定义变量     |
| 图表        | Recharts                          | 折线/面积/多轴图表   | 必须     | 趋势图、AI 预测图                                        |
| 地图        | Leaflet + react-leaflet           | 地理地图渲染         | 必须     | 替代 next/dynamic SSR 隔离方案                           |
| 热力图      | leaflet.heat                      | 插值热力图层         | 必须     | 需自行处理 SPA 路由切换时的图层清理                      |
| 拖拽        | @dnd-kit/core + @dnd-kit/sortable | 设备卡片拖拽排序     | 必须     | 保持 PointerSensor 5px 激活距离                          |
| 图标        | lucide-react                      | 矢量图标             | 必须     | 替代内联 SVG，统一图标源                                 |
| 状态管理    | React useState/useMemo            | 组件级状态           | 必须     | 当前无需 Redux/Zustand                                   |
| 数据来源    | mock data (demoReadings.ts)       | 前端模拟数据         | 必须     | 不接真实后端                                             |
| 未来 API 层 | src/services/*                    | 预留 service 层      | 必须     | 当前返回 mock data，未来可替换为真实 API                 |
| 构建与部署  | Vite build + preview              | 静态产物             | 必须     | 输出到 dist/                                             |

### 2. Next.js 到 Vite 的迁移说明

| 旧技术                     | 新技术                                 | 替换原因                          | 迁移注意事项                                                 |
| -------------------------- | -------------------------------------- | --------------------------------- | ------------------------------------------------------------ |
| Next.js 16 App Router      | react-router-dom                       | SPA 路由更轻量，避免 SSR 水合问题 | 移除 `app/` 目录，改用 `src/pages/` + `src/router/routes.tsx` |
| `next/link`                | `react-router-dom` 的 `<Link>`         | 路由库切换                        | 全局替换 import 与使用方式                                   |
| `next/image`               | 原生 `<img>` 或自定义 ImagePlaceholder | Vite 无 next/image                | 图片统一走 `/Materials/` 静态目录                            |
| Next.js API routes         | 前端 mock service                      | 当前不接后端                      | 在 `src/services/` 中返回 mock data                          |
| SSR / Server Component     | 全部客户端组件                         | Leaflet/Recharts 依赖浏览器 API   | 移除 `'use client'` 区分，所有组件均在浏览器执行             |
| `app/layout.tsx`           | `src/layouts/AppShell.tsx`             | 布局结构迁移                      | 全局装饰、Header、Sidebar 统一在 AppShell 中管理             |
| `app/page.tsx`             | `src/pages/OverviewPage.tsx`           | 文件路由迁移                      | 路由映射：`/` 对应 OverviewPage                              |
| `next/dynamic(ssr: false)` | 条件渲染/懒加载                        | Vite 无 next/dynamic              | 地图组件直接导入，通过环境判断或 useEffect 延迟加载          |

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

## 