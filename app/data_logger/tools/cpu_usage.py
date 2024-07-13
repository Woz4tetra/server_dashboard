from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass
from typing import Literal

import numpy as np
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


def get_cpu_temperatures() -> list[float]:
    temp_sensors = psutil.sensors_temperatures()
    # the priority for CPU temp is as follows: coretemp sensor -> sensor with CPU in the label -> acpi -> k10temp
    if "coretemp" in temp_sensors:
        return [temp.current for temp in temp_sensors["coretemp"]]

    temperatures = []
    # iterate over all sensors
    for sensor in temp_sensors:
        # iterate over all temperatures in the current sensor
        for temp in temp_sensors[sensor]:
            if "CPU" in temp.label and temp.current != 0:
                temperatures.append(temp.current)
    if len(temperatures) == 0:
        for sensor in ["acpitz", "k10temp", "zenpower"]:
            if sensor in temp_sensors and temp_sensors[sensor][0].current != 0:
                temperatures.append(temp_sensors[sensor][0].current)
    return temperatures


def cpu_usage() -> CpuData:
    cpu_percent = psutil.cpu_percent()
    virtual_memory = psutil.virtual_memory()
    virtual_memory_free = virtual_memory.free / 1024**2
    virtual_memory_used = virtual_memory.used / 1024**2
    average_temperature = float(np.mean(get_cpu_temperatures()))
    return CpuData(
        timestamp=datetime.datetime.now().timestamp(),
        utilization=cpu_percent,
        memory_used=virtual_memory_used,
        memory_free=virtual_memory_free,
        temperature=average_temperature,
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
