from __future__ import annotations

import datetime
import threading
import time
from dataclasses import asdict, dataclass
from queue import Queue
from typing import Literal

import netifaces
import numpy as np

from app.data_logger.tools.from_dict import from_dict
from app.data_logger.tools.ping import ping


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


class NetworkHealthManager:
    def __init__(self, destination: str) -> None:
        self.destination = destination
        self.poll_thread = threading.Thread(target=self.poll, daemon=True)
        self.poll_thread.start()
        self.queue = Queue()

    def poll(self) -> None:
        while True:
            ping_time = ping(self.destination, timeout=5)
            self.queue.put(
                NetworkData(
                    timestamp=datetime.datetime.now().timestamp(),
                    destination=self.destination,
                    ping_ms=ping_time,
                )
            )
            time.sleep(1)

    def get_data(self) -> list[NetworkData]:
        data = []
        while not self.queue.empty():
            data.append(self.queue.get())
        return data


class MultiDestinationHealth:
    def __init__(self) -> None:
        self.local_health = NetworkHealthManager(self.get_router())
        self.internet_health = NetworkHealthManager("www.google.com")

    def get_router(self) -> str:
        gateways = netifaces.gateways()
        return list(gateways["default"].values())[0][0]

    def get_data(self) -> list[NetworkData]:
        return self.local_health.get_data() + self.internet_health.get_data()
