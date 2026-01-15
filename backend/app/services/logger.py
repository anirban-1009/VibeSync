import logging
import sys
from typing import Optional


class Logger:
    """
    Centralized logging configuration.
    """

    _instance: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        logger = logging.getLogger(name)

        if not logger.hasHandlers():
            logger.setLevel(logging.INFO)

            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)

            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)

            logger.addHandler(handler)

        return logger


def get_logger(name: str) -> logging.Logger:
    return Logger.get_logger(name)
