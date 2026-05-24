# Role & Core Objective
You are an elite, pixel-perfect UI/UX Front-End Structural Engineer AI. Your absolute goal is to reverse-engineer the provided data analysis interface design (`数据分析页目标.png`) into a high-fidelity, production-ready `.pen` file using the **Pencil Design Plugin**.

You must interpret the image with strict mathematical and geometric precision. Replicate exact padding, alignment, font weights, color hex codes, chart structures, and border radii without introducing any arbitrary changes.

---

## 1. Global Layout Engine & Design Tokens

### 📐 Structural Grid & Dimensions (Based on 1920x1080 Viewport)
* **Canvas Boundary:** `width: 1920px; height: 1080px; box-sizing: border-box;`
* **Global Layout Scheme:**
    * **Sidebar Width:** `240px` (Fixed left layout)
    * **Top Nav Height:** `80px` (Fixed top layout, spans across `width: 1680px`)
    * **Main Workspace Content Grid:** `width: 1640px; margin: 20px; display: flex; flex-direction: column; gap: 20px;`
        * **Top Content Row (Trend + Comparison):** `height: 440px; display: flex; flex-direction: row; gap: 20px;`
        * **Bottom Content Row (AI Prediction + Metrics):** `height: 460px; display: flex; flex-direction: row; gap: 20px;`

### 🎨 Precise Color & Asset Tokens
```css
:root {
  /* Backgrounds */
  --global-bg: linear-gradient(180deg, #F4F8FC 0%, #E6F0FA 100%);
  --panel-bg: #FFFFFF;
  --header-bg: #F8FAFC;
  
  /* Brand & Active States */
  --primary-blue: #1A73E8;
  --active-tab-bg: #E6F0FA;
  --active-tab-text: #1A73E8;
  
  /* Chart Line & Status Palette */
  --chart-toxin-blue: #1A73E8;
  --chart-temp-green: #10B981;
  --chart-ph-purple: #8B5CF6;
  
  --status-danger: #EF4444;      /* Red */
  --status-warning: #FF7A00;     /* Orange */
  --status-normal: #22C55E;      /* Green */
  --status-info: #06B6D4;        /* Cyan/Teal */
  
  /* Threshold Lines */
  --threshold-high: #EF4444;
  --threshold-alert: #FF7A00;

  /* Typography */
  --text-primary: #0F172A;
  --text-secondary: #475569;
  --text-muted: #64748B;
  --border-color: #E2E8F0;
}
```

## 2. Component Node Tree & CSS Blueprint (Pixel-Perfect Specs)

### [Node 1] Top Navigation Bar (Filters & Tools)

- **Geometry:** `height: 80px; padding: 0 32px; display: flex; align-items: center; border-bottom: 1px solid var(--border-color); background: #FFF;`
- **Layout Blocks:**
  - **Left Brand Area:** Title text "水体藻毒素监测平台" (`font-size: 22px; font-weight: bold; color: #0D47A1;`) with logo placeholder.
  - **Middle Filter Controls Area (`display: flex; gap: 24px; margin-left: 60px;`):**
    1. *时间范围 (Date Range):* Label + Input box showing "2025-05-20 ~ 2025-05-27" with a trailing calendar suffix icon.
    2. *设备筛选 (Device Filter):* Label + Dropdown selector showing "全部设备" with a down arrow icon.
    3. *传感器筛选 (Sensor Filter):* Label + Dropdown selector showing multi-select tags "藻毒素 + 水温 + pH" with a down arrow icon.
  - **Right Action Area (`margin-left: auto;`):**
    - `导出数据` Button: `border: 1px solid var(--border-color); background: #FFF; color: var(--text-primary); border-radius: 8px; padding: 8px 16px; font-size: 14px; font-weight: 500;`

### [Node 2] Left Sidebar Navigation

- **Active State Update:** The active highlighted tab must switch to **`数据分析` (Data Analysis)**.
  - Style: Background fill (`var(--active-tab-bg)`), text/icon color (`var(--active-tab-text)`), matching standard nav item block border-radius.

### [Node 3] Top Content Row (`height: 440px; display: flex; gap: 20px;`)

#### Sub-Node 3A: 趋势分析 (Trend Analysis Multi-Axis Chart) - Left Card

- **Geometry:** `flex: 1; background: var(--panel-bg); border-radius: 16px; border: 1px solid var(--border-color); padding: 24px; position: relative;`
- **Header Area:** Title "趋势分析" (`font-size: 16px; font-weight: bold;`) with centered legend inline indicators:
  - Blue Line: 藻毒素 (µg/L) | Green Line: 水温 (°C) | Purple Line: pH
- **Triple Y-Axis Configuration:**
  - **Left Y-Axis (Blue):** Toxin scales from `0` to `5`.
  - **Right Y-Axis 1 (Green):** Temperature scales from `18` to `30`.
  - **Right Y-Axis 2 (Purple):** pH scales from `6.0` to `8.5`.
- **Chart Threshold Lines:**
  - Horizontal dashed red line at `Toxin = 5` labeled "-- 高风险阈值 (5.0 µg/L)".
  - Horizontal dashed orange line at `Toxin = 1` labeled "-- 警戒阈值 (1.0 µg/L)".
- **Data Visualization Details:**
  - Render 3 intersecting smooth spline curves (Blue, Green, Purple) across dates `05-20` to `05-27`.
  - Place 3 red alert triangle marker icons (`🔺`) on critical peak values (e.g., around 05-21, 05-23, and 05-25).

#### Sub-Node 3B: 传感器对比 (Sensor Comparison) - Right Card

- **Geometry:** `width: 400px; background: var(--panel-bg); border-radius: 16px; border: 1px solid var(--border-color); padding: 24px;`
- **Header Row:** Title "传感器对比" (`font-size: 16px; font-weight: bold;`).
- **Sub-header Row:** Subtext metrics labels "藻毒素 (µg/L)" and right-aligned "最新值 (单位)".
- **Data Rows List (`display: flex; flex-direction: column; gap: 16px; margin-top: 16px;`):**
  1. 🔴 漂华预警-06 | Right-aligned Value: **`6.35`** (`color: var(--status-danger); font-weight: bold; font-size: 18px;`)
  2. 🟡 入水口探针-02 | Right-aligned Value: **`1.36`** (`color: var(--status-warning); font-weight: bold; font-size: 18px;`)
  3. 🟢 岸线巡检猫-03 | Right-aligned Value: **`0.78`** (`color: var(--status-normal); font-weight: bold; font-size: 18px;`)
  4. 🔵 湖心浮标-01 | Right-aligned Value: **`0.42`** (`color: var(--status-info); font-weight: bold; font-size: 18px;`)
  5. 🟡 排水口监测-04 | Right-aligned Value: **`1.05`** (`color: var(--status-warning); font-weight: bold; font-size: 18px;`)

### [Node 4] Bottom Content Row (`height: 460px; display: flex; gap: 20px;`)

#### Sub-Node 4A: AI 预测 (AI Prediction Chart) - Left Card

- **Geometry:** `flex: 1; background: var(--panel-bg); border-radius: 16px; border: 1px solid var(--border-color); padding: 24px;`
- **Header Area:** Title "AI 预测（藻毒素浓度）" + Right-aligned dropdown menu selector containing text "预测未来 7 天".
- **Legend Row:** `● 历史数据` (Solid Blue), `▲ 预测值` (Dashed Blue line with nodes), `■ 置信区间 (95%)` (Light blue shaded rect marker).
- **Chart Engine Details:**
  - **X-Axis timeline:** Consecutively displays `05-20` to `06-03`.
  - **Y-Axis scale:** Left-side single metrics from `0` to `6`.
  - **Line Structure:** Transition happens around `05-26`. Values before `05-26` use a solid smooth curve (Historical Data). From `05-26` onwards to `06-03`, the line styles switch to a dashed curve with data node points (Predicted Values).
  - **Confidence Fill Area:** A shaded polygon layer spanning from `05-26` to `06-03` under and above the dashed line trajectory representing the 95% confidence bounds. Fill style: `background: rgba(26, 115, 232, 0.12);`.

#### Sub-Node 4B: 模型指标 (Model Metrics) - Right Card

- **Geometry:** `width: 400px; background: var(--panel-bg); border-radius: 16px; border: 1px solid var(--border-color); padding: 24px; display: flex; flex-direction: column; gap: 24px;`
- **Card Element 1 (Top Block):**
  - Label: "模型置信度" (`color: var(--text-muted); font-size: 14px;`)
  - Large Value: **`87%`** (`font-size: 38px; font-weight: 800; color: var(--chart-toxin-blue); margin-top: 8px;`)
- **Divider line:** Light horizontal grey separator line.
- **Card Element 2 (Middle Block):**
  - Label: "预测区间 (95%)" (`color: var(--text-muted); font-size: 14px;`)
  - Value Range: **`0.45 - 3.20`** `µg/L` (`font-size: 20px; font-weight: 700; color: var(--text-primary); margin-top: 4px;`)
- **Card Element 3 (Bottom Block):**
  - Label: "下一高风险时间" (`color: var(--text-muted); font-size: 14px;`)
  - Date Value: **`5月29日`** (`font-size: 20px; font-weight: 700; color: var(--text-primary); margin-top: 4px;`)

## 3. Pencil Design Plugin Compilation Constraints

1. **Isolation of Decorative Elements:** The large vector illustration of the microscope and lab beakers at the bottom-left corner of the content area must be compiled as an absolute-positioned overlay node layer group labeled `[Overlay_Decoration_Microscope]`.
2. **Chart Spline Accuracy:** Do not render rough charts; calculate smooth control anchors for Bezier curves to capture the perfect waves displayed in both the Trend Analysis and AI Prediction widgets.
3. **Strict Text Segregation:** Avoid joining data values and text strings into a singular text field block; force separate layer properties for values like `6.35` and units like `µg/L` to support proper font weighting.