"""
Created on 2026-08-27
Updated on 2026-08-27
@author: https://github.com/Linmoqian
"""

from __future__ import annotations

from pathlib import Path

from proess import plot_sensor_locations

CSV_PATH = Path(__file__).resolve().parents[3] / "data/2.data_时空浓度/sensor_gps.csv"


def main() -> None:
    """读取 CSV 并绘制各传感器位置。"""
    plot_sensor_locations(CSV_PATH)


if __name__ == "__main__":
    main()
