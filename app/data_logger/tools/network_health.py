import datetime
import threading
import time
from queue import Queue

import netifaces

from app.data_logger.tools.ping import ping
from app.shared.network_data import NetworkData


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
