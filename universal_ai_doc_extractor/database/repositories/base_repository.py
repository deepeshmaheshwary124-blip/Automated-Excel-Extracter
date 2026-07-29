"""Base repository with common CRUD operations."""

import logging
from datetime import datetime
from typing import Any, Optional

from database.connection import DatabaseConnection


logger = logging.getLogger(__name__)


class BaseRepository:
    def __init__(self) -> None:
        self.db = DatabaseConnection()

    def _row_to_dict(self, row: Any) -> dict[str, Any]:
        if row is None:
            return {}
        return dict(row)

    def _rows_to_list(self, rows: list[Any]) -> list[dict[str, Any]]:
        return [self._row_to_dict(r) for r in rows]

    def _now(self) -> str:
        return datetime.now().isoformat()

    def execute(self, query: str, params: tuple = ()) -> Any:
        return self.db.execute(query, params)

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[dict[str, Any]]:
        result = self.db.execute(query, params).fetchone()
        return self._row_to_dict(result) if result else None

    def fetch_all(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        return self._rows_to_list(self.db.execute(query, params).fetchall())

    def insert(self, query: str, params: tuple = ()) -> int:
        self.db.execute(query, params)
        self.db.commit()
        return self.db.last_insert_id()

    def update(self, query: str, params: tuple = ()) -> int:
        cursor = self.db.execute(query, params)
        self.db.commit()
        return cursor.rowcount

    def delete(self, query: str, params: tuple = ()) -> int:
        cursor = self.db.execute(query, params)
        self.db.commit()
        return cursor.rowcount
