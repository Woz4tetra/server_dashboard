from datetime import datetime
from typing import get_args

from app.shared.types import AggregateImpl, DataImpl, DataType

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


def get_aggregate_class(data: dict) -> AggregateImpl:
    return get_aggregate_class_from_name(data["type"])


def get_aggregate_class_from_name(class_name: str) -> AggregateImpl:
    for cls in get_args(AggregateImpl):
        if cls.__name__ == class_name:
            return cls
    raise ValueError(f"Unknown aggregate class: {class_name}")


def group_by_day(data: list[DataType]) -> list[list[DataType]]:
    data_map: dict[int, list[DataType]] = {}
    now = datetime.now()
    for row in data:
        row_date = datetime.fromtimestamp(row.timestamp)
        row_delta = now - row_date
        key = int(row_delta.days)
        if key == 1:
            key = 0
        data_map.setdefault(key, []).append(row)
    grouped_data = list(data_map.values())
    grouped_dates = list(data_map.keys())
    grouped_dates = [row for timestamp, row in sorted(zip(grouped_dates, grouped_data))]
    return grouped_data


def group_by_type(data: list[DataType]) -> dict[str, list[DataType]]:
    groups = {}
    for row in data:
        groups.setdefault(row.__class__.__name__, []).append(row)
    return groups


def group_by_key(data: list[DataType], key: str) -> dict[str, list[DataType]]:
    groups = {}
    for row in data:
        groups.setdefault(getattr(row, key), []).append(row)
    return groups
