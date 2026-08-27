"""
Created on 2026-08-27
Updated on 2026-08-27
@author: https://github.com/Linmoqian
"""

from __future__ import annotations

import csv
from pathlib import Path

import serial

from protocol import BAUD_RATE, CSV_FIELDS, parse_sensor_data

COM_PORT = "COM7"
CSV_PATH = Path(__file__).resolve().parents[3] / "data/2.data_时空浓度/sensor_gps.csv"
is_Read = False


def main(port: str, csv_path: str | Path) -> None:
    """读取串口数据并追加到 CSV。"""
    global is_Read

    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not csv_path.exists() or csv_path.stat().st_size == 0

    try:
        with (
            serial.Serial(port, BAUD_RATE, timeout=1) as device,
            csv_path.open("a", newline="", encoding="utf-8") as csv_file,
        ):
            is_Read = True
            writer = csv.writer(csv_file)
            if needs_header:
                writer.writerow(CSV_FIELDS)

            while is_Read:
                try:
                    row = parse_sensor_data(device.readline())
                except (UnicodeDecodeError, ValueError):
                    continue
                if row is None:
                    continue

                writer.writerow(row)
                csv_file.flush()
                print(",".join(row))
    except KeyboardInterrupt:
        print("\n[info] 已停止读取。")
    except serial.SerialException:
        print("[error] 未连接设备")
    finally:
        is_Read = False


if __name__ == "__main__":
    main(COM_PORT, CSV_PATH)
