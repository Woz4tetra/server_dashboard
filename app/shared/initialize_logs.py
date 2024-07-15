import logging
from logging.handlers import TimedRotatingFileHandler


def initialize_logs(name: str) -> None:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(levelname)s] [%(name)s] %(asctime)s: %(message)s")

    print_handle = logging.StreamHandler()
    print_handle.setFormatter(formatter)
    print_handle.setLevel(logging.DEBUG)
    logger.addHandler(print_handle)

    file_handle = TimedRotatingFileHandler(
        f"data/{name}.log", when="midnight", interval=1, backupCount=7
    )
    file_handle.setFormatter(formatter)
    file_handle.setLevel(logging.DEBUG)
    logger.addHandler(file_handle)

    logger.debug(f"Initialized logs for {name}")
