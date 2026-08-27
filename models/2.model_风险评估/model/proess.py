"""
Created on 2026-08-27
Updated on 2026-08-27
@author: https://github.com/Linmoqian
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from data import read_sensor_data


def plot_sensor_locations(csv_path: str | Path) -> None:
    """绘制每个传感器最新的有效 GPS 位置。"""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print("[warning] GPS 数据文件不存在")
        return

    latest_locations = {
        data.sensor_id: data
        for data in read_sensor_data(csv_path)
        if data.gps_valid
        and data.latitude_deg is not None
        and data.longitude_deg is not None
    }
    if not latest_locations:
        print("[warning] 没有有效 GPS 数据")
        return

    figure, axes = plt.subplots()
    for sensor_id, data in latest_locations.items():
        axes.scatter(data.longitude_deg, data.latitude_deg)
        axes.annotate(sensor_id, (data.longitude_deg, data.latitude_deg))
    axes.set(xlabel="Longitude (deg)", ylabel="Latitude (deg)", title="Sensor GPS")
    axes.grid()
    figure.tight_layout()
    plt.show()
