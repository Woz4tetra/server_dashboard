import json
import time
from dataclasses import dataclass, field
from io import BufferedReader
from queue import Queue
from threading import Lock, Thread
from typing import Generator

import jsonlines

from app.shared_data import (
    CpuAggregatedData,
    CpuData,
    GpuAggregatedData,
    GpuData,
    NetworkAggregatedData,
    NetworkData,
    UpsAggregatedData,
    UpsData,
)
from app.shared_data.aggregate_utils import (
    get_aggregate_class,
    get_data_class,
    group_by_key,
    group_by_type,
)
from app.shared_data.constants import BULK_DATA, TODAYS_DATA


def follow(fp: BufferedReader) -> Generator[bytes, None, None]:
    """generator function that yields new lines in a file"""

    while True:
        line = fp.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line


def follow_task(fp: BufferedReader, queue: Queue, lock: Lock) -> None:
    for line in follow(fp):
        with lock:
            queue.put(line)


@dataclass
class AggregatedData:
    cpu: list[CpuAggregatedData] = field(default_factory=list)
    gpu: dict[str, list[GpuAggregatedData]] = field(default_factory=dict)
    network: dict[str, list[NetworkAggregatedData]] = field(default_factory=dict)
    ups: dict[str, list[UpsAggregatedData]] = field(default_factory=dict)


def load_bulk() -> AggregatedData:
    all_lines = jsonlines.open(BULK_DATA)
    aggregate = AggregatedData()
    data = []
    for data_dict in all_lines:
        row = get_aggregate_class(data_dict).from_dict(data_dict)
        data.append(row)
    grouped_by_type = group_by_type(data)

    aggregate.cpu = grouped_by_type.get("CpuAggregatedData", [])
    aggregate.gpu = group_by_key(grouped_by_type.get("GpuAggregatedData", []), "uuid")
    aggregate.network = group_by_key(
        grouped_by_type.get("NetworkAggregatedData", []), "destination"
    )
    aggregate.ups = group_by_key(grouped_by_type.get("UpsAggregatedData", []), "serial")

    return aggregate


class DataVacuum:
    def __init__(self) -> None:
        self.cpu_data: list[CpuData] = []
        self.gpu_data: dict[str, list[GpuData]] = {}
        self.network_data: dict[str, list[NetworkData]] = {}
        self.ups_data: dict[str, list[UpsData]] = {}

        fp = open(TODAYS_DATA, "rb")
        self.line_queue: Queue[bytes] = Queue()
        self.data_lock = Lock()
        follow_thread = Thread(
            target=follow_task, args=(fp, self.line_queue, self.data_lock), daemon=True
        )
        follow_thread.start()

    def wait_for_data(self) -> None:
        while self.line_queue.empty():
            time.sleep(0.1)

    def update(self) -> None:
        self.wait_for_data()
        data = []
        with self.data_lock:
            while not self.line_queue.empty():
                line = self.line_queue.get()
                try:
                    data_dict = json.loads(line)
                except json.JSONDecodeError:
                    continue
                row = get_data_class(data_dict).from_dict(data_dict)
                data.append(row)
        print(f"Updating with {len(data)} records")

        grouped_by_type = group_by_type(data)

        self.cpu_data.extend(grouped_by_type.get("CpuData", []))

        gpu_data_by_key = group_by_key(grouped_by_type.get("GpuData", []), "uuid")
        for key, value in gpu_data_by_key.items():
            self.gpu_data.setdefault(key, []).extend(value)  # type: ignore

        network_data_by_key = group_by_key(
            grouped_by_type.get("NetworkData", []), "destination"
        )
        for key, value in network_data_by_key.items():
            self.network_data.setdefault(key, []).extend(value)  # type: ignore

        ups_data_by_key = group_by_key(grouped_by_type.get("UpsData", []), "serial")
        for key, value in ups_data_by_key.items():
            self.ups_data.setdefault(key, []).extend(value)  # type: ignore
