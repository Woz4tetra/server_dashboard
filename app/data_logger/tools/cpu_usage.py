from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass
from typing import Literal

import psutil

from app.data_logger.tools.from_dict import from_dict


@dataclass
class CpuData:
    timestamp: float
    utilization: float  # percent (0..100)
    memory_free: float  # in MiB
    memory_used: float  # in MiB
    temperature: float  # in degrees Celsius
    type: Literal["CpuData"] = "CpuData"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> CpuData:
        return from_dict(cls, data)


def cpu_usage() -> CpuData:
    cpu_percent = psutil.cpu_percent()
    virtual_memory = psutil.virtual_memory()
    temperature = psutil.sensors_temperatures()
    virtual_memory_free = virtual_memory.free / 1024**2
    virtual_memory_used = virtual_memory.used / 1024**2
    return CpuData(
        timestamp=datetime.datetime.now().timestamp(),
        utilization=cpu_percent,
        memory_used=virtual_memory_used,
        memory_free=virtual_memory_free,
        temperature=temperature["coretemp"][0].current,
    )


@dataclass
class CpuAggregatedData:
    timestamp: float
    time_span: float  # in seconds
    peak_utilization: float  # percent (0..100)
    peak_memory_used: float  # in MiB
    peak_memory_free: float  # in MiB
    peak_temperature: float  # in degrees Celsius
    type: Literal["CpuAggregatedData"] = "CpuAggregatedData"

    @classmethod
    def from_collection(cls, data: list[CpuData]) -> CpuAggregatedData:
        peak_utilization = max(data, key=lambda x: x.utilization).utilization
        peak_memory_used = max(data, key=lambda x: x.memory_used).memory_used
        peak_memory_free = min(data, key=lambda x: x.memory_free).memory_free
        peak_temperature = max(data, key=lambda x: x.temperature).temperature
        start_time = min(data, key=lambda x: x.timestamp).timestamp
        end_time = max(data, key=lambda x: x.timestamp).timestamp
        time_span = end_time - start_time
        return CpuAggregatedData(
            timestamp=datetime.datetime.now().timestamp(),
            peak_utilization=peak_utilization,
            peak_memory_used=peak_memory_used,
            peak_memory_free=peak_memory_free,
            peak_temperature=peak_temperature,
            time_span=time_span,
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> CpuAggregatedData:
        return from_dict(cls, data)
