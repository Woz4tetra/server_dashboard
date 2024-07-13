import asyncio
import logging

import jsonlines

from app.data_logger.tools.cpu_usage import cpu_usage
from app.data_logger.tools.data_interface import DataInterface
from app.data_logger.tools.network_health import MultiDestinationHealth
from app.data_logger.tools.nvidia_smi import nvidia_smi
from app.data_logger.tools.ups_stats import ups_stats


class TodayLogger:
    def __init__(self, data_path: str) -> None:
        self.data_queue: asyncio.Queue[DataInterface] = asyncio.Queue()
        self.data_path = data_path
        self.logger = logging.getLogger("data_logger")

    async def poll_cpu(self) -> None:
        while True:
            data = cpu_usage()
            await self.data_queue.put(data)
            await asyncio.sleep(1)

    async def poll_gpu(self) -> None:
        while True:
            data = nvidia_smi()
            for row in data:
                await self.data_queue.put(row)
            await asyncio.sleep(1)

    async def poll_network(self) -> None:
        net_health = MultiDestinationHealth()
        while True:
            data = net_health.get_data()
            for row in data:
                await self.data_queue.put(row)
            await asyncio.sleep(1)

    async def poll_ups(self) -> None:
        while True:
            data = ups_stats()
            if data is not None:
                await self.data_queue.put(data)
            await asyncio.sleep(60)

    async def write_data(self) -> None:
        while True:
            with jsonlines.open(self.data_path, mode="a") as writer:
                data = await self.data_queue.get()
                writer.write(data.to_dict())
                self.logger.debug(f"Wrote data: {type(data)}")
