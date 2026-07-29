"""Repository implementations for all database models."""

import logging
from typing import Any, Optional

from database.repositories.base_repository import BaseRepository


logger = logging.getLogger(__name__)


class DocumentRepository(BaseRepository):
    def create(self, file_path: str, file_type: str = "", file_size: int = 0,
               page_count: int = 1, file_hash: str = "") -> int:
        return self.insert(
            """INSERT INTO documents (file_path, file_type, file_size, page_count, file_hash)
               VALUES (?, ?, ?, ?, ?)""",
            (file_path, file_type, file_size, page_count, file_hash),
        )

    def get_by_id(self, doc_id: int) -> Optional[dict]:
        return self.fetch_one("SELECT * FROM documents WHERE id = ?", (doc_id,))

    def get_all(self, limit: int = 100, offset: int = 0) -> list[dict]:
        return self.fetch_all(
            "SELECT * FROM documents ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )

    def update_status(self, doc_id: int, status: str, error: str = "") -> int:
        return self.update(
            "UPDATE documents SET status = ?, error_message = ?, updated_at = datetime('now') WHERE id = ?",
            (status, error, doc_id),
        )

    def update_text(self, doc_id: int, text: str, ocr_engine: str = "", time_ms: int = 0) -> int:
        return self.update(
            """UPDATE documents SET text_content = ?, ocr_engine_used = ?,
               processing_time_ms = ?, status = 'extracted', updated_at = datetime('now') WHERE id = ?""",
            (text, ocr_engine, time_ms, doc_id),
        )

    def count_by_status(self, status: str) -> int:
        row = self.fetch_one(
            "SELECT COUNT(*) as count FROM documents WHERE status = ?", (status,)
        )
        return row["count"] if row else 0

    def get_recent(self, limit: int = 10) -> list[dict]:
        return self.fetch_all(
            "SELECT * FROM documents ORDER BY created_at DESC LIMIT ?", (limit,)
        )

    def delete(self, doc_id: int) -> int:
        return super().delete("DELETE FROM documents WHERE id = ?", (doc_id,))


class WorkbookRepository(BaseRepository):
    def create(self, file_path: str, sheet_name: str = "", display_name: str = "",
               project_id: Optional[int] = None) -> int:
        return self.insert(
            """INSERT INTO workbooks (file_path, sheet_name, display_name, project_id)
               VALUES (?, ?, ?, ?)""",
            (file_path, sheet_name, display_name or file_path, project_id),
        )

    def get_by_id(self, wb_id: int) -> Optional[dict]:
        return self.fetch_one("SELECT * FROM workbooks WHERE id = ?", (wb_id,))

    def get_all(self, limit: int = 100, offset: int = 0) -> list[dict]:
        return self.fetch_all(
            "SELECT * FROM workbooks ORDER BY is_pinned DESC, last_opened DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )

    def get_pinned(self) -> list[dict]:
        return self.fetch_all(
            "SELECT * FROM workbooks WHERE is_pinned = 1 ORDER BY last_opened DESC"
        )

    def toggle_pin(self, wb_id: int) -> int:
        wb = self.get_by_id(wb_id)
        if not wb:
            return 0
        new_pin = 0 if wb["is_pinned"] else 1
        return self.update(
            "UPDATE workbooks SET is_pinned = ?, updated_at = datetime('now') WHERE id = ?",
            (new_pin, wb_id),
        )

    def update_stats(self, wb_id: int, row_count: int, column_count: int) -> int:
        return self.update(
            "UPDATE workbooks SET row_count = ?, column_count = ?, updated_at = datetime('now') WHERE id = ?",
            (row_count, column_count, wb_id),
        )

    def search(self, query: str) -> list[dict]:
        return self.fetch_all(
            "SELECT * FROM workbooks WHERE file_path LIKE ? OR display_name LIKE ? ORDER BY last_opened DESC",
            (f"%{query}%", f"%{query}%"),
        )

    def delete(self, wb_id: int) -> int:
        return super().delete("DELETE FROM workbooks WHERE id = ?", (wb_id,))


class ExtractionRepository(BaseRepository):
    def create_group(self, document_id: int, workbook_id: Optional[int] = None) -> int:
        return self.insert(
            "INSERT INTO extraction_groups (document_id, workbook_id) VALUES (?, ?)",
            (document_id, workbook_id),
        )

    def get_group(self, group_id: int) -> Optional[dict]:
        return self.fetch_one("SELECT * FROM extraction_groups WHERE id = ?", (group_id,))

    def create_extraction(self, group_id: int, document_id: int, field_name: str,
                          field_value: str, confidence: float = 0.0,
                          workbook_id: Optional[int] = None) -> int:
        return self.insert(
            """INSERT INTO extractions (group_id, document_id, workbook_id, field_name, field_value, confidence)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (group_id, document_id, workbook_id, field_name, field_value, confidence),
        )

    def get_extractions_for_group(self, group_id: int) -> list[dict]:
        return self.fetch_all(
            "SELECT * FROM extractions WHERE group_id = ? ORDER BY field_name", (group_id,)
        )

    def get_extractions_for_document(self, document_id: int) -> list[dict]:
        return self.fetch_all(
            "SELECT * FROM extractions WHERE document_id = ? ORDER BY field_name", (document_id,)
        )

    def update_extraction(self, ext_id: int, field_value: str, confidence: float,
                          status: str = "edited") -> int:
        return self.update(
            """UPDATE extractions SET field_value = ?, confidence = ?, status = ?,
               updated_at = datetime('now') WHERE id = ?""",
            (field_value, confidence, status, ext_id),
        )

    def approve_group(self, group_id: int) -> int:
        return self.update(
            "UPDATE extraction_groups SET status = 'approved', updated_at = datetime('now') WHERE id = ?",
            (group_id,),
        )

    def get_pending_review_count(self) -> int:
        row = self.fetch_one(
            "SELECT COUNT(*) as count FROM extraction_groups WHERE status = 'pending_review'"
        )
        return row["count"] if row else 0


class ActivityLogRepository(BaseRepository):
    def log(self, action: str, category: str, details: str = "",
            duration_ms: int = 0, status: str = "success", user: str = "") -> int:
        return self.insert(
            """INSERT INTO activity_logs (action, category, details, duration_ms, status, user)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (action, category, details, duration_ms, status, user),
        )

    def get_recent(self, limit: int = 50) -> list[dict]:
        return self.fetch_all(
            "SELECT * FROM activity_logs ORDER BY created_at DESC LIMIT ?", (limit,)
        )

    def get_by_category(self, category: str, limit: int = 100) -> list[dict]:
        return self.fetch_all(
            "SELECT * FROM activity_logs WHERE category = ? ORDER BY created_at DESC LIMIT ?",
            (category, limit),
        )

    def get_by_date_range(self, start: str, end: str, limit: int = 500) -> list[dict]:
        return self.fetch_all(
            "SELECT * FROM activity_logs WHERE created_at BETWEEN ? AND ? ORDER BY created_at DESC LIMIT ?",
            (start, end, limit),
        )

    def count_by_category(self) -> list[dict]:
        return self.fetch_all(
            "SELECT category, COUNT(*) as count FROM activity_logs GROUP BY category ORDER BY count DESC"
        )

    def get_daily_counts(self, days: int = 30) -> list[dict]:
        return self.fetch_all(
            """SELECT DATE(created_at) as date, COUNT(*) as count
               FROM activity_logs
               WHERE created_at >= datetime('now', ?)
               GROUP BY DATE(created_at) ORDER BY date""",
            (f"-{days} days",),
        )


class AIConversationRepository(BaseRepository):
    def add_message(self, session_id: str, role: str, content: str,
                    model_used: str = "", tokens_used: int = 0, duration_ms: int = 0) -> int:
        return self.insert(
            """INSERT INTO ai_conversations (session_id, role, content, model_used, tokens_used, duration_ms)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, role, content, model_used, tokens_used, duration_ms),
        )

    def get_session(self, session_id: str, limit: int = 50) -> list[dict]:
        return self.fetch_all(
            "SELECT * FROM ai_conversations WHERE session_id = ? ORDER BY created_at ASC LIMIT ?",
            (session_id, limit),
        )

    def get_recent_sessions(self, limit: int = 20) -> list[dict]:
        return self.fetch_all(
            """SELECT session_id, MIN(created_at) as started_at, COUNT(*) as message_count,
               MAX(created_at) as last_message
               FROM ai_conversations
               GROUP BY session_id
               ORDER BY last_message DESC LIMIT ?""",
            (limit,),
        )


class SettingsStoreRepository(BaseRepository):
    def get(self, key: str) -> Optional[dict]:
        return self.fetch_one(
            "SELECT * FROM settings_store WHERE key = ?", (key,)
        )

    def set(self, key: str, value: str, encrypted: int = 0) -> int:
        existing = self.get(key)
        if existing:
            return self.update(
                "UPDATE settings_store SET value = ?, encrypted = ?, updated_at = datetime('now') WHERE key = ?",
                (value, encrypted, key),
            )
        return self.insert(
            "INSERT INTO settings_store (key, value, encrypted) VALUES (?, ?, ?)",
            (key, value, encrypted),
        )

    def delete(self, key: str) -> int:
        return super().delete("DELETE FROM settings_store WHERE key = ?", (key,))


class TemplateRepository(BaseRepository):
    def create(self, name: str, description: str = "", field_mapping: str = "{}",
               document_type: str = "", is_default: bool = False) -> int:
        return self.insert(
            """INSERT INTO templates (name, description, field_mapping, document_type, is_default)
               VALUES (?, ?, ?, ?, ?)""",
            (name, description, field_mapping, document_type, int(is_default)),
        )

    def get_all(self) -> list[dict]:
        return self.fetch_all("SELECT * FROM templates ORDER BY is_default DESC, name ASC")

    def get_by_id(self, tmpl_id: int) -> Optional[dict]:
        return self.fetch_one("SELECT * FROM templates WHERE id = ?", (tmpl_id,))

    def set_default(self, tmpl_id: int) -> int:
        self.update("UPDATE templates SET is_default = 0")
        return self.update(
            "UPDATE templates SET is_default = 1, updated_at = datetime('now') WHERE id = ?",
            (tmpl_id,),
        )


class BackupRepository(BaseRepository):
    def create(self, workbook_id: int, file_path: str, file_size: int = 0, checksum: str = "") -> int:
        return self.insert(
            "INSERT INTO backups (workbook_id, file_path, file_size, checksum) VALUES (?, ?, ?, ?)",
            (workbook_id, file_path, file_size, checksum),
        )

    def get_for_workbook(self, workbook_id: int) -> list[dict]:
        return self.fetch_all(
            "SELECT * FROM backups WHERE workbook_id = ? ORDER BY created_at DESC", (workbook_id,)
        )


class ProjectRepository(BaseRepository):
    def create(self, name: str, description: str = "", path: str = "") -> int:
        return self.insert(
            "INSERT INTO projects (name, description, path) VALUES (?, ?, ?)",
            (name, description, path),
        )

    def get_all(self) -> list[dict]:
        return self.fetch_all("SELECT * FROM projects ORDER BY is_pinned DESC, last_opened DESC")

    def get_by_id(self, proj_id: int) -> Optional[dict]:
        return self.fetch_one("SELECT * FROM projects WHERE id = ?", (proj_id,))

    def search(self, query: str) -> list[dict]:
        return self.fetch_all(
            "SELECT * FROM projects WHERE name LIKE ? OR description LIKE ? ORDER BY last_opened DESC",
            (f"%{query}%", f"%{query}%"),
        )
