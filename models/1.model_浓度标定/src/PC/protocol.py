BAUD_RATE = 115200


def parse_sensor_value(raw_line: bytes) -> int | None:
    """解析 ESP32 发送的单行 ADC 原始值。"""
    line = raw_line.decode("ascii").strip()
    return int(line) if line else None
