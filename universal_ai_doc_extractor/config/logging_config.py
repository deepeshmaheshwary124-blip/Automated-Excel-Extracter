"""Logging configuration for the application."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from config.constants import LOGS_DIR, APP_NAME


_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class LogManager:
    _instance: Optional["LogManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "LogManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, level: str = "INFO") -> None:
        if self._initialized:
            return
        self._initialized = True

        log_level = getattr(logging, level.upper(), logging.INFO)

        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        file_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / "app.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))

        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        logging.getLogger(APP_NAME).info(
            "Logging initialized at level %s", level
        )

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)

    def set_level(self, level: str) -> None:
        log_level = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger().setLevel(log_level)
        for handler in logging.getLogger().handlers:
            handler.setLevel(log_level)
