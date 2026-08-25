# Web 平台后端接口接入说明

## 1. 接入方式

前端所有业务数据均通过 `src/services/` 获取。默认 `VITE_USE_MOCKS=true`，页面使用内存和 `localStorage` 中的模拟数据；真实后端就绪后复制 `.env.example` 为 `.env.local`，并配置：

```env
VITE_USE_MOCKS=false
VITE_API_BASE_URL=http://localhost:8080/api/v1
VITE_WS_URL=ws://localhost:8080/api/v1/realtime
```

HTTP service 支持两种响应格式：直接返回业务对象，或使用统一包裹：

```json
{
  "data": {},
  "timestamp": "2026-08-10T15:42:00Z",
  "requestId": "req_01J..."
}
```

约定：

- 编码：UTF-8，`Content-Type: application/json`。
- 时间：ISO 8601；前端也兼容演示数据中的 `YYYY-MM-DD HH:mm`。
- 坐标：WGS84，经度 `lng`、纬度 `lat`。
- 单位：藻毒素 `μg/L`，水温 `°C`，信号 `dBm`，电量 `%`。
- 风险阈值：正常 `<0.5`；关注 `0.5–1.0`；警戒 `1.0–5.0`；高风险 `>5.0 μg/L`。
- 错误：建议返回 `{ "code": "DEVICE_NOT_FOUND", "message": "设备不存在", "details": {} }`，并使用正确 HTTP 状态码。

## 2. 核心数据结构

### 2.1 DeviceReading

```json
{
  "id": "aq-006",
  "name": "藻华预警浮标-06",
  "status": "online",
  "connectionType": "wifi",
  "locationLabel": "东湖湖心区",
  "lat": 30.5699,
  "lng": 114.3864,
  "batteryPercent": 86,
  "signalDbm": -61,
  "toxinUgL": 6.35,
  "waterTempC": 24.8,
  "ph": 7.4,
  "updatedAt": "2026-08-10T15:42:00Z"
}
```

枚举：

- `status`: `online | idle | offline`
- `connectionType`: `bluetooth | wifi | none`

### 2.2 DeviceHistoryPoint

```json
{
  "time": "2026-08-10T15:40:00Z",
  "toxinUgL": 1.36,
  "waterTempC": 25.5,
  "ph": 7.1,
  "batteryPercent": 63,
  "signalDbm": -74
}
```

### 2.3 PredictionPoint

```json
{
  "time": "2026-08-11T00:00:00Z",
  "value": 2.7,
  "lowerBound": 1.4,
  "upperBound": 3.8,
  "isPrediction": true
}
```

## 3. REST API

### 3.1 总览摘要

`GET /dashboard/summary`

响应：

```json
{
  "totalDevices": 14,
  "onlineDevices": 9,
  "idleDevices": 2,
  "offlineDevices": 3,
  "lowBatteryDevices": 3,
  "weakSignalDevices": 2,
  "averageToxinUgL": 2.5,
  "maxToxinReading": { "id": "aq-006", "name": "藻华预警浮标-06", "toxinUgL": 6.35 }
}
```

`maxToxinReading` 可返回完整 `DeviceReading`；无数据时为 `null`。

### 3.2 最新读数

`GET /readings/latest?deviceId=&status=&risk=&limit=`

响应：`DeviceReading[]`。不传查询参数时返回全部设备最新读数。

### 3.3 设备列表与 CRUD

- `GET /devices` → `DeviceReading[]`
- `POST /devices` → 新建后的 `DeviceReading`
- `PATCH /devices/:id` → 更新后的 `DeviceReading`
- `DELETE /devices/:id` → `204 No Content`

新增请求：

```json
{
  "name": "湖心浮标-15",
  "connectionType": "wifi",
  "locationLabel": "东湖待部署点",
  "lat": 30.5667,
  "lng": 114.3833
}
```

`lat`、`lng` 可选；后端未获得坐标时应返回待部署状态，而不是使用 `(0, 0)`。

### 3.4 设备排序

`PUT /devices/order`

```json
{ "ids": ["aq-006", "aq-002", "aq-003"] }
```

响应：完整排序后的 `DeviceReading[]`。后端需校验重复 ID 与越权 ID；请求未包含的设备可追加在末尾。

### 3.5 设备历史

`GET /devices/:id/history?from=2026-08-03T00:00:00Z&to=2026-08-10T23:59:59Z&interval=1h`

响应：`DeviceHistoryPoint[]`，按时间升序。

### 3.6 扫描与配对

`POST /devices/scan`

可选请求：`{ "protocols": ["bluetooth", "wifi"], "timeoutSeconds": 10 }`

响应：

```json
[
  {
    "id": "scan-7f2a",
    "name": "WaterProbe-7F2A",
    "connectionType": "bluetooth",
    "signalDbm": -48,
    "paired": false
  }
]
```

`POST /devices/pair`

请求为一条扫描结果，可附加 Wi-Fi 凭证引用；禁止把明文密码写入日志。响应为正式创建/绑定后的 `DeviceReading`。

### 3.7 趋势分析

`GET /analytics/trends?deviceId=aq-006&from=&to=&interval=12h`

响应：

```json
[
  { "time": "2026-08-10T00:00:00Z", "toxinUgL": 1.2, "waterTempC": 24.8, "ph": 7.3 }
]
```

### 3.8 模型预测

`POST /predict`

请求：

```json
{
  "region": "east-lake",
  "deviceId": "aq-006",
  "forecastDays": 7,
  "inputFeatures": {}
}
```

建议响应：

```json
{
  "points": [
    { "time": "2026-08-11T00:00:00Z", "value": 2.7, "lowerBound": 1.4, "upperBound": 3.8, "isPrediction": true }
  ],
  "confidence": 0.87,
  "modelVersion": "cmadre-ensemble-2.1",
  "ood": false,
  "generatedAt": "2026-08-10T15:42:00Z"
}
```

当前前端 service 为简化接入，直接读取 `PredictionPoint[]`。真实接口若采用上述带元数据格式，应在 `monitoringService.getPredictions` 中把 `points` 返回给页面，并保存其余元数据用于模型卡片。

## 4. WebSocket 实时事件

连接：`WS /realtime`。前端入口为 `src/services/realtimeService.ts`。

```json
{
  "event": "sensor_update",
  "timestamp": "2026-08-10T15:42:00Z",
  "payload": {
    "deviceId": "aq-006",
    "reading": { "toxinUgL": 6.35, "waterTempC": 24.8, "ph": 7.4 }
  }
}
```

支持事件：

| event | 用途 |
| --- | --- |
| `sensor_update` | 合并最新传感器读数 |
| `risk_alert` | 展示阈值或模型风险告警 |
| `device_status` | 更新在线/离线、电量和信号 |
| `task_status` | 预留给无人机/模拟任务进度 |

生产环境建议增加心跳、指数退避重连、最后事件 ID 和鉴权令牌刷新。不要把设备密钥放入 URL 查询参数。

## 5. 检测节点上行映射

ESP32 可继续按项目计划通过 MQTT QoS 1 上报至数据中台：

```text
Topic: sensor/{device_id}/data
```

数据中台需把硬件字段映射为 Web DTO：

| 硬件字段 | Web 字段 |
| --- | --- |
| `device_id` | `id` |
| `timestamp` | `updatedAt` |
| `battery_mv` | 换算为 `batteryPercent` |
| `readings.water_temp` | `waterTempC` |
| `readings.ph` | `ph` |
| 生物传感标定结果 | `toxinUgL` |
| 网关 RSSI | `signalDbm` |

建议后端而非浏览器承担标定、单位换算、异常值剔除、状态判定和风险分级，保证各客户端口径一致。

## 6. 联调检查表

- 使用 `.env.local` 切换真实 API 后四个路由均能直接刷新。
- 设备时间戳、经纬度和单位与本文一致。
- 删除接口使用 `204` 时前端不会尝试解析 JSON。
- 预测区间满足 `lowerBound <= value <= upperBound`。
- WebSocket 断开不会清空页面已有数据。
- CORS 允许开发地址，生产环境限制到正式域名/Tauri 来源。
- 设备凭证和模型内部敏感信息不下发到浏览器。
