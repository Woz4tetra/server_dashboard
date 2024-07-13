import datetime
import subprocess

from app.shared_data.gpu_data import GpuData


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
