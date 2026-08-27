import csv
import sys
from datetime import datetime
from pathlib import Path

import serial

from protocol import BAUD_RATE, parse_sensor_value

DEFAULT_CSV_PATH = Path("light_sensor.csv")


def main() -> None:
    """持续读取串口并将 ADC 原始值追加到 CSV。"""
    if len(sys.argv) < 2:
        raise SystemExit("用法: python READ.py <串口> [CSV 文件]")

    port = sys.argv[1]
    csv_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CSV_PATH
    needs_header = not csv_path.exists() or csv_path.stat().st_size == 0

    try:
        with (
            serial.Serial(port, BAUD_RATE, timeout=1) as device,
            csv_path.open("a", newline="", encoding="utf-8") as csv_file,
        ):
            writer = csv.writer(csv_file)
            if needs_header:
                writer.writerow(["timestamp", "adc_raw"])

            while True:
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
        print("\n[信息] 已停止读取。")


if __name__ == "__main__":
    main()
