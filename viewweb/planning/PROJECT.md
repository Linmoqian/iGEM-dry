# iGEM 实验室物联网监视系统

## What This Is

面向 iGEM 干实验团队的实验室传感器监控前端。通过暗色科技风 Web 界面，实时查看实验室传感器的运行状态、地理位置分布和历史数据分析。前端使用模拟数据驱动，后期对接真实硬件后端。

## Core Value

设备管理——能添加、删除、配置传感器，管理连接，实时查看状态。设备管好了，监控和数据分析才有意义。

## Requirements

### Validated

<!-- 现有代码已实现的能力 -->

- ✓ 暗色科技风 UI 主题 — 现有代码已实现（深海蓝黑背景、cyan neon 风格）
- ✓ 导航栏路由切换 — 现有 Navbar 组件支持 4 页导航
- ✓ 设备卡片展示 — DeviceStatus 组件支持三态显示（online/idle/offline）
- ✓ 设备卡片拖拽排序 — @dnd-kit 实现拖拽重排
- ✓ 模拟设备数据 — device 页面有 3 个模拟设备

### Active

<!-- 当前要构建的范围 -->

- [ ] 设备 CRUD（添加/编辑/删除传感器，配置名称、位置、类型）
- [ ] 连接管理（蓝牙/WiFi 扫描、配对、断开模拟）
- [ ] 设备状态实时监控（在线/空闲/离线、电量、温度）
- [ ] 总览页设备统计（在线/空闲/离线数量汇总）
- [ ] 总览页告警摘要（异常事件列表）
- [ ] 总览页快速趋势图（核心指标缩略折线图）
- [ ] 地理地图页（真实地图，标记设备位置，点击查看详情）
- [ ] 数据分析页趋势折线图（温度/湿度等指标随时间变化）
- [ ] 数据分析页传感器对比（不同传感器同一时间对比）
- [ ] 数据分析页异常标注（超出阈值标记异常点）
- [ ] 数据分析页筛选过滤（按传感器类型/时间范围）

### Out of Scope

- 真实后端 API 对接 — 后期再接，当前纯前端 + 模拟数据
- 用户认证/登录 — 单人使用场景，不需要多用户
- 数据持久化 — 模拟数据跑在内存，刷新重置
- 移动端适配 — Web 优先，不做响应式移动端
- 暗色模式切换 — 整个应用就是暗色主题
- 实时推送/WebSocket — 后期对接真实硬件时再考虑
- 告警通知（邮件/短信）— 纯前端展示告警即可

## Context

- iGEM 竞赛项目，干实验（dry lab）团队的监控前端
- 技术栈已确定：Next.js 16 + React 19 + TypeScript + Tailwind CSS v4
- 前端骨架已搭建（4 页路由、导航栏、设备卡片组件、暗色科技风主题）
- 地图页和数据分析页目前是占位状态
- 使用 @dnd-kit 实现设备卡片拖拽排序
- 设计参考图在 `designe-figure/` 目录

## Constraints

- **Tech Stack**: Next.js 16 App Router — 有破坏性变更，需参考 `node_modules/next/dist/docs/`
- **Data**: 纯模拟数据 — 不依赖任何后端 API
- **Scope**: 前端先行 — 所有功能都在浏览器端完成
- **Design**: 暗色科技风 — 保持现有 cyan/blue/indigo 视觉语言一致
- **Tailwind**: v4 — 使用 `@import "tailwindcss"` 语法，无 tailwind.config.js

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 模拟数据先行 | 真实硬件尚未就绪，先做好前端体验 | — Pending |
| 前端先行，后期待接 | iGEM 时间线压力，先交付可用前端 | — Pending |
| 设备管理优先 | 没有设备管理，其他页面没有数据源 | — Pending |
| 真实地理地图 | 设备有物理位置，需要地图可视化 | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-14 after initialization*
