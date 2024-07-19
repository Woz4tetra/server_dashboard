import shutil

import jsonlines

from app.shared.aggregate_utils import (
    AGGREGATE_MAPPING,
    get_aggregate_class_from_name,
    get_data_class,
    group_by_key,
    group_by_type,
)
from app.shared.types import AggregateImpl, DataImpl


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

    def bulk(self, data: list[DataImpl]) -> list[AggregateImpl]:
        grouped_by_type = group_by_type(data)
        cpu_data = {"cpu": grouped_by_type.get("CpuData", [])}
        gpu_data = group_by_key(grouped_by_type.get("GpuData", []), "uuid")
        network_data = group_by_key(
            grouped_by_type.get("NetworkData", []), "destination"
        )
        ups_data = {"ups": grouped_by_type.get("UpsData", [])}
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
            if len(data) == 0:
                continue
            aggregate_cls = get_aggregate_class_from_name(
                AGGREGATE_MAPPING[data[0].__class__.__name__]
            )
            aggregated_data.append(aggregate_cls.from_collection(data))  # type: ignore
        return aggregated_data

    def write_data(self, data: list[AggregateImpl]) -> None:
        with jsonlines.open(self.bulk_path, mode="a") as writer:
            for row in data:
                writer.write(row.to_dict())
