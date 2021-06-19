import logging
from logging import Logger
from .config import LOGGER_LEVEL


def get_logger(name: str) -> Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LOGGER_LEVEL)

    stream_handler = logging.StreamHandler()
    logger_formatter = logging.Formatter(
        "[%(asctime)s]{%(filename)s:%(lineno)d}-10s: %(levelname)s - %(message)s"
    )
    stream_handler.setFormatter(logger_formatter)
    logger.addHandler(stream_handler)
    return logger
