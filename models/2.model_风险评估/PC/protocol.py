"""
Created on 2026-08-27
Updated on 2026-08-27
@author: https://github.com/Linmoqian
"""

from __future__ import annotations

BAUD_RATE = 115200
CSV_FIELDS = [
    "sensor_id",
    "device_uptime_ms",
    "gps_valid",
    "latitude_deg",
    "longitude_deg",
]


def parse_sensor_data(raw_line: bytes) -> list[str] | None:
    """解析 ESP32 发来的单行传感器数据。"""
    line = raw_line.decode("ascii").strip()
    if not line:
        return None

    parts = line.split(",")
    if len(parts) != 5 or not parts[0] or parts[2] not in {"0", "1"}:
        raise ValueError("invalid sensor data")

    int(parts[1])
    if parts[2] == "1":
        latitude = float(parts[3])
        longitude = float(parts[4])
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError("invalid GPS coordinates")

    return parts
