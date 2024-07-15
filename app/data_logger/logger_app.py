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
    start_date = datetime.now()
    next_roll_over = start_date
    while True:
        now = datetime.now()
        next_roll_over += roll_over_time
        logger.info(f"Next roll over: {next_roll_over}")
        await asyncio.sleep((next_roll_over - now).total_seconds())
        bulk_stats_logger.make_backup()
        data = bulk_stats_logger.read_data()
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
        bulk_task(data_path, BULK_DATA, timedelta(days=1)),
    )


def main() -> None:
    asyncio.run(async_main())
