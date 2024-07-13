import shutil
from typing import Iterable, Union, get_args

import jsonlines

from app.data_logger.tools.cpu_usage import CpuAggregatedData, CpuData
from app.data_logger.tools.network_health import NetworkAggregatedData, NetworkData
from app.data_logger.tools.nvidia_smi import GpuAggregatedData, GpuData
from app.data_logger.tools.ups_stats import UpsAggregatedData, UpsData

DataImpl = Union[
    CpuData,
    NetworkData,
    GpuData,
    UpsData,
]

AggregateImpl = Union[
    CpuAggregatedData,
    NetworkAggregatedData,
    GpuAggregatedData,
    UpsAggregatedData,
]

AGGREGATE_MAPPING: dict[str, str] = {
    "CpuData": "CpuAggregatedData",
    "NetworkData": "NetworkAggregatedData",
    "GpuData": "GpuAggregatedData",
    "UpsData": "UpsAggregatedData",
}


def get_data_class(data: dict) -> DataImpl:
    for cls in get_args(DataImpl):
        if cls.__name__ == data["type"]:
            return cls
    raise ValueError(f"Unknown data type: {data['type']}")


def get_aggregate_class(class_name: str) -> AggregateImpl:
    for cls in get_args(AggregateImpl):
        if cls.__name__ == class_name:
            return cls
    raise ValueError(f"Unknown aggregate class: {class_name}")


class BulkStatsLogger:
    def __init__(self, data_path: str, bulk_path: str) -> None:
        self.data_path = data_path
        self.bulk_path = bulk_path

    def make_backup(self) -> None:
        shutil.copy(self.data_path, self.data_path + ".bak")

    def clear_data(self) -> None:
        with open(self.data_path, "w") as f:
            f.write("")

    def read_data(self) -> list[DataImpl]:
        with jsonlines.open(self.data_path) as reader:
            return [get_data_class(row).from_dict(row) for row in reader]

    def group_by_type(self, data: list[DataImpl]) -> dict[str, list[DataImpl]]:
        groups = {}
        for row in data:
            groups.setdefault(row.__class__.__name__, []).append(row)
        return groups

    def group_by_key(self, data: list[DataImpl], key: str) -> dict[str, list[DataImpl]]:
        groups = {}
        for row in data:
            groups.setdefault(getattr(row, key), []).append(row)
        return groups

    def bulk(self, data: list[DataImpl]) -> list[AggregateImpl]:
        grouped_by_type = self.group_by_type(data)
        cpu_data = {"cpu": grouped_by_type.get("CpuData", [])}
        gpu_data = self.group_by_key(grouped_by_type.get("GpuData", []), "uuid")
        network_data = self.group_by_key(
            grouped_by_type.get("NetworkData", []), "destination"
        )
        ups_data = self.group_by_key(grouped_by_type.get("UpsData", []), "serial")
        return (
            self.aggregate(cpu_data)
            + self.aggregate(gpu_data)
            + self.aggregate(network_data)
            + self.aggregate(ups_data)
        )

    def aggregate(
        self, grouped_by_key: dict[str, list[DataImpl]]
    ) -> list[AggregateImpl]:
        if len(grouped_by_key) == 0:
            return []
        aggregated_data = []
        for data in grouped_by_key.values():
            aggregate_cls = get_aggregate_class(
                AGGREGATE_MAPPING[data[0].__class__.__name__]
            )
            aggregated_data.append(aggregate_cls.from_collection(data))  # type: ignore
        return aggregated_data

    def write_data(self, data: list[AggregateImpl]) -> None:
        with jsonlines.open(self.bulk_path, mode="a") as writer:
            for row in data:
                writer.write(row.to_dict())
