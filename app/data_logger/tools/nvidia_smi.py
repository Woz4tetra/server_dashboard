from __future__ import annotations

import datetime
import subprocess
from dataclasses import asdict, dataclass
from typing import Literal

from app.data_logger.tools.from_dict import from_dict


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


def parse_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return float("nan")


class NvidiaSmiManager:
    def __init__(self, poll_interval: float) -> None:
        self.poll_interval = poll_interval

        poll_interval_ms = int(self.poll_interval * 1000)
        command = [
            "nvidia-smi",
            f"-lms={poll_interval_ms}",
            "--query-gpu="
            "timestamp,"
            "name,"
            "serial,"
            "uuid,"
            "utilization.gpu,"
            "utilization.memory,"
            "memory.free,"
            "memory.used,"
            "temperature.gpu,"
            "power.draw",
            "--format=csv,noheader,nounits",
        ]
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE)
        self.gpu_count = self.get_gpu_count()

    def get_gpu_count(self) -> int:
        process = subprocess.Popen(
            ["nvidia-smi", "--query-gpu=uuid", "--format=csv,noheader,nounits"],
            stdout=subprocess.PIPE,
        )
        stdout = process.communicate()[0]
        return len(stdout.decode().strip().splitlines())

    def get_data(self) -> list[GpuData]:
        if self.process.stdout is None:
            raise ValueError("Process not started")
        all_data = []
        for _ in range(self.gpu_count):
            line = self.process.stdout.readline()
            values = line.decode().strip().split(", ")
            date_str = values[0]
            date = datetime.datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S.%f")
            data = GpuData(
                timestamp=date.timestamp(),
                name=values[1],
                serial=values[2],
                uuid=values[3],
                utilization_gpu=parse_float(values[4]),
                utilization_memory=parse_float(values[5]),
                memory_free=int(values[6]),
                memory_used=int(values[7]),
                temperature_gpu=parse_float(values[8]),
                power_draw=parse_float(values[9]),
            )
            all_data.append(data)
        return all_data


NVIDIA_SMI_MANAGER = NvidiaSmiManager(poll_interval=1.0)


def nvidia_smi() -> list[GpuData]:
    return NVIDIA_SMI_MANAGER.get_data()
