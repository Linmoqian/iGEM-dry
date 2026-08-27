# 2.model_风险评估

当前阶段仅采集传感器 ID 和 GPS，暂不计算风险值。

- ESP32：在 `ESP32/main.cpp` 顶部配置 `SENSOR_ID`、`PUSH_STYLE` 和 GPS UART 引脚；ID 不得包含逗号。
- `PUSH_STYLE = "serial"` 时通过串口发送；`"server"` 为云端通道，但地址、协议和鉴权尚未配置。
- 数据采集：`PC/READ.py` 读取串口并更新 CSV；在文件顶部配置 `COM_PORT` 和 `CSV_PATH`。
- 数学建模：`model/main.py` 只读取 CSV 并绘图；在文件顶部配置 `CSV_PATH`，不连接串口。
- 串口协议：`sensor_id,device_uptime_ms,gps_valid,latitude_deg,longitude_deg`。
- CSV 列与串口协议相同，每行代表一次采样。
- GPS 坐标使用 WGS 84 经纬度，单位为度；无有效定位时经纬度留空。
