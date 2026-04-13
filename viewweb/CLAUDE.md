# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- `npm run dev` — 启动开发服务器（端口 3000）
- `npm run build` — 生产构建
- `npm run lint` — ESLint 检查
- 不用启动开发服务器验证效果

## Tech Stack

- Next.js 16 (App Router) + React 19 + TypeScript
- Tailwind CSS v4（`@import "tailwindcss"` 语法，通过 CSS 配置，非 tailwind.config.js）
- 字体：Geist / Geist Mono（通过 `next/font/google` 加载）
- 路径别名：`@/*` → 项目根目录

## Architecture

### 关键约束

**Next.js 16 有破坏性变更。** 编写代码前必须先阅读 `node_modules/next/dist/docs/` 中对应文档，API 和约定可能与训练数据不同。

### 页面路由

共享导航栏的 4 页应用，`Navbar` 组件在根 `layout.tsx` 中渲染：

| 路由 | 页面 | 说明 |
|------|------|------|
| `/` | `app/page.tsx` | 总览 |
| `/map` | `app/map/page.tsx` | 地图监视 |
| `/data` | `app/data/page.tsx` | 数据分析 |
| `/device` | `app/device/page.tsx` | 设备配对 |

### 组件

- `Navbar` — 客户端组件（`'use client'`），`usePathname` 检测路由，激活项椭圆黑底白字，非激活项圆形白底黑字，CSS transition 变形动画
- `DeviceStatus` — 服务端组件，接收 `deviceName/status/location/battery/temperature` props，三态颜色指示（online=绿, idle=琥珀, offline=红）

### 样式约定

- 整体风格：毛玻璃（`backdrop-blur`）+ 圆角卡片（`rounded-2xl`）+ 浅阴影
- 背景色 `bg-stone-50`，卡片 `bg-white/80`
- 无暗色模式适配（globals.css 有 dark 变量但组件未使用）
- Tailwind v4 通过 `@theme inline` 在 `globals.css` 注册 CSS 变量，无 `tailwind.config.js`

### 设计资源

`designe-figure/` 目录包含 UI 设计参考图，开发前应参考对应图片。
