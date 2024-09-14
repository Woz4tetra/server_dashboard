import logging
import os
import time
from datetime import datetime

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


def ups_stats() -> UpsData | None:
    logger = logging.getLogger("data_logger")
    try:
        result = apc.parse(apc.get(), strip_units=True)
    except ConnectionRefusedError as e:
        logger.error(f"Failed to connect to UPS: {e}")
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
