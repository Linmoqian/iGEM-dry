# Role & Core Objective
You are an elite, pixel-perfect UI/UX Front-End Structural Engineer AI. Your absolute goal is to reverse-engineer the provided device pairing interface design (`设备配对页目标.png`) into a high-fidelity, production-ready `.pen` file using the **Pencil Design Plugin**.

You must interpret the image with strict mathematical and geometric precision. Replicate exact padding, alignment, font weights, color hex codes, layout grids, and border radii without introducing any arbitrary variations.

---

## 1. Global Layout Engine & Design Tokens

### 📐 Structural Grid & Dimensions (Based on 1920x1080 Viewport)
* **Canvas Boundary:** `width: 1920px; height: 1080px; box-sizing: border-box;`
* **Global Layout Scheme:**
    * **Sidebar Width:** `240px` (Fixed left layout)
    * **Top Nav Height:** `80px` (Fixed top layout, spans across `width: 1680px`)
    * **Main Workspace Content Grid:** `width: 1640px; margin: 20px; display: flex; flex-direction: row; gap: 20px;`
        * **Left Workspace Panel (Device Management Grid):** `flex: 1; display: flex; flex-direction: column; gap: 16px;`
        * **Right Workspace Panel (Scan & Pairing Inspector):** `width: 420px; fixed right;`

### 🎨 Precise Color & Asset Tokens
```css
:root {
  /* Backgrounds */
  --global-bg: linear-gradient(180deg, #F4F8FC 0%, #E6F0FA 100%);
  --panel-bg: #FFFFFF;
  --card-bg: #FFFFFF;
  
  /* Brand & Active States */
  --primary-blue: #0084FF;
  --active-tab-bg: #E6F0FA;
  --active-tab-text: #1A73E8;
  --active-pill-bg: #E0F2FE;
  --active-pill-text: #0284C7;
  
  /* Device Status States */
  --status-online: #22C55E;    /* Green */
  --status-idle: #FF7A00;      /* Orange */
  --status-offline: #64748B;   /* Gray */
  --status-danger: #EF4444;    /* Red (For high toxin flags) */
  
  /* Borders & Radar */
  --border-color: #E2E8F0;
  --card-border-active: #3B82F6;
  --radar-ring: rgba(0, 132, 255, 0.1);
  --dropzone-dash: #93C5FD;

  /* Typography */
  --text-primary: #0F172A;
  --text-secondary: #475569;
  --text-muted: #64748B;
}
```

## 2. Component Node Tree & CSS Blueprint (Pixel-Perfect Specs)

### [Node 1] Top Navigation Bar & Left Sidebar

- **Active State Update:** The active highlighted tab must switch to **`设备配对` (Device Pairing)**.
  - Style: Background fill (`var(--active-pill-bg)`), text/icon color (`var(--active-pill-text)`), matching standard nav item block border-radius.

### [Node 2] Left Workspace Panel (Paired Devices Interface)

#### Sub-Node 2A: Top Action Button Row

- `display: flex; gap: 12px; margin-bottom: 4px;`
- **Button 1 (`添加设备`):** `background: var(--primary-blue); color: #FFF; font-weight: bold; border-radius: 8px; padding: 10px 20px; display: flex; align-items: center; gap: 6px;` (Incorporate clear `+` vector sign)
- **Button 2 (`刷新列表`):** `background: #FFF; border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 8px; padding: 10px 20px; display: flex; align-items: center; gap: 6px;`
- **Button 3 (`批量操作`):** `background: #FFF; border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 8px; padding: 10px 20px; display: flex; align-items: center; gap: 4px;` (Includes a right-aligned down arrow)

#### Sub-Node 2B: 3x2 Core Device Cards Matrix

- `display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;`
- **Card Node Properties:** `background: var(--card-bg); border-radius: 12px; border: 1px solid var(--border-color); padding: 16px; position: relative;`
  - *Active Selection Rule:* Cards 3, 5, and 6 show a soft blue highlight border (`border: 1px solid var(--card-border-active);`) and a cyan checkmark badge (`✓`) floating exactly at the top-right corner.
- **Internal Card Layout Structure:**
  - **Top Split Row:**
    - *Left block:* Contains custom stylized transparent vector illustrations of the physical monitoring hardware (e.g., buoys, probes).
    - *Right block (`display: flex; flex-direction: column; gap: 6px;`):*
      - Title text: Device Name (`font-size: 16px; font-weight: bold; color: var(--text-primary);`)
      - Status indicator line: Mini dot (`●`) + state text (`在线`, `待机`, or `离线`) following standard status color tokens.
      - Peripheral hardware icons line: Mini Green/Gray Wi-Fi wave vector + Battery gauge container displaying text payload (e.g., `86%`, `63%`, `--`).
  - **Bottom Row Metrics Grid (`display: flex; justify-content: space-between; margin-top: 16px; border-top: 1px dashed #F1F5F9; padding-top: 12px;`):**
    - Splits into 3 data columns: `藻毒素` | `水温` | `pH`
    - Labels use `color: var(--text-muted); font-size: 12px;`.
    - Values use `font-size: 16px; font-weight: bold; margin-top: 4px;`.
- **Specific Card Payloads:**
  1. **藻华预警浮标-06:** 在线 | 🔋 86% | 藻毒素: `6.35 µg/L` (Red: `var(--status-danger)`) | 水温: `24.8 ℃` | pH: `7.4`
  2. **入水口探针-02:** 在线 | 🔋 63% | 藻毒素: `1.36 µg/L` (Green: `var(--status-online)`) | 水温: `25.5 ℃` | pH: `7.1`
  3. **岸线巡检猫-03 (Selected):** 待机 | 🔋 38% | 藻毒素: `0.78 µg/L` (Green) | 水温: `26.1 ℃` | pH: `7.6`
  4. **湖心浮标-01:** 在线 | 🔋 86% | 藻毒素: `0.42 µg/L` (Green) | 水温: `24.8 ℃` | pH: `7.4`
  5. **撞水口监测-04 (Selected):** 在线 | 🔋 55% | 藻毒素: `1.05 µg/L` (Green) | 水温: `25.0 ℃` | pH: `7.2`
  6. **老旧探针-05 (Selected):** 离线 | 🔋 -- | 藻毒素: `-- µg/L` (Muted) | 水温: `-- ℃` | pH: `--`

#### Sub-Node 2C: Bottom Interactive Reorder Zone

- `width: 100%; height: 72px; border: 2px dashed var(--dropzone-dash); background: rgba(0, 132, 255, 0.01); border-radius: 12px; display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 8px;`
- Content Text: "🎛️ 拖拽设备卡片可调整顺序" (`color: var(--text-secondary); font-size: 14px; font-weight: 500;`)

### [Node 3] Right Workspace Panel (Add New Device & Radar Scan)

- **Geometry:** `background: var(--panel-bg); border-radius: 16px; border: 1px solid var(--border-color); padding: 24px; display: flex; flex-direction: column; justify-content: space-between;`
- **Layer 3-1: Headers Block**
  - Title: "添加新设备" (`font-size: 18px; font-weight: bold; color: var(--text-primary);`)
  - Subtitle: "扫描附近设备" (`font-size: 14px; color: var(--text-secondary); margin-top: 8px;`)
- **Layer 3-2: Radar Graphic Visualization Center**
  - Centered container layout. Replicate 4 concentric structural thin vector rings (`stroke: var(--radar-ring); fill: none;`).
  - Exact Center Target: Deep vibrant blue circular button badge carrying a clean white Bluetooth icon (`⚡`) glowing with a outer concentric dropping shadow radius effect.
- **Layer 3-3: Discovered Items Section**
  - Section Title: "已发现设备 (2)" (`font-size: 14px; font-weight: 600; color: var(--text-primary); margin: 16px 0 12px 0;`)
  - **List Element 1:** `border: 1px solid var(--border-color); border-radius: 10px; padding: 12px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;`
    - Left Label Details: `WaterProbe-7F2A` (`font-size: 14px; font-weight: bold;`) over subtext `RSSI -48 dBm` (`font-size: 12px; color: var(--text-muted);`).
    - Right Action Button (`蓝牙配对`): `background: var(--primary-blue); color: #FFF; border-radius: 6px; padding: 6px 14px; font-size: 12px; font-weight: bold; border: none;`
  - **List Element 2:** `border: 1px solid var(--border-color); border-radius: 10px; padding: 12px; display: flex; justify-content: space-between; align-items: center;`
    - Left Label Details: `Buoy-3C91` (`font-size: 14px; font-weight: bold;`) over subtext `RSSI -62 dBm` (`font-size: 12px; color: var(--text-muted);`).
    - Right Action Button (`WiFi连接`): `background: #FFF; border: 1px solid var(--primary-blue); color: var(--primary-blue); border-radius: 6px; padding: 6px 14px; font-size: 12px; font-weight: bold;`

## 3. Pencil Design Plugin Compilation Constraints

1. **Isolation of Decorative Elements:** * The large vector seaweed illustration at the bottom-left corner of the workspace must be isolated as an absolute-positioned overlay node layer group labeled `[Overlay_Decoration_Seaweed]`.
   - The lower right-hand chibi anime character holding chemical tubes beside a laboratory flask setup must be assigned to its standalone layer node group labeled `[Overlay_Mascot_LabResearcher]`.
2. **Explicit Matrix Alignment:** Ensure the device list uses precise grid alignment matching standard flex parameters to preserve perfectly structured column rows across different render targets.
3. **Strict Icon Splitting:** Ensure all vector elements like battery shapes, wireless signals, and arrow dropdown tags remain as discrete path outlines, avoiding compilation into monolithic flattened text glyph layers.

Generate the final highly accurate `.pen` structured definition output parsing these rules step by step.