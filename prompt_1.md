你是一名资深前端架构师、UI 规范设计师、网页重构文档工程师。你的任务不是直接编写完整网页代码，而是基于当前项目文件、四张网页设计蓝图和新增要求，编写一份高度详细、可执行的《网页重构有效信息文档 / Web Rebuild Specification》。

这份文档的使用对象是后续网页编写 Agent。后续 Agent 将在一个空白工作目录中，根据你输出的文档重新构建网页。因此，你必须把所有有效信息整理清楚，不能让后续 Agent 再去猜测页面结构、元素命名、元素大小、元素位置、图片占位符尺寸或技术路线。

最终输出文件：
/iGEM-dry/web/WEB_REBUILD_SPEC.md

━━━━━━━━━━━━━━━━━━━━
一、项目背景
━━━━━━━━━━━━━━━━━━━━

项目名称：水体藻毒素监测平台。

这是一个面向 iGEM 干实验团队的水体藻毒素监测 Dashboard。它不是宣传落地页，而是一个可操作的数据监控平台。

新网页需要严格参考四张设计蓝图进行重构：

1. 总览页目标图
/iGEM-dry/viewweb/designe-figure/Page_design_objective/总览页目标.png

2. 地图监视页目标图
/iGEM-dry/viewweb/designe-figure/Page_design_objective/地图监视页目标.png

3. 设备配对页目标图
/iGEM-dry/viewweb/designe-figure/Page_design_objective/设备配对页目标.png

4. 数据分析页目标图
/iGEM-dry/viewweb/designe-figure/Page_design_objective/数据分析页目标.png

当前已有项目说明文件：
/iGEM-dry/viewweb/planning/PROJECT.md

当前已有项目目录：
/iGEM-dry/viewweb

未来素材目录：
/iGEM-dry/web/Materials

素材目录约定：
/iGEM-dry/web/Materials/General
/iGEM-dry/web/Materials/Overview
/iGEM-dry/web/Materials/Map
/iGEM-dry/web/Materials/Data
/iGEM-dry/web/Materials/Drive

注意：目前 ./Materials/{对应页面名称} 中没有任何图片和图标。因此，文档中必须先规定所有图片、图标、吉祥物、装饰图、设备图、Logo 的占位符。占位符必须参与正常页面排版，并且尺寸必须按照目标设计蓝图中的对应元素大小进行规定。

━━━━━━━━━━━━━━━━━━━━
二、最终技术路线要求
━━━━━━━━━━━━━━━━━━━━

当前项目可能是 Next.js 项目，但本次重构目标不是继续使用 Next.js。

最终技术路线必须写为：

1. 构建工具
   - Vite

2. 前端框架
   - React (明确指定为稳定版 18.x，以确保 Leaflet 和 Recharts 的三方生态库完美兼容)
   - TypeScript

3. 路由
   - react-router-dom

4. 样式
   - Tailwind CSS v4
   - 必须建立统一设计变量。由于 Tailwind v4 彻底拥抱原生 CSS 变量，文档必须提供符合 Tailwind v4 规范的 `@theme` 变量定义块。

5. 图表
   - Recharts

6. 地图
   - Leaflet / React Leaflet
   - 热力图层可使用 leaflet.heat 或自定义热力图封装

7. 拖拽排序
   - @dnd-kit

8. 数据
   - 当前阶段只使用 mock data
   - 不接真实后端 API
   - 不接数据库
   - 不接 WebSocket
   - 不做真实硬件通信
   - 需要从旧项目迁移 demoReadings 或同类模拟数据

9. 后端
   - 当前不实现后端
   - 前端代码需要预留 service 层
   - service 层当前返回 mock data，未来可替换为 Node.js、Rust 或其他后端 API

请在文档中明确说明：

- 为什么从 Next.js 迁移到 Vite（避免 SSR 在图表和地图上的水合错误、减少包体积、提供纯静态产物以便未来无缝通过 Tauri/Capacitor 转化为手机应用并适配 Rust 后端）。
- 当前项目中的 Next.js 内容只作为迁移来源，不作为最终技术路线。
- 如果 PROJECT.md 与本次要求冲突，则功能要求参考 PROJECT.md，技术路线以 React + Vite 为准。
- 需要替换的 Next.js 专属内容包括：
  - app router 路由结构
  - next/link
  - next/image
  - Next.js API routes
  - SSR / Server Component 相关写法
  - app/page.tsx、app/layout.tsx 等结构
- 新项目应使用：
  - src/main.tsx
  - src/App.tsx
  - src/router/routes.tsx
  - src/pages/*
  - src/layouts/*
  - src/components/*
  - src/data/*
  - src/services/*
  - src/types/*
  - src/utils/*

━━━━━━━━━━━━━━━━━━━━
三、必须读取和总结的内容
━━━━━━━━━━━━━━━━━━━━

请读取并分析以下内容：

1. /iGEM-dry/viewweb/planning/PROJECT.md
   - 总结现有功能范围。
   - 总结页面范围。
   - 总结数据来源。
   - 总结交互能力。
   - 总结验收标准。
   - 注意：其中的 Next.js 技术栈仅作为旧项目状态，不作为最终目标。

2. /iGEM-dry/viewweb/package.json
   - 分析当前依赖。
   - 标记保留依赖。
   - 标记需要移除的 Next.js 依赖。
   - 标记迁移到 Vite 后需要新增的依赖（如 react-router-dom、lucide-react 等）。

3. 当前项目页面文件
   - 查找总览页。
   - 查找地图监视页。
   - 查找数据分析页。
   - 查找设备配对页。
   - 如果旧项目是 Next.js，请优先检查：
     /iGEM-dry/viewweb/app/page.tsx
     /iGEM-dry/viewweb/map/page.tsx
     /iGEM-dry/viewweb/data/page.tsx
     /iGEM-dry/viewweb/device/page.tsx

4. 当前项目数据文件
   - 优先查找：
     /iGEM-dry/viewweb/app/lib/demoReadings.ts
   - 如果不存在，请搜索：
     demoReadings
     readings
     devices
     mockDevices
     sampleData
     toxin
     sensor

5. 当前项目组件
   - 查找 Navbar、PageHeader、MetricCard、SectionPanel、StatusBadge、RiskBadge、MiniSparkline、FilterBar、DeviceStatus、ToxinPredictionModel、地图组件、设备卡片等。
   - 总结哪些组件可以迁移逻辑。
   - 总结哪些组件需要重写样式。
   - 总结组件之间的关系。

6. 当前项目样式
   - 查找 globals.css、tokens.css、Tailwind 设置、主题变量。
   - 总结可保留的业务样式逻辑（如颜色判定函数）。
   - 根据新蓝图完全废弃原有暗色霓虹风，重新规划浅色青蓝水体实验风设计系统。

━━━━━━━━━━━━━━━━━━━━
四、文档必须包含的核心内容
━━━━━━━━━━━━━━━━━━━━

最终输出的 WEB_REBUILD_SPEC.md 必须包含以下章节。

━━━━━━━━━━━━━━━━━━━━
1. 项目目标摘要
━━━━━━━━━━━━━━━━━━━━

请用清晰中文说明：

- 项目是什么。
- 面向谁使用。
- 为什么要重构。
- 为什么从 Next.js 迁移到 Vite。
- 新网页需要保留哪些核心功能。
- 新网页视觉上要达到什么效果。
- 当前阶段不做哪些事情。

━━━━━━━━━━━━━━━━━━━━
2. 信息来源与优先级
━━━━━━━━━━━━━━━━━━━━

必须列出你读取过的文件和图片，包括：

- PROJECT.md
- 当前项目代码
- 四张设计蓝图
- package.json
- 数据文件
- 组件文件
- 样式文件

请说明信息优先级：

1. 用户当前新增要求。
2. 四张目标设计蓝图。
3. PROJECT.md 中的功能范围和验收标准。
4. 当前项目源代码。
5. 可推断的前端最佳实践。

必须明确说明：
如果 PROJECT.md 和本次重构要求冲突，则功能保留参考 PROJECT.md，技术路线以 React + Vite 为准。

━━━━━━━━━━━━━━━━━━━━
3. 技术路线
━━━━━━━━━━━━━━━━━━━━

这一章必须单独存在，标题必须叫“技术路线”。

必须包含：

1. 目标技术栈表格
   字段包括：
   - 类别
   - 技术
   - 用途
   - 是否必须
   - 备注

示例类别：
- 构建工具
- UI 框架
- 类型系统
- 路由
- 样式
- 图表
- 地图
- 热力图
- 拖拽
- 状态管理
- 数据来源
- 未来 API 层
- 构建与部署

2. Next.js 到 Vite 的迁移说明
   - 旧技术。
   - 新技术。
   - 替换原因。
   - 迁移注意事项。

3. 推荐依赖清单
   - dependencies (必须包含 react, react-dom, react-router-dom, recharts, leaflet, react-leaflet, @dnd-kit/core, @dnd-kit/sortable, lucide-react 等)
   - devDependencies

4. 推荐脚本命令
   - dev
   - build
   - preview
   - lint

5. 推荐项目结构

必须给出类似以下结构：

/iGEM-dry/web
  package.json
  index.html
  vite.config.ts
  tsconfig.json
  src/
    main.tsx
    App.tsx
    router/
      routes.tsx
    layouts/
      AppShell.tsx
      Header.tsx
      Sidebar.tsx
    pages/
      OverviewPage.tsx
      MapMonitorPage.tsx
      DataAnalysisPage.tsx
      DevicePairingPage.tsx
    components/
      common/
      overview/
      map/
      data/
      device/
    data/
      demoReadings.ts
      mockDevices.ts
    services/
      readingsService.ts
      deviceService.ts
    types/
      domain.ts
    utils/
      risk.ts
      format.ts
      chart.ts
    styles/
      tokens.css
      globals.css
      layout.css
    assets/
      assetMap.ts

━━━━━━━━━━━━━━━━━━━━
4. 整体视觉设计系统
━━━━━━━━━━━━━━━━━━━━

请根据四张设计蓝图总结统一视觉风格。

必须包含：

1. 色彩 token 与 Tailwind v4 主题定义
   至少包含以下变量，并显式写出符合 Tailwind CSS v4 规范的 `@theme` CSS 代码块，以供后续 Agent 直接粘贴使用：
   --color-bg
   --color-bg-soft
   --color-surface
   --color-surface-strong
   --color-border
   --color-primary
   --color-primary-strong
   --color-mint
   --color-warning
   --color-danger
   --color-text
   --color-muted

2. 字体规范
   - 页面标题字号。
   - 导航文字字号。
   - 卡片标题字号。
   - 主数据字号。
   - 表格文字字号。
   - 辅助说明文字字号。

3. 间距规范
   - 页面边距。
   - Header 内边距。
   - Sidebar 内边距。
   - 卡片间距。
   - 表格行高。
   - 图表内边距。
   - 图标与文字间距。

4. 圆角规范
   - 页面外框圆角。
   - 卡片圆角。
   - 按钮圆角。
   - Badge 圆角。
   - 输入框圆角。

5. 阴影规范
   - 卡片阴影。
   - 浮层阴影。
   - 按钮 hover 阴影。

6. 边框规范
   - 页面外框。
   - 卡片边框。
   - 表格边框。
   - 图表容器边框。
   - 选中态边框。

7. 状态色规范
   - online。
   - idle。
   - offline。
   - normal。
   - attention。
   - warning。
   - danger。

8. 插画和吉祥物视觉边界溢出规范（还原度核心指标）
   - 插画风格：浅色扁平可爱风，与 Wiki 协调。
   - 出现位置：严格比对蓝图排版。
   - **边界溢出控制规约**：文档必须特别指出，设计图中如右上方、左下方等部分的吉祥物采用了破格、溢出容器边界（Overlap）的视觉特效。承载吉祥物素材组件的父级容器必须显式配置为 `relative overflow-visible`，吉祥物自身使用 `absolute` 定位并设定高层级 `z-index`。严禁误用 `overflow-hidden` 导致吉祥物被切体截断，且必须保障其图层绝不遮挡底层核心监控数据的交互与视线。

━━━━━━━━━━━━━━━━━━━━
5. 全局布局规范
━━━━━━━━━━━━━━━━━━━━

必须详细规定全局结构。

请按桌面端 1536px × 960px 或相近尺寸作为主要设计基准。

必须包含：

1. PageFrame
   - 页面最外层容器名称。
   - 位置。
   - 宽高。
   - 圆角。
   - 边框。
   - 背景。
   - 是否包含水波装饰。

2. Header
   - 组件名称：AppHeader。
   - 位置：页面顶部。
   - 高度范围，例如 96px - 112px。
   - 左侧 Logo 区域宽度。
   - 标题位置。
   - 顶部导航位置。
   - 用户区域位置。
   - 通知按钮位置。
   - 右上角吉祥物占位符位置与尺寸。

3. Sidebar
   - 组件名称：SidebarNav。
   - 位置：左侧。
   - 宽度范围，例如 200px - 220px。
   - 顶部起始位置。
   - 每个导航项尺寸。
   - 导航项间距。
   - 当前激活态样式。
   - 底部装饰占位符位置与尺寸。

4. MainContent
   - 组件名称：MainContent。
   - 左侧与 Sidebar 的关系。
   - 顶部与 Header 的关系。
   - 内容区 padding。
   - 页面最大宽度。
   - 滚动规则。

5. 全局装饰元素
   - Logo 占位符。
   - Header 小吉祥物占位符。
   - Sidebar 大吉祥物占位符。
   - 气泡装饰占位符。
   - 水波装饰占位符。
   - 实验器材装饰占位符。

6. 双导航状态联动机制（硬性设计还原要求）
   - 横向与纵向导航联动：顶部 `AppHeader` 的横向胶囊 Tab 与左侧 `SidebarNav` 的纵向菜单项，必须共享同一个来自 `react-router-dom` 的路由状态。无论用户点击哪一套导航，两边的激活高亮态（浅蓝胶囊背景 vs 左侧边框发光）必须保持绝对同步变色。

每一个占位符必须写清楚：
- 元素名称。
- 推荐文件名。
- 放置路径。
- 页面位置。
- 宽度。
- 高度。
- z-index 建议。
- 是否可点击。
- 缺失时的 fallback 文本。

━━━━━━━━━━━━━━━━━━━━
6. 页面元素级规格总表
━━━━━━━━━━━━━━━━━━━━

标题为“页面元素级规格总表”。为避免 Markdown 单个表格由于字段过多导致模型在输出时省略核心信息，你必须将总表拆分为以下两张相互关联的子表来详细呈现：

### 表 6.1：几何布局与数据源表
字段必须包含：
- 页面名称
- 元素层级
- 推荐组件名
- 推荐代码变量名 / id
- 所属父元素
- 页面位置（描述需具体，如“Header 左侧”、“MainContent 顶部第一行”）
- 与相邻元素关系（如“位于 Logo 右侧 24px”、“列间距 24px”）
- 推荐宽度（尺寸确定，或给出合理范围，严禁使用“按实际情况决定”等模糊表述）
- 推荐高度
- 内边距 (Padding)
- 外边距 (Margin)
- 数据来源（需指明对应旧项目 `demoReadings.ts` 中的具体字段）

### 表 6.2：交互与视觉素材表
字段必须包含：
- 推荐组件名（与表 6.1 一一对应）
- 功能说明
- 交互说明（点击、hover 反馈，是否只做前端模拟）
- 状态说明（不同风险/在线等级下的变色逻辑）
- 是否需要图片/图标
- 视觉素材占位符名称（对应第七章）
- 占位符初始呈现尺寸
- 未来素材存放路径
- 缺失素材时的 Fallback 文本内容

━━━━━━━━━━━━━━━━━━━━
7. 图片与图标占位符总表
━━━━━━━━━━━━━━━━━━━━

必须新增一个章节，标题为“图片与图标占位符总表”。

由于 ./Materials/{对应页面名称} 目前没有任何图片，所以你必须为所有图片和图标规划占位符。

表格字段必须包含：

- 页面
- 占位符名称
- 推荐素材文件名
- 未来素材路径
- 类型
- 用途
- 页面位置
- 所属组件
- 推荐宽度
- 推荐高度
- 是否保持比例
- 是否需要透明背景
- 当前占位符样式
- 缺失素材 fallback 文案
- 备注

类型可包括：
- logo
- mascot
- icon
- device-illustration
- decoration
- chart-icon
- map-marker
- status-icon
- button-icon
- empty-state

请至少规划以下占位符：

通用：
- logo-ocean-placeholder
- header-user-avatar-placeholder
- notification-icon-placeholder
- nav-overview-icon-placeholder
- nav-map-icon-placeholder
- nav-data-icon-placeholder
- nav-device-icon-placeholder
- bubble-decoration-placeholder
- wave-decoration-placeholder

总览页：
- overview-header-mascot-placeholder
- overview-sidebar-mascot-placeholder
- overview-system-shield-icon-placeholder
- overview-online-icon-placeholder
- overview-idle-icon-placeholder
- overview-offline-icon-placeholder
- overview-average-toxin-icon-placeholder
- overview-risk-icon-placeholder
- overview-alert-icon-placeholder

地图监视页：
- map-header-mascot-placeholder
- map-marker-normal-placeholder
- map-marker-attention-placeholder
- map-marker-warning-placeholder
- map-marker-danger-placeholder
- map-selected-device-illustration-placeholder
- map-bottom-mascot-placeholder
- map-layer-icon-placeholder
- map-location-icon-placeholder

数据分析页：
- data-sidebar-microscope-placeholder
- data-trend-warning-icon-placeholder
- data-export-icon-placeholder
- data-confidence-icon-placeholder
- data-prediction-icon-placeholder
- data-wave-decoration-placeholder

设备配对页：
- device-card-buoy-placeholder
- device-card-probe-placeholder
- device-card-offline-placeholder
- device-scan-bluetooth-placeholder
- device-bottom-mascot-placeholder
- device-lab-flask-placeholder
- device-add-icon-placeholder
- device-refresh-icon-placeholder
- device-drag-icon-placeholder
- device-wifi-icon-placeholder
- device-battery-icon-placeholder
- device-signal-icon-placeholder

每个占位符都必须写出尺寸。例如：
- Header Logo：64px × 64px。
- Header 小吉祥物：84px × 84px。
- Sidebar 大吉祥物：160px × 220px。
- 导航图标：24px × 24px。
- 状态卡图标：48px × 48px。
- 设备卡片插画：92px × 92px。
- 地图 marker：36px × 48px。
- 雷达蓝牙图标：72px × 72px。
- 底部实验器材装饰：180px × 160px。

如果无法从图片精确判断尺寸，请根据页面比例给出推荐尺寸 and 范围。

━━━━━━━━━━━━━━━━━━━━
8. 页面 1：总览页详细规格
━━━━━━━━━━━━━━━━━━━━

路由：
/

页面组件名：
OverviewPage

素材目录：
/iGEM-dry/web/Materials/Overview

必须详细写出以下元素：

1. Header 区域
   - Logo
   - 标题
   - 顶部导航
   - 通知按钮
   - 用户胶囊
   - 右上角吉祥物占位符

2. Sidebar 区域
   - 四个导航项
   - 当前页高亮
   - 气泡装饰
   - 大吉祥物占位符
   - 水波装饰

3. 顶部指标卡行
   - 在线设备卡
   - 空闲设备卡
   - 离线设备卡
   - 平均藻毒素卡
   - 最高风险卡

每张指标卡必须规定：
- 卡片名称。
- 组件名。
- 放置位置。
- 宽度。
- 高度。
- 标题位置。
- 数字位置。
- 单位位置。
- 说明文字位置。
- 图标占位符位置与尺寸。
- 风险颜色。
- 数据字段。
- 点击或 hover 交互。

4. 中部内容区
   - SystemStatusPanel。
   - AlertSummaryPanel。
   - OverviewTrendChart。

必须规定这三个面板的相对布局：
- 系统状态面板在左。
- 告警摘要面板在中。
- 趋势概览在右。
- 三者之间的间距。
- 每个面板的宽高。
- 内部元素排列。

5. 底部最新采样表格
   - LatestReadingsTable。
   - 表格列名。
   - 表格行高。
   - 每列宽度比例。
   - 彩色状态圆点尺寸。
   - 数值颜色规则。
   - “查看全部”按钮位置。

6. 总览页所有图片与图标占位符
   - 必须逐一列出。
   - 每个占位符都必须有大小。
   - 占位符必须参与排版。
   - 不允许真实图片缺失时导致布局塌陷。

━━━━━━━━━━━━━━━━━━━━
9. 页面 2：地图监视页详细规格
━━━━━━━━━━━━━━━━━━━━

路由：
/map

页面组件名：
MapMonitorPage

素材目录：
/iGEM-dry/web/Materials/Map

必须详细写出以下元素：

1. Header 与 Sidebar
   - 沿用全局规范。
   - 当前激活项为“地图监视”。

2. 主地图面板 LakeRiskMap
   - 位置。
   - 宽度。
   - 高度。
   - 圆角。
   - 地图底图区域。
   - 地图控件。
   - 缩放按钮。
   - 定位按钮。
   - 图层切换按钮。
   - 热力图层。
   - 设备点位。
   - 选中设备点位。
   - 风险图例。

3. 地图 marker 占位符
   - normal marker。
   - attention marker。
   - warning marker。
   - danger marker。
   - selected marker。
   - 每种 marker 的尺寸。
   - 每种 marker 的颜色。
   - 每种 marker 的交互状态。

4. 右侧设备详情面板 SelectedDevicePanel
   - 位置。
   - 宽度。
   - 高度。
   - 标题区。
   - 风险状态。
   - 在线状态。
   - 藻毒素浓度卡。
   - 更新时间。
   - 电量卡。
   - 信号强度卡。
   - 水温卡。
   - pH 卡。
   - 位置 / 设备类型 / 备注区域。
   - 查看历史数据按钮。
   - 底部设备或吉祥物占位符。

5. 风险图例 RiskLegend
   - 位置：地图底部浮层。
   - 宽度。
   - 高度。
   - 每个图例项的圆点大小。
   - 每个图例项的文字。
   - 每个图例项之间的间距。

6. 地图页交互与架构防御（硬性要求说明）
   - 点击设备点位更新右侧详情。
   - 热力图层开关。
   - 设备图层开关。
   - 查看历史数据跳转或打开数据页。
   - 地图加载失败 fallback。
   - 无设备数据 fallback。
   - **单页应用(SPA)防御规约**：文档中必须着重强调，使用 `react-leaflet` 渲染插值热力图时，热力图数据必须利用 `useMemo` 缓存；在生命周期结束或重新挂载时，必须在 React 清理函数中显式执行 `map.removeLayer`，防止后续 Agent 编写组件时由于单页路由频繁切换导致地图重叠、重复渲染或 Canvas 内存泄漏。

━━━━━━━━━━━━━━━━━━━━
10. 页面 3：数据分析页详细规格
━━━━━━━━━━━━━━━━━━━━

路由：
/data

页面组件名：
DataAnalysisPage

素材目录：
/iGEM-dry/web/Materials/Data

必须详细写出以下元素：

1. 顶部筛选栏 DataFilterBar
   - 位置。
   - 高度。
   - 时间范围选择器。
   - 设备筛选器。
   - 传感器筛选器。
   - 导出数据按钮。
   - 每个控件宽度。
   - 控件之间的间距。
   - 图标占位符大小。
   - 交互说明。

2. 趋势分析面板 MultiMetricTrendChart
   - 位置。
   - 宽度。
   - 高度。
   - 标题位置。
   - 图例位置。
   - **三 Y 轴独立刻度映射系统（图表还原硬性指标）**：必须显式配置 Recharts 的三个具有不同 `yAxisId` 的 `<YAxis />` 组件。左轴对应藻毒素刻度范围（0 - 5 µg/L），右轴内侧对应水温范围（18 - 30 ℃），右轴外侧独立悬空对应 pH 轴线刻度（6.0 - 8.5）。每条折线必须严丝合缝地绑定到自己的 `yAxisId`，并在其折线峰值超过安全阈值的特殊数据点位上，绑定定制化的红色三角形告警 Marker（▲）。
   - **Recharts 高度塌陷防御规约**：文档必须特别命令 Agent，图表的父级包裹容器必须显式声明固定的物理高度（或通过 Tailwind 网格/比例锁定 `h-[380px]` 等明确范围）和 `relative` 定位。严禁直接将 `<ResponsiveContainer>` 置于不确定高度的弹性 flex/grid 容器中，以防图表高度塌陷至 0px 或无限制无限纵向伸展。
   - 藻毒素折线、水温折线、pH 折线、高风险阈值线、警戒阈值线、异常点图标占位符、tooltip、空状态。

3. 传感器对比面板 SensorComparisonPanel
   - 位置：趋势分析图右侧。
   - 宽度。
   - 高度。
   - 每个设备对比项高度。
   - 彩色圆点尺寸。
   - 数值位置。
   - 单位位置。
   - 排序规则。
   - 风险颜色规则。

4. AI 预测模块 ToxinPredictionPanel
   - 位置：页面下半部分。
   - 主预测图（使用 Recharts 的 AreaChart 实现）。
   - 历史数据线（实线）。
   - 预测数据线（虚线）。
   - 95% 置信区间（半透明 Area 阴影覆盖）。
   - 右侧模型置信度卡。
   - 预测区间卡。
   - 下一高风险时间卡。
   - 图例。
   - 时间范围下拉。
   - 占位符图标。

5. 数据分析页装饰占位符
   - 左下角显微镜或实验器材。
   - 气泡。
   - 水波。
   - 图表警告图标。
   - 导出图标。
   - 每个都必须有尺寸和位置。

━━━━━━━━━━━━━━━━━━━━
11. 页面 4：设备配对页详细规格
━━━━━━━━━━━━━━━━━━━━

路由：
/device

页面组件名：
DevicePairingPage

素材目录：
/iGEM-dry/web/Materials/Drive

必须详细写出以下元素：

1. 顶部操作栏 DeviceToolbar
   - 添加设备按钮。
   - 刷新列表按钮。
   - 批量操作按钮。
   - 每个按钮宽高。
   - 图标占位符尺寸。
   - 按钮间距。
   - 交互状态。

2. 设备卡片网格 DeviceCardGrid
   - 位置。
   - 列数。
   - 行间距。
   - 列间距。
   - 单张卡片宽度。
   - 单张卡片高度。
   - 选中态边框。
   - 拖拽态样式。

3. 单张设备卡片 DeviceCard
   - **设备插画动态条件渲染规约**：必须根据 `MonitoringDevice` 数据结构中的 `type` 字段，动态条件渲染不同的图片占位符。例如：`type === 'buoy'` 渲染 `device-card-buoy-placeholder`（水面浮标模型），`type === 'probe'` 渲染 `device-card-probe-placeholder`（管状探针模型）。严禁全量渲染单一重复素材，以确保视觉还原度。
   - 设备名称、状态圆点、状态文本、WiFi / 蓝牙图标、电量图标、电量百分比、分割线、藻毒素指标、水温指标、pH 指标。
   - 卡片右上角选中勾。
   - 每个元素的位置、大小、间距。
   - 每个指标的数据字段。
   - 高风险、待机、离线状态样式。

4. 拖拽排序提示区 DeviceSortDropZone
   - 位置。
   - 宽度。
   - 高度。
   - 虚线边框。
   - 图标占位符。
   - 文案。
   - 与设备卡片网格之间的距离。

5. 右侧添加新设备 / 扫描面板 PairingPanel
   - 位置。
   - 宽度。
   - 高度。
   - 标题。
   - 扫描附近设备文字。
   - **雷达无线扫描组件几何布局（硬性视觉层级要求）**：雷达扫描区域（RadarScanner）必须由纯 Tailwind 样式构建，使用绝对定位（`absolute`）和宽高居中。需通过 3 层 `border-dashed` 且带有淡蓝半透明环境光的圆环进行等间距等比堆叠嵌套，并在几何圆心正中央放置独立的蓝牙状态占位符（尺寸 72px × 72px）。
   - 发现设备列表、每个发现设备项高度、RSSI 信息、蓝牙配对按钮、WiFi 连接按钮、底部吉祥物 / 实验器材占位符。
   - 每个占位符尺寸和位置。

6. 设备页交互
   - 添加设备。
   - 编辑设备。
   - 删除设备。
   - 详情查看。
   - 刷新列表。
   - 批量操作。
   - 拖拽排序。
   - 扫描设备。
   - 蓝牙配对。
   - WiFi 连接。
   - 断开连接。
   - 所有交互当前只修改前端本地 state。

━━━━━━━━━━━━━━━━━━━━
12. 数据模型与字段规范
━━━━━━━━━━━━━━━━━━━━

请根据当前项目和页面需求定义 TypeScript 类型。你必须明确：新项目应当直接继承、完整平移旧项目数据文件中的核心静态数据与判定计算工具函数（如原 `getRiskLevel`、`getRiskColor`、`getSignalLabel` 等），新页面组件需直接调用这些统一工具函数，严禁在组件内部重复进行魔法数字或颜色硬编码。

必须包含：

1. DeviceStatus
   - online
   - idle
   - offline

2. RiskLevel
   - normal
   - attention
   - warning
   - danger

3. MonitoringDevice
   字段至少包含：
   - id
   - name
   - type
   - locationName
   - latitude
   - longitude
   - status
   - connectionType
   - battery
   - signalDbm
   - lastUpdated
   - note

4. DeviceReading
   字段至少包含：
   - id
   - deviceId
   - deviceName
   - sampledAt
   - toxin
   - waterTemp
   - ph
   - battery
   - signalDbm
   - status
   - locationName
   - latitude
   - longitude

5. AlertSummary

6. TrendPoint

7. PredictionPoint

8. DiscoveredDevice

9. FilterState

10. DeviceAction

每个类型都要写：
- 字段名。
- 类型。
- 含义。
- 示例值。
- 是否必填。
- 对应页面用途。

━━━━━━━━━━━━━━━━━━━━
13. 风险规则与状态规则
━━━━━━━━━━━━━━━━━━━━

必须写清楚：

1. 藻毒素浓度风险分级
   - normal: < 0.5 µg/L
   - attention: 0.5 - 1.0 µg/L
   - warning: 1.0 - 5.0 µg/L
   - danger: > 5.0 µg/L

2. 状态映射
   - online：绿色，显示“在线”。
   - idle：橙色，显示“待机”或“空闲”。
   - offline：灰色或红色，显示“离线”。

3. 数值颜色
   - 高风险藻毒素：红色。
   - 警戒：橙色。
   - 关注：黄色或橙黄。
   - 正常：绿色。
   - 平均值和主强调：蓝色。

4. 表格状态圆点
   - 直径。
   - 颜色。
   - 与文字间距。

5. Badge 规范
   - 尺寸。
   - 背景色。
   - 文字颜色。
   - 圆角。

━━━━━━━━━━━━━━━━━━━━
14. 交互流程
━━━━━━━━━━━━━━━━━━━━

请用流程列表说明每个交互。

必须包含：

1. 导航切换。
2. 总览页查看全部。
3. 总览页点击告警摘要。
4. 地图页点击设备点。
5. 地图页切换热力图。
6. 地图页切换设备图层。
7. 地图页查看历史数据。
8. 数据分析页筛选时间范围。
9. 数据分析页筛选设备。
10. 数据分析页筛选传感器。
11. 数据分析页导出数据。
12. 设备页添加设备。
13. 设备页编辑设备。
14. 设备页删除设备。
15. 设备页拖拽排序。
16. 设备页扫描附近设备。
17. 设备页蓝牙配对。
18. 设备页 WiFi 连接。
19. 设备页断开连接。
20. 加载态、空状态、错误态。

每个交互都需要写：
- 触发元素。
- 触发条件。
- 状态变化。
- UI 反馈。
- 涉及的数据。
- 当前阶段是否只做前端模拟。

━━━━━━━━━━━━━━━━━━━━
15. 组件拆分方案
━━━━━━━━━━━━━━━━━━━━

必须给出完整组件拆分。

每个组件都要写：

- 组件名。
- 文件路径。
- 所属页面。
- 功能。
- props。
- state。
- 是否可复用。
- 是否依赖数据。
- 是否依赖图片占位符。
- 子组件。
- 父组件。

至少包含：

common:
- AquaPanel
- AquaCard
- IconPlaceholder
- ImagePlaceholder
- StatusBadge
- RiskBadge
- EmptyAssetSlot
- AppButton
- AppSelect

layout:
- AppShell
- AppHeader
- SidebarNav
- PageFrame

overview:
- MetricSummaryCard
- SystemStatusPanel
- AlertSummaryPanel
- OverviewTrendChart
- LatestReadingsTable

map:
- LakeRiskMap
- RiskLegend
- SelectedDevicePanel
- MapLayerToggle
- MapMarkerPlaceholder

data:
- DataFilterBar
- MultiMetricTrendChart
- SensorComparisonPanel
- ToxinPredictionPanel

device:
- DeviceToolbar
- DeviceCardGrid
- DeviceCard
- DeviceSortDropZone
- PairingPanel
- DeviceFormModal
- DiscoveredDeviceItem

━━━━━━━━━━━━━━━━━━━━
16. 素材占位符实现规范
━━━━━━━━━━━━━━━━━━━━

由于 Materials 目录为空，必须规定如何实现占位符。

请在文档中要求：

1. 所有图片和图标先用占位符组件显示。
2. 占位符组件名称：
   - ImagePlaceholder
   - IconPlaceholder
   - EmptyAssetSlot
3. 占位符必须拥有固定宽高。
4. 占位符不能因为真实图片缺失而改变页面布局。
5. 占位符内部显示：
   - 素材名称。
   - 推荐文件名。
   - 推荐尺寸。
6. 占位符外观：
   - 浅蓝半透明背景。
   - 虚线边框。
   - 圆角。
   - 居中文字。
   - 可选小图标。
7. 未来真实图片放入 Materials 后，只需要替换 assetMap 即可。
8. 图片加载失败时继续显示占位符。
9. 不允许代码直接假设图片一定存在。

请提供建议 assetMap 结构，例如：

```typescript
const assetMap = {
  common: {
    logoOcean: "/Materials/General/logo-ocean.png",
    navOverviewIcon: "/Materials/General/nav-overview-icon.png"
  },
  overview: {
    headerMascot: "/Materials/Overview/mascot-overview-corner.png"
  }
}
```

但要说明：当前文件不存在时必须 fallback 到占位符。

━━━━━━━━━━━━━━━━━━━━ 

17. Vite 重构迁移步骤 

    ━━━━━━━━━━━━━━━━━━━━

请写出详细迁移步骤：

1. 审计旧项目。
2. 初始化 Vite React TypeScript 项目（选用 React 18 稳定版本）。
3. 安装依赖（使用 `--legacy-peer-deps` 确保低版本图表组件稳定兼容）。
4. 建立 src 目录结构。
5. 迁移并对齐旧项目 `demoReadings.ts` 的 mock data 数据与算法逻辑。
6. 迁移类型定义。
7. 建立风险计算工具函数。
8. 建立全局样式 token（在全局 globals.css 中建立符合 Tailwind v4 的 `@theme` 变量层）。
9. 建立 AppShell。
10. 建立 Header 和 Sidebar。
11. 建立 react-router-dom 路由。
12. 实现总览页。
13. 实现地图页（注意 React Leaflet 的图层状态生命周期清理）。
14. 实现数据分析页（引入双轴折线与 Area 置信区间）。
15. 实现设备配对页。
16. 替换 Next.js 专属代码。
17. **处理 Leaflet 样式和默认 Marker 路径崩溃 Bug（硬性代码安全要求）**：文档必须强力命令 Agent 解决 Leaflet 的默认标记图标在 Vite 静态资源编译散列化（Asset Hashing）后的路径丢失问题。必须在新项目的地图模块初始化代码中显式调用 `L.Icon.Default.mergeOptions` 并显式导入本地或静态占位符图标图源，或统一自定义全量 Marker 的 `L.icon` 结构，彻底断绝地图 Marker 加载出 404 碎片报错的问题。
18. 实现图片占位符系统。
19. 实现 mock service 层。
20. 进行构建和验收。

每一步都要写：

- 目标。
- 涉及文件。
- 注意事项。
- 验收方式。

━━━━━━━━━━━━━━━━━━━━ 

18. 验收标准 

    ━━━━━━━━━━━━━━━━━━━━

必须包含：

1. 技术验收
   - npm install 成功。
   - npm run dev 成功。
   - npm run build 成功。
   - npm run preview 成功。
   - 无 TypeScript 关键错误。
   - 无明显控制台运行错误。
2. 页面验收
   - / 正常显示总览页。
   - /map 正常显示地图监视页。
   - /data 正常显示数据分析页。
   - /device 正常显示设备配对页。
3. 视觉验收
   - 四页整体接近设计蓝图。
   - 使用浅色青蓝水体实验风。
   - Header、Sidebar、MainContent 一致。
   - 卡片、按钮、图表、表格风格统一。
   - 所有图片和图标即使缺失，也有正确尺寸的占位符。
   - 页面不会因为 Materials 为空而错位或报错。
4. 功能验收
   - 总览页指标、告警、趋势、最新采样表格可见。
   - 地图页设备点位、热力图、图例、右侧详情可见。
   - 数据分析页筛选栏、趋势图、传感器对比、AI 预测可见。
   - 设备页设备卡片、拖拽排序、扫描面板、配对按钮可见。
   - 所有交互至少有前端模拟反馈。
5. 响应式验收
   - 桌面端 1280px - 1600px 效果最佳。
   - 小屏幕下内容纵向堆叠。
   - 不出现严重水平溢出。
   - 关键数据不被装饰图遮挡。

━━━━━━━━━━━━━━━━━━━━ 

19. 缺失信息与待确认问题 

    ━━━━━━━━━━━━━━━━━━━━

如果无法确认某些内容，请在本章列出。

每一项必须包含：

- 问题。
- 当前无法确认的原因。
- 建议默认方案。
- 是否阻塞重构。

不要编造无法确认的信息。

━━━━━━━━━━━━━━━━━━━━ 

五、输出要求 

━━━━━━━━━━━━━━━━━━━━

1. 最终只输出 Markdown 文档： /iGEM-dry/web/WEB_REBUILD_SPEC.md
2. 文档必须使用中文。
3. 文档必须足够详细，让后续 Agent 可以直接据此编码。
4. 必须包含“技术路线”章节。
5. 必须包含拆分后的“几何布局与数据源表”与“交互与视觉素材表”。
6. 必须包含“图片与图标占位符总表”。
7. 必须对每个页面的所有元素在规格双表中描述清楚：名称、组件名、位置、相邻元素关系、宽高、内外边距、数据源、功能、交互、状态、占位符尺寸和未来路径。
8. 对所有图片和图标，必须先使用占位符标注。
   - 占位符不能只是文字说明。
   - 占位符要作为真实页面元素参与排版。
   - 占位符大小必须与最终元素规定大小一致。
   - ./Materials/{对应页面名称} 为空时，页面仍必须完整显示。
9. 不要使用“参考设计图自行调整”“按实际情况决定”“大概放这里”等模糊表述。
10. 如果尺寸无法精确判断，请根据设计图比例给出合理的推荐范围与尺寸数值（如：卡片圆角 16px-24px，图标 24px×24px，大吉祥物高 160px-220px）。
11. 不要实现完整网页代码。
12. 不要接真实后端。
13. 不要依赖真实图片存在。
14. 不要省略四个页面中的任何主要元素。
15. 请现在开始读取路径、分析项目和蓝图，并生成完整的 /iGEM-dry/web/WEB_REBUILD_SPEC.md。