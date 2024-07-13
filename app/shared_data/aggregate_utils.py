from typing import get_args

from app.shared_data.types import AggregateImpl, DataImpl

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


def group_by_type(data: list[DataImpl]) -> dict[str, list[DataImpl]]:
    groups = {}
    for row in data:
        groups.setdefault(row.__class__.__name__, []).append(row)
    return groups


def group_by_key(data: list[DataImpl], key: str) -> dict[str, list[DataImpl]]:
    groups = {}
    for row in data:
        groups.setdefault(getattr(row, key), []).append(row)
    return groups
