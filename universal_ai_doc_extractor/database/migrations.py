"""Database schema migrations."""

import logging

from database.connection import DatabaseConnection


logger = logging.getLogger(__name__)

MIGRATIONS = [
    # Version 1: Initial schema
    """
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY,
        applied_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    # Version 2: Core tables
    """
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        path TEXT DEFAULT '',
        is_pinned INTEGER DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now')),
        last_opened TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS workbooks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
        file_path TEXT NOT NULL,
        sheet_name TEXT DEFAULT '',
        display_name TEXT DEFAULT '',
        row_count INTEGER DEFAULT 0,
        column_count INTEGER DEFAULT 0,
        is_pinned INTEGER DEFAULT 0,
        is_valid INTEGER DEFAULT 1,
        backup_path TEXT DEFAULT '',
        last_error TEXT DEFAULT '',
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now')),
        last_opened TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        file_type TEXT DEFAULT '',
        file_size INTEGER DEFAULT 0,
        page_count INTEGER DEFAULT 1,
        file_hash TEXT DEFAULT '',
        status TEXT DEFAULT 'pending',
        text_content TEXT DEFAULT '',
        ocr_engine_used TEXT DEFAULT '',
        processing_time_ms INTEGER DEFAULT 0,
        error_message TEXT DEFAULT '',
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS extraction_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        workbook_id INTEGER REFERENCES workbooks(id) ON DELETE SET NULL,
        status TEXT DEFAULT 'pending_review',
        overall_confidence REAL DEFAULT 0.0,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS extractions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER REFERENCES extraction_groups(id) ON DELETE CASCADE,
        document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        workbook_id INTEGER REFERENCES workbooks(id) ON DELETE SET NULL,
        field_name TEXT NOT NULL,
        field_value TEXT DEFAULT '',
        confidence REAL DEFAULT 0.0,
        status TEXT DEFAULT 'pending',
        reviewed_by TEXT DEFAULT '',
        reviewed_at TEXT,
        notes TEXT DEFAULT '',
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS ai_conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        model_used TEXT DEFAULT '',
        tokens_used INTEGER DEFAULT 0,
        duration_ms INTEGER DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        category TEXT NOT NULL,
        details TEXT DEFAULT '',
        duration_ms INTEGER DEFAULT 0,
        status TEXT DEFAULT 'success',
        user TEXT DEFAULT '',
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        field_mapping TEXT DEFAULT '{}',
        document_type TEXT DEFAULT '',
        is_default INTEGER DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS backups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workbook_id INTEGER NOT NULL REFERENCES workbooks(id) ON DELETE CASCADE,
        file_path TEXT NOT NULL,
        file_size INTEGER DEFAULT 0,
        checksum TEXT DEFAULT '',
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS queue_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,
        file_path TEXT NOT NULL,
        status TEXT DEFAULT 'queued',
        priority INTEGER DEFAULT 0,
        error_message TEXT DEFAULT '',
        retry_count INTEGER DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS settings_store (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        encrypted INTEGER DEFAULT 0,
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_extractions_document ON extractions(document_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_extractions_group ON extractions(group_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_workbooks_project ON workbooks(project_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_logs_category ON activity_logs(category)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_logs_created ON activity_logs(created_at)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_queue_status ON queue_items(status)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_conversations_session ON ai_conversations(session_id)
    """,
]


def run_migrations() -> None:
    db = DatabaseConnection()
    db.execute(
        "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT (datetime('now')))"
    )
    db.commit()

    current = db.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] or 0

    for i, sql in enumerate(MIGRATIONS, 1):
        if i > current:
            try:
                db.get_connection().executescript(sql)
                db.get_connection().execute(
                    "INSERT INTO schema_version (version) VALUES (?)", (i,)
                )
                logger.info("Migration %d applied", i)
            except Exception as e:
                logger.error("Migration %d failed: %s", i, e)
                raise

    logger.info("All migrations applied (current version: %d)", len(MIGRATIONS))
