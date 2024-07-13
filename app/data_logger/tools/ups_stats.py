from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass
from typing import Literal

from apcaccess import status as apc
from dateutil.parser import parse as date_parse

from app.data_logger.tools.from_dict import from_dict


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
    peak_line_voltage: float
    peak_load_percent: float
    peak_battery_voltage: float
    peak_battery_percent: float
    peak_output_current: float
    type: Literal["UpsAggregatedData"] = "UpsAggregatedData"

    @classmethod
    def from_collection(cls, data: list[UpsData]) -> UpsAggregatedData:
        # assumes all the same UPS
        assert all(x.serial == data[0].serial for x in data)
        peak_line_voltage = max(data, key=lambda x: x.line_voltage).line_voltage
        peak_load_percent = max(data, key=lambda x: x.load_percent).load_percent
        peak_battery_voltage = max(
            data, key=lambda x: x.battery_voltage
        ).battery_voltage
        peak_battery_percent = max(
            data, key=lambda x: x.battery_percent
        ).battery_percent
        peak_output_current = max(data, key=lambda x: x.output_current).output_current
        start_time = min(data, key=lambda x: x.timestamp).timestamp
        timestamp = datetime.datetime.now().timestamp()
        return UpsAggregatedData(
            timestamp=timestamp,
            time_span=timestamp - start_time,
            serial=data[0].serial,
            peak_line_voltage=peak_line_voltage,
            peak_load_percent=peak_load_percent,
            peak_battery_voltage=peak_battery_voltage,
            peak_battery_percent=peak_battery_percent,
            peak_output_current=peak_output_current,
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> UpsAggregatedData:
        return from_dict(cls, data)


def ups_stats() -> UpsData | None:
    try:
        result = apc.parse(apc.get(), strip_units=True)
    except ConnectionRefusedError:
        return None

    date_str = result["DATE"]
    date = date_parse(date_str)
    return UpsData(
        timestamp=date.timestamp(),
        serial=result["APC"],
        line_voltage=result["LINEV"],
        status=result["STATUS"],
        load_percent=result["LOADPCT"],
        battery_voltage=result["BATTV"],
        battery_percent=result["BCHARGE"],
        output_current=result["OUTCURNT"],
    )
