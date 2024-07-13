from apcaccess import status as apc
from dateutil.parser import parse as date_parse

from app.shared_data.ups_data import UpsData


def ups_stats() -> UpsData | None:
    try:
        result = apc.parse(apc.get(), strip_units=True)
    except ConnectionRefusedError:
        return None

    date_str = result["DATE"]
    date = date_parse(date_str)
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
