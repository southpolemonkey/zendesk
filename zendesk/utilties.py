import logging
from logging import Logger

from os.path import dirname, realpath, join, exists
import os

LOGGER_LEVEL = logging.INFO

fpath = join(dirname(dirname(realpath(__file__))), "logs")

if not exists(fpath):
    os.mkdir(fpath)


def get_logger(name: str) -> Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LOGGER_LEVEL)

    logger_formatter = logging.Formatter(
        "[%(asctime)s]{%(filename)s:%(lineno)d}-10s: %(levelname)s - %(message)s"
    )

    # stream_handler = logging.StreamHandler()
    # stream_handler.setFormatter(logger_formatter)

    file_handler = logging.FileHandler(filename=os.path.join(fpath, name + ".log"))
    file_handler.setFormatter(logger_formatter)

    # logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger
