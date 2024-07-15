from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass
from typing import Literal

import numpy as np

from app.shared.from_dict import from_dict


@dataclass
class NetworkData:
    timestamp: float
    destination: str
    ping_ms: float
    type: Literal["NetworkData"] = "NetworkData"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> NetworkData:
        return from_dict(cls, data)


@dataclass
class NetworkAggregatedData:
    timestamp: float
    time_span: float  # in seconds
    destination: str
    peak_ping: float  # in milliseconds
    percent_packet_loss: float  # percent (0..100)
    type: Literal["NetworkAggregatedData"] = "NetworkAggregatedData"

    @classmethod
    def from_collection(cls, data: list[NetworkData]) -> NetworkAggregatedData:
        # assumes all the same destination
        assert all(x.destination == data[0].destination for x in data)
        peak_ping = max(data, key=lambda x: x.ping_ms).ping_ms
        num_misses = np.isnan([x.ping_ms for x in data]).sum()
        num_hits = len(data) - num_misses
        percent_packet_loss = num_misses / num_hits * 100
        start_time = min(data, key=lambda x: x.timestamp).timestamp
        timestamp = datetime.datetime.now().timestamp()
        return NetworkAggregatedData(
            timestamp=timestamp,
            time_span=timestamp - start_time,
            destination=data[0].destination,
            peak_ping=peak_ping,
            percent_packet_loss=percent_packet_loss,
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> NetworkAggregatedData:
        return from_dict(cls, data)
