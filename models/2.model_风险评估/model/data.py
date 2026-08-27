"""
Created on 2026-08-27
Updated on 2026-08-27
@author: https://github.com/Linmoqian
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SensorData:
    sensor_id: str
    device_uptime_ms: int
    gps_valid: bool
    latitude_deg: float | None
    longitude_deg: float | None

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "SensorData":
        return cls(
            sensor_id=row["sensor_id"],
            device_uptime_ms=int(row["device_uptime_ms"]),
            gps_valid=row["gps_valid"] == "1",
            latitude_deg=float(row["latitude_deg"]) if row["latitude_deg"] else None,
            longitude_deg=float(row["longitude_deg"]) if row["longitude_deg"] else None,
        )


def read_sensor_data(csv_path: str | Path) -> list[SensorData]:
    with Path(csv_path).open(newline="", encoding="utf-8") as csv_file:
        return [SensorData.from_row(row) for row in csv.DictReader(csv_file)]
