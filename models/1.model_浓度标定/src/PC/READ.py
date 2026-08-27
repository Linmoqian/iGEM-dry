import csv
from datetime import datetime
from pathlib import Path

import serial

from protocol import BAUD_RATE, parse_sensor_value

COM_PORT = "COM7"
CSV_PATH = Path("../../data/1.data_电子采集/light_sensor.csv")
is_Read = False


def main(port: str, csv_path: str | Path) -> None:
    """持续读取串口并将 ADC 原始值追加到 CSV。"""
    global is_Read

    csv_path = Path(csv_path)
    needs_header = not csv_path.exists() or csv_path.stat().st_size == 0

    try:
        with (
            serial.Serial(port, BAUD_RATE, timeout=1) as device,
            csv_path.open("a", newline="", encoding="utf-8") as csv_file,
        ):
            is_Read = True
            writer = csv.writer(csv_file)
            if needs_header:
                writer.writerow(["timestamp", "adc_raw"])

            while is_Read:
                try:
                    value = parse_sensor_value(device.readline())
                except (UnicodeDecodeError, ValueError):
                    continue
                if value is None:
                    continue

                timestamp = (
                    datetime.now().astimezone().isoformat(timespec="milliseconds")
                )
                writer.writerow([timestamp, value])
                csv_file.flush()
                print(f"{timestamp},{value}")
    except KeyboardInterrupt:
        print("\n[info] 已停止读取。")
    except serial.SerialException:
        print("[error] 未连接设备")
    finally:
        is_Read = False


if __name__ == "__main__":
    main(COM_PORT, CSV_PATH)
