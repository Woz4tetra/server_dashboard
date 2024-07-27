from __future__ import annotations
import numpy as np
import datetime
from dataclasses import asdict, dataclass
from typing import Literal

from app.shared.from_dict import from_dict


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


@dataclass
class CpuAggregatedData:
    timestamp: float
    time_span: float  # in seconds
    peak_utilization: float  # percent (0..100)
    peak_memory_used: float  # in MiB
    peak_memory_free: float  # in MiB
    peak_temperature: float  # in degrees Celsius
    average_utilization: float  # percent (0..100)
    average_memory_used: float  # in MiB
    average_memory_free: float  # in MiB
    average_temperature: float  # in degrees Celsius
    type: Literal["CpuAggregatedData"] = "CpuAggregatedData"

    @classmethod
    def from_collection(cls, data: list[CpuData]) -> CpuAggregatedData:
        utilization = np.array([x.utilization for x in data])
        memory_used = np.array([x.memory_used for x in data])
        memory_free = np.array([x.memory_free for x in data])
        temperature = np.array([x.temperature for x in data])

        peak_utilization = np.max(utilization)
        peak_memory_used = np.max(memory_used)
        peak_memory_free = np.max(memory_free)
        peak_temperature = np.max(temperature)

        average_utilization = np.mean(utilization)
        average_memory_used = np.mean(memory_used)
        average_memory_free = np.mean(memory_free)
        average_temperature = np.mean(temperature)

        start_time = min(data, key=lambda x: x.timestamp).timestamp
        end_time = max(data, key=lambda x: x.timestamp).timestamp
        time_span = end_time - start_time

        return CpuAggregatedData(
            timestamp=datetime.datetime.now().timestamp(),
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
