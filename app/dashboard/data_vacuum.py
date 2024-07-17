from dataclasses import dataclass, field

import jsonlines
import streamlit as st

from app.shared import (
    CpuAggregatedData,
    CpuData,
    GpuAggregatedData,
    GpuData,
    NetworkAggregatedData,
    NetworkData,
    UpsAggregatedData,
    UpsData,
)
from app.shared.aggregate_utils import (
    get_aggregate_class,
    get_data_class,
    group_by_key,
    group_by_type,
)
from app.shared.constants import BULK_DATA, TODAYS_DATA, TODAYS_DATA_BACKUP


@dataclass
class AggregatedData:
    cpu: list[CpuAggregatedData] = field(default_factory=list)
    gpu: dict[str, list[GpuAggregatedData]] = field(default_factory=dict)
    network: dict[str, list[NetworkAggregatedData]] = field(default_factory=dict)
    ups: list[UpsAggregatedData] = field(default_factory=list)


@dataclass
class TodaysData:
    cpu: list[CpuData] = field(default_factory=list)
    gpu: dict[str, list[GpuData]] = field(default_factory=dict)
    network: dict[str, list[NetworkData]] = field(default_factory=dict)
    ups: list[UpsData] = field(default_factory=list)


@st.cache_data
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
    aggregate.ups = grouped_by_type.get("UpsAggregatedData", [])

    return aggregate


@st.cache_data
def load_today() -> TodaysData:
    today = TodaysData()
    data = []
    for data_dict in jsonlines.open(TODAYS_DATA_BACKUP):
        data.append(get_data_class(data_dict).from_dict(data_dict))
    for data_dict in jsonlines.open(TODAYS_DATA):
        data.append(get_data_class(data_dict).from_dict(data_dict))

    grouped_by_type = group_by_type(data)

    today.cpu.extend(grouped_by_type.get("CpuData", []))

    gpu_data_by_key = group_by_key(grouped_by_type.get("GpuData", []), "uuid")
    for key, value in gpu_data_by_key.items():
        today.gpu.setdefault(key, []).extend(value)  # type: ignore

    network_data_by_key = group_by_key(
        grouped_by_type.get("NetworkData", []), "destination"
    )
    for key, value in network_data_by_key.items():
        today.network.setdefault(key, []).extend(value)  # type: ignore

    today.ups.extend(grouped_by_type.get("UpsData", []))

    return today
