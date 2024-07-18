import hashlib
import logging
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
from app.shared.constants import BULK_DATA, TODAYS_DATA, YESTERDAYS_DATA
from app.shared.types import DataImpl


@dataclass
class AggregatedData:
    cpu: list[CpuAggregatedData] = field(default_factory=list)
    gpu: dict[str, list[GpuAggregatedData]] = field(default_factory=dict)
    network: dict[str, list[NetworkAggregatedData]] = field(default_factory=dict)
    ups: list[UpsAggregatedData] = field(default_factory=list)
    data_hash: str = ""


@dataclass
class TodaysData:
    cpu: list[CpuData] = field(default_factory=list)
    gpu: dict[str, list[GpuData]] = field(default_factory=dict)
    network: dict[str, list[NetworkData]] = field(default_factory=dict)
    ups: list[UpsData] = field(default_factory=list)


def compute_md5_hash(fname: str) -> str:
    hash_md5 = hashlib.md5()
    hash_md5.update(open(fname, "rb").read())
    return hash_md5.hexdigest()


def did_bulk_data_change() -> bool:
    return compute_md5_hash(BULK_DATA) != load_bulk_cache().data_hash


@st.cache_data
def load_bulk_cache() -> AggregatedData:
    logger = logging.getLogger("frontend")
    all_lines = jsonlines.open(BULK_DATA)
    aggregate = AggregatedData()
    data = []
    for data_dict in all_lines:
        row = get_aggregate_class(data_dict).from_dict(data_dict)
        data.append(row)
    logger.debug(f"Loaded {len(data)} rows")
    grouped_by_type = group_by_type(data)

    aggregate.cpu = grouped_by_type.get("CpuAggregatedData", [])
    aggregate.gpu = group_by_key(grouped_by_type.get("GpuAggregatedData", []), "uuid")
    aggregate.network = group_by_key(
        grouped_by_type.get("NetworkAggregatedData", []), "destination"
    )
    aggregate.ups = grouped_by_type.get("UpsAggregatedData", [])
    aggregate.data_hash = compute_md5_hash(BULK_DATA)

    return aggregate


def load_bulk() -> AggregatedData:
    if did_bulk_data_change():
        load_bulk_cache.clear()
    return load_bulk_cache()


def did_yesterday_change() -> bool:
    return compute_md5_hash(YESTERDAYS_DATA) != load_yesterday()[1]


@st.cache_data
def load_yesterday() -> tuple[list[DataImpl], str]:
    logger = logging.getLogger("frontend")
    data = []
    for data_dict in jsonlines.open(YESTERDAYS_DATA):
        data.append(get_data_class(data_dict).from_dict(data_dict))
    logger.debug(f"Loaded {len(data)} rows from {YESTERDAYS_DATA}")
    return data, compute_md5_hash(YESTERDAYS_DATA)


@dataclass
class TodayCache:
    parsed_data: list[DataImpl] = field(default_factory=list)
    seek: int = 0


TODAY_DATA_CACHE = TodayCache()


def load_today_cache() -> list[DataImpl]:
    logger = logging.getLogger("frontend")
    with open(TODAYS_DATA, "rb") as file:
        file.seek(TODAY_DATA_CACHE.seek)
        data = []
        for data_dict in jsonlines.Reader(file):
            data.append(get_data_class(data_dict).from_dict(data_dict))
        TODAY_DATA_CACHE.seek = file.tell()
        TODAY_DATA_CACHE.parsed_data.extend(data)
        logger.debug(
            f"Loaded {len(data)} rows from {TODAYS_DATA}. Seek: {TODAY_DATA_CACHE.seek}"
        )
        return TODAY_DATA_CACHE.parsed_data


def parse_data_series(data: list) -> TodaysData:
    today = TodaysData()

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


def load_today() -> TodaysData:
    logger = logging.getLogger("frontend")
    global TODAY_DATA_CACHE
    if did_yesterday_change():
        logger.info("Yesterday's data changed, reloading today's data")
        TODAY_DATA_CACHE = TodayCache()
        load_yesterday.clear()
    yesterdays_data, file_hash = load_yesterday()
    todays_data = load_today_cache()

    return parse_data_series(yesterdays_data + todays_data)
