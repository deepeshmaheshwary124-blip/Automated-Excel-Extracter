"""Application bootstrap - initializes all services and launches the UI."""

import logging
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication

from config.constants import APP_NAME, APP_VERSION, ensure_dirs
from config.logging_config import LogManager
from config.settings import Settings
from database.connection import DatabaseConnection
from database.migrations import run_migrations
from services.encryption_service import EncryptionService
from themes import ThemeColors
from ui.main_window import MainWindow


logger = logging.getLogger(APP_NAME)


class Application:
    def __init__(self) -> None:
        self.app: Optional[QApplication] = None
        self.main_window: Optional[MainWindow] = None
        self.settings = Settings()

    def initialize(self) -> None:
        LogManager().initialize("INFO")
        logger.info("Starting %s v%s", APP_NAME, APP_VERSION)

        ensure_dirs()

        self.settings.initialize()

        EncryptionService().initialize()

        db = DatabaseConnection()
        db.initialize()
        run_migrations()

        # Qt.AA_EnableHighDpiScaling and Qt.AA_UseHighDpiPixmaps were removed in
        # Qt 6 — high-DPI support is on by default and these attributes no longer
        # exist.  Setting them causes an AttributeError with PySide6.
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(APP_VERSION)
        self.app.setOrganizationName("AIDocExtractor")

        self._setup_fonts()

        self.main_window = MainWindow()

    def _setup_fonts(self) -> None:
        font = self.app.font()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.app.setFont(font)

    def run(self) -> int:
        if self.main_window:
            self.main_window.show()
        if self.app:
            return self.app.exec()
        return 1

    def shutdown(self) -> None:
        try:
            if self.main_window:
                self.settings.save()
            DatabaseConnection().close()
            logger.info("Application shutdown complete")
        except Exception as e:
            logger.error("Shutdown error: %s", e)
