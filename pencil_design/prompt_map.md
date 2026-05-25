1. # Role & Core Objective
   You are an elite, pixel-perfect UI/UX Front-End Structural Engineer AI. Your absolute goal is to reverse-engineer the provided interface design (`地图监视页目标.png`) into a high-fidelity, production-ready `.pen` file using the **Pencil Design Plugin**. 

   You must interpret the image with strict mathematical and geometric precision. No creative liberties allowed—replicate exact padding, alignment, font weights, color hex codes, and border radii.

   ---

   ## 1. Global Layout Engine & Design Tokens

   ### 📐 Structural Grid & Dimensions (Based on 1920x1080 Viewport)
   * **Canvas Boundary:** `width: 1920px; height: 1080px; box-sizing: border-box;`
   * **Global Layout Scheme:** * **Sidebar Width:** `240px` (Fixed left)
       * **Top Nav Height:** `80px` (Fixed top, offsets from `left: 240px`)
       * **Main Workspace Content:** `width: 1640px; height: 960px; margin: 20px; gap: 20px; display: flex; flex-direction: row;`
           * **Left Map Block:** `flex: 1;` (Approx `1140px` width)
           * **Right Inspector Panel:** `width: 440px;` (Fixed right)

   ### 🎨 Precise Color & Asset Tokens
   ```css
   :root {
     /* Backgrounds */
     --global-bg: linear-gradient(180deg, #F4F8FC 0%, #E6F0FA 100%);
     --panel-bg: #FFFFFF;
     --header-bg: #F8FAFC;
     
     /* Brand & Active States */
     --primary-blue: #0084FF;
     --active-tab-bg: #E6F0FA;
     --active-tab-text: #1A73E8;
     --active-pill-bg: #E0F2FE;
     --active-pill-text: #0284C7;
     
     /* Status/Risk Palette */
     --status-normal: #22C55E;   /* Green */
     --status-attention: #F59E0B;/* Yellow */
     --status-warning: #FF7A00;  /* Orange */
     --status-danger: #EF4444;   /* Red */
     --status-info: #3B82F6;     /* Blue */
     
     /* Typography */
     --text-primary: #0F172A;
     --text-secondary: #475569;
     --text-muted: #64748B;
     --border-color: #E2E8F0;
   }

## 2. Component Node Tree & CSS Blueprint (Pixel-Perfect Specs)

### [Node 1] Top Navigation Bar

- **Geometry:** `height: 80px; padding: 0 32px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border-color);`
- **Middle Tabs (`display: flex; gap: 24px;`):**
  - `地图监视` (Active State): `background: var(--active-pill-bg); color: var(--active-pill-text); border-radius: 20px; padding: 6px 20px; font-weight: 600;`
  - `总览`, `数据分析`, `设备配对` (Inactive): `color: var(--text-secondary); font-weight: 400;`

### [Node 2] Left Sidebar Navigation

- **Geometry:** `width: 240px; height: 100%; border-right: 1px solid var(--border-color); padding: 32px 16px;`
- **Active Tab:** `地图监视` must have a vertical selection visual indicator matching the top nav active tokens.
- **Mascot Vector Layer:** Absolute positioned container at `bottom: 0; left: 0; width: 220px; height: auto;` containing the water-ripple anime girl asset placeholder.

### [Node 3] Main Workspace Area (`display: flex; gap: 20px; padding: 20px;`)

#### Sub-Node 3A: Map Container (Left Panel)

- **Geometry:** `position: relative; flex: 1; border: 1px solid var(--border-color); border-radius: 16px; overflow: hidden;`
- **Layer 3A-1: Map Layer Controls (Top Right Overlay)**
  - `position: absolute; top: 16px; right: 16px; display: flex; gap: 12px; z-index: 10;`
  - `设备图层` Button: `background: #FFF; border: 1px solid var(--border-color); border-radius: 8px; padding: 8px 16px; color: var(--text-secondary);`
  - `热力图层` Button (Active): `background: var(--active-pill-bg); border: 1px solid transparent; border-radius: 8px; padding: 8px 16px; color: var(--active-pill-text); font-weight: bold;`
- **Layer 3A-2: Map Zoom Controls (Top Left Overlay)**
  - `position: absolute; top: 16px; left: 16px; display: flex; flex-direction: column; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);`
  - Contains `+`, `-`, and location target tracking button layers. White background, height/width `40px` each.
- **Layer 3A-3: Heatmap & Vector Pins**
  - **Heatmap Core:** Centered radial gradient circle. Center `rgba(239, 68, 68, 0.85)` shifting outward into Orange `rgba(255, 122, 0, 0.6)`, Yellow `rgba(245, 158, 11, 0.4)`, and Light Blue fading to 0% opacity.
  - **Pins Overlay:** Generate 8 specific map markers. Replicate exact shape (Teardrop vector + center white core filled with asset icon). Ensure the center pin is Red (`var(--status-danger)`) with a white buoy symbol.
- **Layer 3A-4: Risk Legend (Bottom Left Floating Overlay)**
  - `position: absolute; bottom: 16px; left: 16px; right: 16px; background: rgba(255,255,255,0.95); border-radius: 12px; padding: 16px 24px; display: flex; align-items: center; gap: 32px;`
  - Title: "风险图例" (`font-size: 14px; font-weight: bold; color: var(--text-primary);`)
  - Items: Render 4 inline flex blocks with circular colored indicators matching `--status-normal`, `--status-attention`, `--status-warning`, and `--status-danger` with accompanying text ranges.

#### Sub-Node 3B: Device Detail Panel (Right Panel)

- **Geometry:** `width: 440px; background: var(--panel-bg); border-radius: 16px; border: 1px solid var(--border-color); padding: 24px; display: flex; flex-direction: column; justify-content: space-between;`
- **Layer 3B-1: Title & Status Banner**
  - Subtitle: "选中设备" (`font-size: 12px; color: var(--text-muted); margin-bottom: 4px;`)
  - Title Row: `display: flex; justify-content: space-between; align-items: center;`
    - Text: "漂华预警浮标-06" (`font-size: 22px; font-weight: 700; color: var(--text-primary);`)
    - Badge: "● 高风险" (`color: var(--status-danger); font-size: 14px; font-weight: 600;`)
- **Layer 3B-2: Core Metric Section**
  - Device Status Block: `display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #F1F5F9;` -> "设备状态" | "● 在线" (`color: var(--status-normal);`)
  - Concentration Metric: `margin: 16px 0;`
    - Label: "藻毒素浓度" (`font-size: 14px; color: var(--text-muted);`)
    - Value Block: **`6.35`** (`font-size: 40px; font-weight: 800; color: var(--status-danger); line-height: 1;`) + `µg/L` (`font-size: 14px; color: var(--text-muted); margin-left: 6px;`)
  - Update Time Block: `display: flex; justify-content: space-between; color: var(--text-muted); font-size: 13px;` -> "更新时间" | "2025-05-27 09:42"
- **Layer 3B-3: 2x2 Grid Metrics Matrix**
  - `display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px;`
  - Each grid box: `border: 1px solid #F1F5F9; border-radius: 12px; padding: 12px; background: #FAFCFF;`
    - Box 1: Icon + "电量" | Value: **`86 %`** (`font-size: 20px; font-weight: 700;`)
    - Box 2: Icon + "信号强度" | Value: **`-61 dBm`** (`font-size: 20px; font-weight: 700;`)
    - Box 3: Icon + "水温" | Value: **`24.8 ℃`** (`font-size: 20px; font-weight: 700;`)
    - Box 4: Icon + "pH" | Value: **`7.4`** (`font-size: 20px; font-weight: 700;`)
- **Layer 3B-4: Metadata Details List**
  - `margin: 20px 0; display: flex; flex-direction: column; gap: 10px; font-size: 14px;`
  - Row 1: 📍 位置 `var(--text-muted)` | 东湖湖心区 `var(--text-primary)`
  - Row 2: 🌐 设备类型 `var(--text-muted)` | 预警浮标 `var(--text-primary)`
  - Row 3: 📋 备注 `var(--text-muted)` | 东湖湖心浮标点 `var(--text-primary)`
- **Layer 3B-5: Primary CTA Button**
  - `width: 100%; height: 48px; background: var(--primary-blue); color: #FFFFFF; font-weight: 700; font-size: 16px; border-radius: 12px; text-align: center; line-height: 48px; cursor: pointer; border: none;`
  - Text Content: "查看历史数据"

## 3. Pencil Design Plugin Compilation Constraints

1. **Strict Vector Translation:** Do not group diverse texts into individual multi-line strings. Every static text field and every value dynamic field must occupy distinct vector structural text blocks to avoid truncation.
2. **Explicit Padding & Alignment:** Implement exact spacing using the specified CSS margins and paddings above into Pencil node property configurations.
3. **Mascot Layers Partitioning:** Isolate the hanging green mascot on the top-right of the Inspector card and the sitting mascot next to the 3D buoy on the bottom right into standalone overlay node definitions labeled `[Overlay_Mascot_TopRight]` and `[Overlay_Mascot_BottomRight]` respectively.

Generate the final highly accurate `.pen` structured definition output parsing these rules step by step.