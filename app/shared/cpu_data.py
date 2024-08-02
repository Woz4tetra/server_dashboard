from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass
from typing import Literal

import numpy as np

from app.shared.from_dict import from_dict


@dataclass
class CpuData:
    timestamp: float = 0.0
    utilization: float = 0.0  # percent (0..100)
    memory_free: float = 0.0  # in MiB
    memory_used: float = 0.0  # in MiB
    temperature: float = 0.0  # in degrees Celsius
    type: Literal["CpuData"] = "CpuData"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> CpuData:
        return from_dict(cls, data)


@dataclass
class CpuAggregatedData:
    timestamp: float
    time_span: float = 0.0  # in seconds
    peak_utilization: float = 0.0  # percent (0..100)
    peak_memory_used: float = 0.0  # in MiB
    peak_memory_free: float = 0.0  # in MiB
    peak_temperature: float = 0.0  # in degrees Celsius
    average_utilization: float = 0.0  # percent (0..100)
    average_memory_used: float = 0.0  # in MiB
    average_memory_free: float = 0.0  # in MiB
    average_temperature: float = 0.0  # in degrees Celsius
    type: Literal["CpuAggregatedData"] = "CpuAggregatedData"

    @classmethod
    def from_collection(cls, data: list[CpuData]) -> CpuAggregatedData:
        timestamps = np.array([x.timestamp for x in data])
        utilization = np.array([x.utilization for x in data])
        memory_used = np.array([x.memory_used for x in data])
        memory_free = np.array([x.memory_free for x in data])
        temperature = np.array([x.temperature for x in data])

        peak_utilization = float(np.max(utilization))
        peak_memory_used = float(np.max(memory_used))
        peak_memory_free = float(np.max(memory_free))
        peak_temperature = float(np.max(temperature))

        average_utilization = float(np.mean(utilization))
        average_memory_used = float(np.mean(memory_used))
        average_memory_free = float(np.mean(memory_free))
        average_temperature = float(np.mean(temperature))

        start_time = float(np.min(timestamps))
        end_time = float(np.max(timestamps))

        time_span = end_time - start_time

        return CpuAggregatedData(
            timestamp=end_time,
            peak_utilization=peak_utilization,
            peak_memory_used=peak_memory_used,
            peak_memory_free=peak_memory_free,
            peak_temperature=peak_temperature,
            average_utilization=average_utilization,
            average_memory_used=average_memory_used,
            average_memory_free=average_memory_free,
            average_temperature=average_temperature,
            time_span=time_span,
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> CpuAggregatedData:
        return from_dict(cls, data)
