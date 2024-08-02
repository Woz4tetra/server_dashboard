from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass
from typing import Literal

import numpy as np

from app.shared.from_dict import from_dict


@dataclass
class GpuData:
    timestamp: float = 0.0  # Unix timestamp
    name: str = ""  # GPU name
    serial: str = ""  # GPU label serial number
    uuid: str = ""  # GPU UUID
    utilization_gpu: float = 0.0  # GPU utilization in percent (0..100)
    utilization_memory: float = 0.0  # Memory utilization in percent (0..100)
    memory_free: int = 0  # Free memory in MiB
    memory_used: int = 0  # Used memory in MiB
    temperature_gpu: float = 0.0  # GPU temperature in degrees Celsius
    power_draw: float = 0.0  # Power draw in watts
    type: Literal["GpuData"] = "GpuData"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> GpuData:
        return from_dict(cls, data)


@dataclass
class GpuAggregatedData:
    timestamp: float
    time_span: float = 0.0  # in seconds
    name: str = ""  # GPU name
    serial: str = ""  # GPU label serial number
    uuid: str = ""  # GPU UUID
    peak_utilization_gpu: float = 0.0  # in percent (0..100)
    peak_utilization_memory: float = 0.0  # in percent (0..100)
    peak_memory_free: int = 0  # in MiB
    peak_memory_used: int = 0  # in MiB
    peak_temperature_gpu: float = 0.0  # in degrees Celsius
    peak_power_draw: float = 0.0  # in watts
    average_utilization_gpu: float = 0.0  # in percent (0..100)
    average_utilization_memory: float = 0.0  # in percent (0..100)
    average_memory_free: int = 0  # in MiB
    average_memory_used: int = 0  # in MiB
    average_temperature_gpu: float = 0.0  # in degrees Celsius
    average_power_draw: float = 0.0  # in watts
    type: Literal["GpuAggregatedData"] = "GpuAggregatedData"

    @classmethod
    def from_collection(cls, data: list[GpuData]) -> GpuAggregatedData:
        # assumes all the same GPU
        assert all(x.uuid == data[0].uuid for x in data)
        timestamps = np.array([x.timestamp for x in data])
        utilization_gpu = np.array([x.utilization_gpu for x in data])
        utilization_memory = np.array([x.utilization_memory for x in data])
        memory_free = np.array([x.memory_free for x in data])
        memory_used = np.array([x.memory_used for x in data])
        temperature_gpu = np.array([x.temperature_gpu for x in data])
        power_draw = np.array([x.power_draw for x in data])

        peak_utilization_gpu = float(np.max(utilization_gpu))
        peak_utilization_memory = float(np.max(utilization_memory))
        peak_memory_free = int(np.min(memory_free))
        peak_memory_used = int(np.max(memory_used))
        peak_temperature_gpu = float(np.max(temperature_gpu))
        peak_power_draw = float(np.max(power_draw))

        average_utilization_gpu = float(np.mean(utilization_gpu))
        average_utilization_memory = float(np.mean(utilization_memory))
        average_memory_free = int(np.mean(memory_free))
        average_memory_used = int(np.mean(memory_used))
        average_temperature_gpu = float(np.mean(temperature_gpu))
        average_power_draw = float(np.mean(power_draw))

        start_time = float(np.min(timestamps))
        end_time = float(np.max(timestamps))

        return GpuAggregatedData(
            timestamp=end_time,
            time_span=end_time - start_time,
            name=data[0].name,
            serial=data[0].serial,
            uuid=data[0].uuid,
            peak_utilization_gpu=peak_utilization_gpu,
            peak_utilization_memory=peak_utilization_memory,
            peak_memory_free=peak_memory_free,
            peak_memory_used=peak_memory_used,
            peak_temperature_gpu=peak_temperature_gpu,
            peak_power_draw=peak_power_draw,
            average_utilization_gpu=average_utilization_gpu,
            average_utilization_memory=average_utilization_memory,
            average_memory_free=average_memory_free,
            average_memory_used=average_memory_used,
            average_temperature_gpu=average_temperature_gpu,
            average_power_draw=average_power_draw,
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> GpuAggregatedData:
        return from_dict(cls, data)
