"""
Система логирования ClipboardX OSINT.

Выводит цветные сообщения в консоль
и одновременно сохраняет их в logs/app.log
"""

from __future__ import annotations

import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"


class ColoredFormatter(logging.Formatter):

    COLORS = {
        "DEBUG": "\033[90m",
        "INFO": "\033[94m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "CRITICAL": "\033[95m",
    }

    RESET = "\033[0m"

    def format(self, record):

        color = self.COLORS.get(
            record.levelname,
            self.RESET
        )

        message = super().format(record)

        return f"{color}{message}{self.RESET}"


def get_logger(name: str) -> logging.Logger:

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console = logging.StreamHandler()

    console.setFormatter(
        ColoredFormatter(
            "%(levelname)s | %(message)s"
        )
    )

    file = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    file.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file)

    return logger