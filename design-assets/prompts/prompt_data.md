# Role & Core Objective
You are an elite, pixel-perfect UI/UX Front-End Structural Engineer AI. Your absolute goal is to reverse-engineer the provided data analysis interface design (`数据分析页目标.png`) into a high-fidelity, production-ready `.pen` file using the **Pencil Design Plugin**.

You must interpret the image with strict mathematical and geometric precision. Replicate exact padding, alignment, font weights, color hex codes, chart structures, and border radii without introducing any arbitrary variations.

---

## 1. Global Layout Engine & Design Tokens

### 📐 Structural Grid & Dimensions (Based on 1920x1080 Viewport)
* **Canvas Boundary:** `width: 1920px; height: 1080px; box-sizing: border-box;`
* **Global Layout Scheme:**
    * **Sidebar Width:** `240px` (Fixed left layout)
    * **Top Nav Height:** `80px` (Fixed top layout, spans across `width: 1680px` from left offset)
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
  --active-pill-bg: #E0F2FE;
  --active-pill-text: #0284C7;
  
  /* Chart Line Palette */
  --chart-toxin-blue: #1A73E8;
  --chart-temp-green: #10B981;
  --chart-ph-purple: #8B5CF6;
  
  /* Status/Risk Palette */
  --status-danger: #EF4444;      /* Red */
  --status-warning: #FF7A00;     /* Orange/Alert */
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
  - **Left Brand Area:** Title text "水体藻毒素监测平台" (`font-size: 22px; font-weight: bold; color: #0D47A1;`) with logo asset placeholder.
  - **Middle Filter Controls Area (`display: flex; gap: 24px; margin-left: 60px;`):**
    1. *时间范围 (Date Range):* Label + Input border-box showing "2025-05-20 ~ 2025-05-27" with a trailing calendar vector icon extension.
    2. *设备筛选 (Device Filter):* Label + Dropdown selector showing text "全部设备" with a down arrow chevron.
    3. *传感器筛选 (Sensor Filter):* Label + Dropdown selector showing multi-select combined tags "藻毒素 + 水温 + pH" with a down arrow chevron.
  - **Right Action Area (`margin-left: auto;`):**
    - `导出数据` Button: `border: 1px solid var(--border-color); background: #FFF; color: var(--text-primary); border-radius: 8px; padding: 8px 16px; font-size: 14px; font-weight: 500;`

### [Node 2] Left Sidebar Navigation

- **Active State Update:** The active highlighted tab is **`数据分析` (Data Analysis)**.
  - Style: Background fill block (`var(--active-tab-bg)`), text/icon color (`var(--active-tab-text)`), matching standard nav item block border-radius (`8px`).

### [Node 3] Top Content Row (`height: 440px; display: flex; gap: 20px;`)

#### Sub-Node 3A: 趋势分析 (Trend Analysis Multi-Axis Chart) - Left Card

- **Geometry:** `flex: 1; background: var(--panel-bg); border-radius: 16px; border: 1px solid var(--border-color); padding: 24px; position: relative;`
- **Header Area:** Title "趋势分析" (`font-size: 16px; font-weight: bold;`) with centered horizontal legend inline line indicators:
  - Blue Line Marker: 藻毒素 (µg/L) | Green Line Marker: 水温 (°C) | Purple Line Marker: pH
- **Triple Y-Axis Configuration:**
  - **Left Y-Axis (Blue, `#1A73E8`):** Toxin scales ranging linearly from `0` to `5`.
  - **Right Y-Axis 1 (Green, `#10B981`):** Temperature scales ranging linearly from `18` to `30`.
  - **Right Y-Axis 2 (Purple, `#8B5CF6`):** pH scales ranging linearly from `6.0` to `8.5` (positioned further right).
- **Chart Threshold Lines:**
  - Horizontal dashed red line exact at `Toxin = 5` labeled text "-- 高风险阈值 (5.0 µg/L)".
  - Horizontal dashed orange line exact at `Toxin = 1` labeled text "-- 警戒阈值 (1.0 µg/L)".
- **Data Visualization Curves:**
  - Render 3 intersecting smooth spline paths (Blue, Green, Purple) across dates `05-20` to `05-27` on X-axis.
  - Place 3 distinct red alert triangle marker icons (`🔺`) on critical peak threshold violations (located near dates 05-21, 05-23, and 05-25).

#### Sub-Node 3B: 传感器对比 (Sensor Comparison List) - Right Card

- **Geometry:** `width: 400px; background: var(--panel-bg); border-radius: 16px; border: 1px solid var(--border-color); padding: 24px;`
- **Header Line:** Title "传感器对比" (`font-size: 16px; font-weight: bold;`).
- **Sub-header Subtext:** Column labels "藻毒素 (µg/L)" and right-aligned "最新值 (单位)" (`color: var(--text-muted); font-size: 12px;`).
- **Data Rows List Matrix (`display: flex; flex-direction: column; gap: 16px; margin-top: 16px;`):**
  1. ● 漂华预警-06 (Blue dot) | Right-aligned Value: **`6.35`** (`color: var(--status-danger); font-weight: bold; font-size: 18px;`)
  2. ● 入水口探针-02 (Orange dot) | Right-aligned Value: **`1.36`** (`color: var(--status-warning); font-weight: bold; font-size: 18px;`)
  3. ● 岸线巡检猫-03 (Green dot) | Right-aligned Value: **`0.78`** (`color: var(--status-normal); font-weight: bold; font-size: 18px;`)
  4. ● 湖心浮标-01 (Cyan dot) | Right-aligned Value: **`0.42`** (`color: var(--status-info); font-weight: bold; font-size: 18px;`)
  5. ● 排水口监测-04 (Orange dot) | Right-aligned Value: **`1.05`** (`color: var(--status-warning); font-weight: bold; font-size: 18px;`)

### [Node 4] Bottom Content Row (`height: 460px; display: flex; gap: 20px;`)

#### Sub-Node 4A: AI 预测 (AI Prediction Chart Widget) - Left Card

- **Geometry:** `flex: 1; background: var(--panel-bg); border-radius: 16px; border: 1px solid var(--border-color); padding: 24px;`
- **Header Area:** Title "AI 预测（藻毒素浓度）" + Right-aligned dropdown option wrapper containing text "预测未来 7 天".
- **Legend Metadata Row:** `● 历史数据` (Solid Blue), `▲ 预测值` (Dashed Blue line path with nodes), `■ 置信区间 (95%)` (Light blue shaded rect opacity box).
- **Chart Axis Metrics:**
  - **X-Axis timeline sequence:** Consecutively maps dates `05-20` through `06-03`.
  - **Y-Axis scale (Left):** Single metrics parameters from bounds `0` to `6` (`µg/L`).
- **Line Path Logic:**
  - Transition occurs at `05-26`. Coordinates before `05-26` use a solid smooth spline curve (Historical Data).
  - From `05-26` onward to `06-03`, the path transitions into a dashed curve accented with node point vectors (Predicted Values).
  - **Confidence Interval Bounds Area:** A custom shaded translucent polygon layer spanning horizontally from `05-26` to `06-03` wrapping both above and below the dashed path. CSS: `fill: rgba(26, 115, 232, 0.12); stroke: none;`.

#### Sub-Node 4B: 模型指标对齐 (Model Metrics Inspection) - Right Card

- **Geometry:** `width: 400px; background: var(--panel-bg); border-radius: 16px; border: 1px solid var(--border-color); padding: 24px; display: flex; flex-direction: column; gap: 20px;`
- **Metric Card Box 1 (Top):**
  - Label: "模型置信度" (`color: var(--text-muted); font-size: 14px;`)
  - Large Primary Value: **`87%`** (`font-size: 38px; font-weight: 800; color: var(--chart-toxin-blue); margin-top: 6px;`)
- **Horizontal Divider Line:** Solid fine rule (`border-top: 1px solid #F1F5F9;`).
- **Metric Card Box 2 (Middle):**
  - Label: "预测区间 (95%)" (`color: var(--text-muted); font-size: 14px;`)
  - Secondary Value: **`0.45 - 3.20`** `µg/L` (`font-size: 20px; font-weight: 700; color: var(--text-primary); margin-top: 4px;`)
- **Metric Card Box 3 (Bottom):**
  - Label: "下一高风险时间" (`color: var(--text-muted); font-size: 14px;`)
  - Date Value Content: **`5月29日`** (`font-size: 20px; font-weight: 700; color: var(--text-primary); margin-top: 4px;`)

## 3. Pencil Design Plugin Compilation Constraints

1. **Isolation of Decorative Elements:** The vector illustration asset group representing the microscope and chemical flask positioned at the bottom-left corner of the workspace must be isolated into a standalone absolute overlay group labeled `[Overlay_Decoration_Microscope_Labware]`.
2. **Strict Axis & Font Weights Separation:** Do not compress numeric values alongside units into single text blocks. Keep fields like `6.35` and `µg/L` as distinct vector text blocks to preserve the exact weights and color tokens specified.
3. **Spline Vector Accuracy:** Ensure that chart trajectories utilize precise Bezier control anchors to recreate the exact wave amplitudes shown in both the Trend Multi-Axis and AI Prediction viewports.

Generate the final highly accurate `.pen` structured definition output parsing these rules step by step.