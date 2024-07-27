from __future__ import annotations
import numpy as np
import datetime
from dataclasses import asdict, dataclass
from typing import Literal

from app.shared.from_dict import from_dict


@dataclass
class UpsData:
    timestamp: float
    serial: str
    line_voltage: float
    status: str
    load_percent: float
    battery_voltage: float
    battery_percent: float
    output_current: float
    output_voltage: float
    type: Literal["UpsData"] = "UpsData"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> UpsData:
        return from_dict(cls, data)


@dataclass
class UpsAggregatedData:
    timestamp: float
    time_span: float
    serial: str
    up_percentage: float
    peak_line_voltage: float
    peak_load_percent: float
    peak_battery_voltage: float
    peak_battery_percent: float
    peak_output_current: float
    peak_output_voltage: float
    average_line_voltage: float
    average_load_percent: float
    average_battery_voltage: float
    average_battery_percent: float
    average_output_current: float
    average_output_voltage: float
    type: Literal["UpsAggregatedData"] = "UpsAggregatedData"

    @classmethod
    def from_collection(cls, data: list[UpsData]) -> UpsAggregatedData:
        # assumes all the same UPS
        line_voltage = np.array([x.line_voltage for x in data])
        load_percent = np.array([x.load_percent for x in data])
        battery_voltage = np.array([x.battery_voltage for x in data])
        battery_percent = np.array([x.battery_percent for x in data])
        output_current = np.array([x.output_current for x in data])
        output_voltage = np.array([x.output_voltage for x in data])

        peak_line_voltage = np.max(line_voltage)
        peak_load_percent = np.max(load_percent)
        peak_battery_voltage = np.max(battery_voltage)
        peak_battery_percent = np.max(battery_percent)
        peak_output_current = np.max(output_current)
        peak_output_voltage = np.max(output_voltage)

        average_line_voltage = np.mean(line_voltage)
        average_load_percent = np.mean(load_percent)
        average_battery_voltage = np.mean(battery_voltage)
        average_battery_percent = np.mean(battery_percent)
        average_output_current = np.mean(output_current)

        timestamp = datetime.datetime.now().timestamp()
        start_time = min(data, key=lambda x: x.timestamp).timestamp
        time_span = timestamp - start_time

        up_percentage = sum(x.status == "ONLINE" for x in data) / len(data) * 100

        return UpsAggregatedData(
            timestamp=timestamp,
            time_span=time_span,
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
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> UpsAggregatedData:
        return from_dict(cls, data)
