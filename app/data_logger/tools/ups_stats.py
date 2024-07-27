import logging
import os
import time

from apcaccess import status as apc
from dateutil.parser import parse as date_parse

from app.shared.ups_data import UpsData


def ups_stats() -> UpsData | None:
    logger = logging.getLogger("data_logger")
    try:
        result = apc.parse(apc.get(), strip_units=True)
    except ConnectionRefusedError as e:
        logger.error(f"Failed to connect to UPS: {e}")
        return None

    date_str = result["DATE"]
    date = date_parse(date_str)

    now = time.time()
    data_timestamp = date.timestamp()
    if now - data_timestamp > 240:
        logger.error("Data is too old. Restarting APC service.")
        os.system("sudo systemctl restart apcupsd.service")
        return None
    return UpsData(
        timestamp=date.timestamp(),
        serial=result["APC"],
        line_voltage=float(result["LINEV"]),
        status=result["STATUS"],
        load_percent=float(result["LOADPCT"]),
        battery_voltage=float(result["BATTV"]),
        battery_percent=float(result["BCHARGE"]),
        output_current=float(result["OUTCURNT"]),
        output_voltage=float(result["OUTPUTV"]),
    )
