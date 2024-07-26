import asyncio
import logging
from datetime import datetime, timedelta

from app.data_logger.bulk_stats_logger import BulkStatsLogger
from app.data_logger.today_logger import TodayLogger
from app.shared.constants import BULK_DATA, TODAYS_DATA
from app.shared.initialize_logs import initialize_logs


async def bulk_task(data_path: str, bulk_path: str, roll_over_time: timedelta) -> None:
    logger = logging.getLogger("data_logger")
    logger.info("Starting bulk task")
    bulk_stats_logger = BulkStatsLogger(data_path, bulk_path)
    while True:
        now = datetime.now()
        next_roll_over = (
            datetime(now.year, now.month, now.day) + timedelta(days=1) + roll_over_time
        )
        sleep_time = (next_roll_over - now).total_seconds()
        logger.info(
            f"Next roll over: {next_roll_over}. Sleeping for {sleep_time} seconds."
        )
        await asyncio.sleep(sleep_time)

        bulk_stats_logger.make_backup()
        logger.debug("Made backup of data.")
        data = bulk_stats_logger.read_data()
        logger.debug(f"Read {len(data)} records from data.")
        bulk_data = bulk_stats_logger.bulk(data)
        bulk_stats_logger.write_data(bulk_data)
        bulk_stats_logger.clear_data()
        logger.info(f"Wrote {len(bulk_data)} records to bulk data.")


async def async_main() -> None:
    initialize_logs("data_logger")
    logger = logging.getLogger("data_logger")
    logger.info("Starting data logger")

    data_path = TODAYS_DATA
    today_logger = TodayLogger(data_path)

    await asyncio.gather(
        today_logger.poll_cpu(),
        today_logger.poll_gpu(),
        today_logger.poll_network(),
        today_logger.poll_ups(),
        today_logger.write_data(),
        bulk_task(data_path, BULK_DATA, timedelta(hours=0, minutes=0)),
    )


def main() -> None:
    asyncio.run(async_main())
