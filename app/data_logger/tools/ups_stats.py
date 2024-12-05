import logging
import os
import time
from datetime import datetime
from queue import Queue
from threading import Thread

from apcaccess import status as apc
from dateutil.parser import parse as date_parse

from app.shared.ups_data import UpsData


def restart_ups_service() -> None:
    os.system("sudo systemctl restart apcupsd.service")


def bad_data(date: datetime, result: dict[str, str]) -> UpsData:
    return UpsData(
        timestamp=date.timestamp(),
        serial=result.get("APC", ""),
        line_voltage=0.0,
        status="BAD DATA",
        load_percent=0.0,
        battery_voltage=0.0,
        battery_percent=0.0,
        output_current=0.0,
        output_voltage=0.0,
    )


class UpsPollThread:
    def __init__(self, poll_delay: float, stale_threshold: float) -> None:
        self.task = Thread(target=self.poll, daemon=True)
        self.queue = Queue()
        self.poll_delay = poll_delay
        self.stale_threshold = stale_threshold
        self.last_receive_time = time.time()
        self.logger = logging.getLogger("data_logger")

    def start(self) -> None:
        self.logger.info("Starting UPS poll thread")
        self.task.start()

    def poll(self) -> None:
        while True:
            try:
                self.logger.debug("Polling UPS")
                result = apc.parse(apc.get(), strip_units=True)
                self.logger.debug("Received data from UPS")
            except ConnectionRefusedError as e:
                self.logger.error(f"Failed to connect to UPS: {e}")
            self.queue.put(result)
            time.sleep(self.poll_delay)

    def restart(self) -> None:
        del self.task
        self.task = Thread(target=self.poll, daemon=True)
        self.start()

    def get(self) -> dict[str, str] | None:
        result = None
        while not self.queue.empty():
            result = self.queue.get()
            self.last_receive_time = time.time()
        return result

    def is_stale(self) -> bool:
        return time.time() - self.last_receive_time > self.stale_threshold


def ups_stats(poll_thread: UpsPollThread) -> UpsData | None:
    logger = logging.getLogger("data_logger")
    result = poll_thread.get()
    if poll_thread.is_stale():
        logger.error("Data is stale. Restarting APC service.")
        poll_thread.restart()
        restart_ups_service()
        return None

    if not result:
        return None

    date_str = result["DATE"]
    date = date_parse(date_str)

    out_current = float(result.get("OUTCURNT", 0.0))
    out_voltage = float(result.get("OUTPUTV", 0.0))
    out_power = out_current * out_voltage
    nominal_power = float(result.get("NOMPOWER", 0.0))
    line_voltage = float(result.get("LINEV", 0.0))

    if out_power > nominal_power:
        logger.error("UPS is overloaded. Restarting APC service.")
        restart_ups_service()
        return bad_data(date, result)

    now = time.time()
    data_timestamp = date.timestamp()
    if now - data_timestamp > 240:
        logger.error("Data is too old. Restarting APC service.")
        restart_ups_service()
        return bad_data(date, result)

    if line_voltage <= 0.0 or line_voltage > 130.0:
        logger.error(
            f"Line voltage is incorrect {line_voltage}. Restarting APC service."
        )
        restart_ups_service()
        return bad_data(date, result)

    return UpsData(
        timestamp=date.timestamp(),
        serial=result.get("APC", ""),
        line_voltage=line_voltage,
        status=result.get("STATUS", ""),
        load_percent=float(result.get("LOADPCT", 0.0)),
        battery_voltage=float(result.get("BATTV", 0.0)),
        battery_percent=float(result.get("BCHARGE", 0.0)),
        output_current=out_current,
        output_voltage=out_voltage,
    )
