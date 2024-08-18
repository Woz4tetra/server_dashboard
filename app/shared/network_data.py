from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

import numpy as np

from app.shared.from_dict import from_dict


@dataclass
class NetworkData:
    timestamp: float = 0.0
    destination: str = ""
    ping_ms: float = 0.0
    type: Literal["NetworkData"] = "NetworkData"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> NetworkData:
        return from_dict(cls, data)


@dataclass
class NetworkAggregatedData:
    timestamp: float = 0.0
    time_span: float = 0.0  # in seconds
    destination: str = ""
    peak_ping: float = 0  # in milliseconds
    percent_packet_loss: float = 0.0  # percent (0..100)
    num_pings: int = 0
    num_hits: int = 0
    type: Literal["NetworkAggregatedData"] = "NetworkAggregatedData"

    @classmethod
    def from_collection(cls, data: list[NetworkData]) -> NetworkAggregatedData:
        # assumes all the same destination
        assert all(x.destination == data[0].destination for x in data)
        timestamps = np.array([x.timestamp for x in data])
        peak_ping = max(data, key=lambda x: x.ping_ms).ping_ms
        num_misses = int(np.isnan([x.ping_ms for x in data]).sum())
        num_pings = len(data)
        num_hits = num_pings - num_misses
        percent_packet_loss = num_misses / num_hits * 100
        start_time = min(data, key=lambda x: x.timestamp).timestamp

        start_time = float(np.min(timestamps))
        end_time = float(np.max(timestamps))

        return NetworkAggregatedData(
            timestamp=end_time,
            time_span=end_time - start_time,
            destination=data[0].destination,
            peak_ping=peak_ping,
            percent_packet_loss=percent_packet_loss,
            num_pings=num_pings,
            num_hits=num_hits,
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> NetworkAggregatedData:
        return from_dict(cls, data)
