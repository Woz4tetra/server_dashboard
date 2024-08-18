from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

import numpy as np

from app.shared.from_dict import from_dict


@dataclass
class UpsData:
    timestamp: float = 0.0
    serial: str = ""
    line_voltage: float = 0.0
    status: str = ""
    load_percent: float = 0.0
    battery_voltage: float = 0.0
    battery_percent: float = 0.0
    output_current: float = 0.0
    output_voltage: float = 0.0
    type: Literal["UpsData"] = "UpsData"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> UpsData:
        return from_dict(cls, data)


@dataclass
class UpsAggregatedData:
    timestamp: float = 0.0
    time_span: float = 0.0
    serial: str = ""
    up_percentage: float = 0.0
    peak_line_voltage: float = 0.0
    peak_load_percent: float = 0.0
    peak_battery_voltage: float = 0.0
    peak_battery_percent: float = 0.0
    peak_output_current: float = 0.0
    peak_output_voltage: float = 0.0
    average_line_voltage: float = 0.0
    average_load_percent: float = 0.0
    average_battery_voltage: float = 0.0
    average_battery_percent: float = 0.0
    average_output_current: float = 0.0
    average_output_voltage: float = 0.0
    type: Literal["UpsAggregatedData"] = "UpsAggregatedData"

    @classmethod
    def from_collection(cls, data: list[UpsData]) -> UpsAggregatedData:
        # assumes all the same UPS
        timestamps = np.array([x.timestamp for x in data])
        line_voltage = np.array([x.line_voltage for x in data])
        load_percent = np.array([x.load_percent for x in data])
        battery_voltage = np.array([x.battery_voltage for x in data])
        battery_percent = np.array([x.battery_percent for x in data])
        output_current = np.array([x.output_current for x in data])
        output_voltage = np.array([x.output_voltage for x in data])

        peak_line_voltage = float(np.max(line_voltage))
        peak_load_percent = float(np.max(load_percent))
        peak_battery_voltage = float(np.max(battery_voltage))
        peak_battery_percent = float(np.max(battery_percent))
        peak_output_current = float(np.max(output_current))
        peak_output_voltage = float(np.max(output_voltage))

        average_line_voltage = float(np.mean(line_voltage))
        average_load_percent = float(np.mean(load_percent))
        average_battery_voltage = float(np.mean(battery_voltage))
        average_battery_percent = float(np.mean(battery_percent))
        average_output_current = float(np.mean(output_current))
        average_output_voltage = float(np.mean(output_voltage))

        start_time = float(np.min(timestamps))
        end_time = float(np.max(timestamps))

        up_percentage = sum(x.status == "ONLINE" for x in data) / len(data) * 100

        return UpsAggregatedData(
            timestamp=end_time,
            time_span=end_time - start_time,
            serial=data[0].serial,
            up_percentage=up_percentage,
            peak_line_voltage=peak_line_voltage,
            peak_load_percent=peak_load_percent,
            peak_battery_voltage=peak_battery_voltage,
            peak_battery_percent=peak_battery_percent,
            peak_output_current=peak_output_current,
            peak_output_voltage=peak_output_voltage,
            average_line_voltage=average_line_voltage,
            average_load_percent=average_load_percent,
            average_battery_voltage=average_battery_voltage,
            average_battery_percent=average_battery_percent,
            average_output_current=average_output_current,
            average_output_voltage=average_output_voltage,
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> UpsAggregatedData:
        return from_dict(cls, data)
