import logging
from logging import Logger
import os
from os.path import dirname, realpath, join, exists

import yaml

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


def read_yaml(file: str):
    with open(file, 'r') as f:
        dic = yaml.load(f, Loader=yaml.FullLoader)
        return dic

if __name__ == '__main__':
    config = read_yaml("../config.yaml")
    from pprint import pprint
    pprint(config, indent=2)
    # tables = config.get('tables')
    # print(tables.keys())
