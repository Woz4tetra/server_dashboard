from app.data_logger.bulk_stats_logger import BulkStatsLogger
from app.shared.constants import BULK_DATA, TODAYS_DATA


def main() -> None:
    bulk_stats_logger = BulkStatsLogger(TODAYS_DATA, BULK_DATA)
    bulk_stats_logger.make_backup()
    print("Made backup of data.")
    data = bulk_stats_logger.read_data()
    print(f"Read {len(data)} records from data.")
    bulk_data = bulk_stats_logger.bulk(data)
    bulk_stats_logger.write_data(bulk_data)
    bulk_stats_logger.clear_data()
    print(f"Wrote {len(bulk_data)} records to bulk data.")


if __name__ == "__main__":
    main()
