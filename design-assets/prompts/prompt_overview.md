# Role & Goal
You are a pixel-perfect UI/UX front-end design agent specializing in replicating web dashboard interfaces. Your task is to use the **Pencil Design Plugin** to perfectly recreate the provided webpage design (`总览页目标.png`) and output a high-fidelity, production-ready `.pen` file. 

You must maintain absolute visual consistency, adhering strictly to the layout hierarchy, typography, padding, spacing, and color palette specified below.

---

## 1. Global Styles & Design Tokens

### 🎨 Color Palette (CSS Reference)
* **Main Background:** `background: linear-gradient(180deg, #F4F8FC 0%, #E6F0FA 100%);` (A very light, soft blue-gray gradient)
* **Card Background:** `#FFFFFF` with smooth shadows (`box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.03);`)
* **Border Radius:** Standardized card corners at `border-radius: 16px;`, smaller components at `border-radius: 8px;`
* **Brand Primary Blue:** `#1A73E8` or `#2575FC` (Used for selected states, tabs, and main chart line)
* **Status Colors:**
    * **Success/Normal (Green):** `#22C55E` (Text & Icons)
    * **Info/Muted (Blue/Gray):** `#3B82F6` (Offline/Info)
    * **Attention (Yellow):** `#EAB308` or `#F59E0B` (For "关注告警")
    * **Warning (Orange):** `#FF7A00` (For "警戒告警")
    * **Danger (Red):** `#EF4444` (For "高风险告警", font weight: bold)
* **Typography Colors:**
    * Primary Text (Titles, Dark Labels): `#1E293B`
    * Secondary Text (Subtext, Units): `#64748B`
    * Muted Text (Dates, Placeholders): `#94A3B8`

### 📐 Layout Structure
* **Overall Canvas:** 1920x1080 pixel standard desktop dashboard.
* **Layout Type:** Left Sidebar + Top Navigation + Main Content Grid.

---

## 2. Detailed Component Breakdown

### 🛠️ Layout 1: Top Navigation Bar
* **Left Section:** * Logo illustration placeholder.
    * Title text: "水体藻毒素监测平台" (Font-size: 22px, Font-weight: bold, Color: `#0F172A`).
* **Middle Section (Nav Tabs):** * Tabs: `总览` (Active), `地图监视`, `数据分析`, `设备配对`.
    * Active State (`总览`): Light blue background fill (`#E0F2FE`), text color (`#0284C7`), rounded corners (`border-radius: 20px`), padding: `8px 20px`.
    * Inactive States: Transparent background, text color (`#64748B`).
* **Right Section:** * Notification Bell Icon.
    * User Profile Dropdown: Avatar image placeholder + Text "IGEM Team" + Down arrow.

### 🗂️ Layout 2: Left Sidebar Navigation
* Mirrors the Top Navigation tabs vertically (`总览` active with a light blue block indicator on the left).
* **Bottom Left Corner:** Features a large, cute anime mascot character illustration asset standing on water ripples. Reserve space for this vector/image layers.

### 📊 Layout 3: Main Dashboard Content (Grid Layout)

#### 🔸 Row 1: Status KPI Cards (5 Cards inline, equal spacing)
1.  **在线设备 (Online Devices):** Big Number `9` (Green, `#22C55E`), Total `/ 14 台`. Subtext: "数据正常传输中". Icon: Green circular Wi-Fi wave icon.
2.  **空闲设备 (Idle Devices):** Big Number `2` (Orange, `#FF7A00`), Total `/ 14 台`. Subtext: "设备待机中". Icon: Orange circular clock icon.
3.  **离线设备 (Offline Devices):** Big Number `3` (Gray, `#64748B`), Total `/ 14 台`. Subtext: "设备离线". Icon: Gray circular 'X' icon.
4.  **平均藻毒素 (Avg Algal Toxin):** Big Number `2.50` (Blue, `#1A73E8`), Unit `µg/L`. Subtext: "较昨日 -0.18 µg/L" (Greenish/Muted). Icon: Blue circular globe/water icon.
5.  **最高风险 (Highest Risk):** Big Number `6.35` (Red, `#EF4444`), Unit `µg/L`. Subtext: "漂华预警浮标-06". Icon: Red circular warning triangle icon.

#### 🔸 Row 2: Detailed Analysis Section (3 Cards split horizontally)
* **Card 1 (Left): 系统状态 (System Status)**
    * Header: "系统状态"
    * Center: Large green shield check icon + Big Bold Text "运行正常" (`#22C55E`) + Subtext "所有系统功能正常运行".
    * Bottom Row: Three horizontal mini-metrics:
        * 数据采集: Green dot + "正常"
        * 数据传输: Green dot + "正常"
        * 设备在线率: Bold Text "64%"
* **Card 2 (Middle): 告警摘要 (Alert Summary)**
    * Header: "告警摘要"
    * List view with 4 rows (Each row has a light background tint, icon, label, count, and a right arrow `>`):
        1.  高风险告警 (Red triangle) -> Count: `1` (Red)
        2.  警戒告警 (Orange triangle) -> Count: `2` (Orange)
        3.  关注告警 (Yellow triangle) -> Count: `3` (Yellow)
        4.  设备离线 (Blue info circle) -> Count: `3` (Blue)
* **Card 3 (Right): 趋势概览 (Trend Overview)**
    * Header: "趋势概览（平均藻毒素）" + Right-aligned Dropdown selector showing "近7天".
    * Chart Type: Smooth Bezier Line Chart (Spline).
    * Line Color: Vibrant Blue (`#1A73E8`), thickness `3px`, with a soft blue gradient area fill underneath.
    * Data Points: 7 points labeled from `05-21` to `05-27` on X-axis. Y-axis ranges from `0.5` to `4.5` with steps of `1.0`. Peak is on `05-23` (~4.3), ending point on `05-27` is highlighted with a data label tooltip `2.50`.

#### 🔸 Row 3: Bottom Table (Latest Samples)
* **Header:** "最新采样（近5条）" on the left, "查看全部" clickable link text on the right.
* **Table Layout:** Clean modern borderless table with a light gray header row (`#F8FAFC`).
* **Columns:** 设备名称 | 采样时间 | 藻毒素 (µg/L) | 电量 | 信号强度 | 状态 | 位置
* **Rows & Data Specifications:**
    1.  漂华预警浮标-06 | 2025-05-27 09:42 | `6.35` (Red) | 86% | -61 dBm | 🔴 高风险 (Red text) | 东湖湖心区
    2.  入水口探针-02 | 2025-05-27 09:40 | `1.36` (Greenish) | 63% | -74 dBm | 🟡 关注 (Orange text) | 北侧入水口
    3.  岸线巡检猫-03 | 2025-05-27 09:33 | `0.78` (Greenish) | 38% | -83 dBm | 🟢 正常 (Green text) | 西侧岸线浅水区
    4.  湖心浮标-01 | 2025-05-27 09:32 | `0.42` (Greenish) | 86% | -61 dBm | 🟢 正常 (Green text) | 东湖湖心区
    5.  排水口监测-04 | 2025-05-27 09:21 | `1.05` (Greenish) | 55% | -74 dBm | 🟡 关注 (Orange text) | 后湖排水口

---

## 3. Output Generation Rules for Pencil Plugin
1.  **Pixel-Level Proportions:** Ensure card widths, paddings (`padding: 24px` for cards), and vertical margins match the visual distribution perfectly.
2.  **Layers Grouping:** Group each logical component (e.g., `Card_Online_Devices`, `Table_Latest_Samples`) cleanly within the `.pen` file hierarchy.
3.  **Mascot Placeholder:** For the cute anime characters (bottom left and top right), generate clear vector shape bounding boxes labeled `[Mascot Character Asset]` so they can be easily replaced or maintained.

Please compile all the rules above and output the definitive, fully configured `.pen` file layout structure.