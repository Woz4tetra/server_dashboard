from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass
from typing import Literal

from app.shared_data.from_dict import from_dict


@dataclass
class GpuData:
    timestamp: float  # Unix timestamp
    name: str  # GPU name
    serial: str  # GPU label serial number
    uuid: str  # GPU UUID
    utilization_gpu: float  # GPU utilization in percent (0..100)
    utilization_memory: float  # Memory utilization in percent (0..100)
    memory_free: int  # Free memory in MiB
    memory_used: int  # Used memory in MiB
    temperature_gpu: float  # GPU temperature in degrees Celsius
    power_draw: float  # Power draw in watts
    type: Literal["GpuData"] = "GpuData"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> GpuData:
        return from_dict(cls, data)


@dataclass
class GpuAggregatedData:
    timestamp: float
    time_span: float  # in seconds
    name: str  # GPU name
    serial: str  # GPU label serial number
    uuid: str  # GPU UUID
    peak_utilization_gpu: float  # in percent (0..100)
    peak_utilization_memory: float  # in percent (0..100)
    peak_memory_free: int  # in MiB
    peak_memory_used: int  # in MiB
    peak_temperature_gpu: float  # in degrees Celsius
    peak_power_draw: float  # in watts
    type: Literal["GpuAggregatedData"] = "GpuAggregatedData"

    @classmethod
    def from_collection(cls, data: list[GpuData]) -> GpuAggregatedData:
        # assumes all the same GPU
        assert all(x.uuid == data[0].uuid for x in data)
        peak_utilization_gpu = max(
            data, key=lambda x: x.utilization_gpu
        ).utilization_gpu
        peak_utilization_memory = max(
            data, key=lambda x: x.utilization_memory
        ).utilization_memory
        peak_memory_free = min(data, key=lambda x: x.memory_free).memory_free
        peak_memory_used = max(data, key=lambda x: x.memory_used).memory_used
        peak_temperature_gpu = max(
            data, key=lambda x: x.temperature_gpu
        ).temperature_gpu
        peak_power_draw = max(data, key=lambda x: x.power_draw).power_draw
        start_time = min(data, key=lambda x: x.timestamp).timestamp
        timestamp = datetime.datetime.now().timestamp()
        return GpuAggregatedData(
            timestamp=timestamp,
            time_span=timestamp - start_time,
            name=data[0].name,
            serial=data[0].serial,
            uuid=data[0].uuid,
            peak_utilization_gpu=peak_utilization_gpu,
            peak_utilization_memory=peak_utilization_memory,
            peak_memory_free=peak_memory_free,
            peak_memory_used=peak_memory_used,
            peak_temperature_gpu=peak_temperature_gpu,
            peak_power_draw=peak_power_draw,
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> GpuAggregatedData:
        return from_dict(cls, data)
