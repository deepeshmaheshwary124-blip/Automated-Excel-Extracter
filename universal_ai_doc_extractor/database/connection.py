"""SQLite database connection manager with thread safety."""

import sqlite3
import threading
import logging
from pathlib import Path
from typing import Optional

from config.constants import DB_PATH


logger = logging.getLogger(__name__)


class DatabaseConnection:
    _instance: Optional["DatabaseConnection"] = None
    _lock = threading.Lock()
    _local = threading.local()

    def __new__(cls) -> "DatabaseConnection":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Database path: %s", self.db_path)

    def get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "connection") or self._local.connection is None:
            conn = sqlite3.connect(str(self.db_path), timeout=30)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.row_factory = sqlite3.Row
            self._local.connection = conn
        return self._local.connection

    def close(self) -> None:
        if hasattr(self._local, "connection") and self._local.connection:
            self._local.connection.close()
            self._local.connection = None

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        conn = self.get_connection()
        return conn.execute(query, params)

    def executemany(self, query: str, params: list[tuple]) -> sqlite3.Cursor:
        conn = self.get_connection()
        return conn.executemany(query, params)

    def commit(self) -> None:
        conn = self.get_connection()
        conn.commit()

    def rollback(self) -> None:
        conn = self.get_connection()
        conn.rollback()

    def last_insert_id(self) -> int:
        conn = self.get_connection()
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]
