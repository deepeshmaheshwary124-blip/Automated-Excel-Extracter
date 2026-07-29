"""Tests for database models and repositories."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from database.connection import DatabaseConnection
from database.migrations import run_migrations
from database.repositories import (
    DocumentRepository,
    WorkbookRepository,
    ExtractionRepository,
    ActivityLogRepository,
    SettingsStoreRepository,
    TemplateRepository,
    BackupRepository,
    ProjectRepository,
    AIConversationRepository,
)
from services.encryption_service import EncryptionService


class TestDatabase:
    def setup_method(self):
        self.db = DatabaseConnection()
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            self.db_path = Path(f.name)
        self.db.initialize(self.db_path)
        run_migrations()

    def teardown_method(self):
        self.db.close()
        self.db_path.unlink(missing_ok=True)

    def test_document_crud(self):
        repo = DocumentRepository()
        doc_id = repo.create("/test/invoice.pdf", "pdf", 1024, 2, "abc123")
        assert doc_id > 0

        doc = repo.get_by_id(doc_id)
        assert doc is not None
        assert doc["file_path"] == "/test/invoice.pdf"

        repo.update_status(doc_id, "extracted")
        doc = repo.get_by_id(doc_id)
        assert doc["status"] == "extracted"

        docs = repo.get_recent(10)
        assert len(docs) >= 1

    def test_workbook_crud(self):
        repo = WorkbookRepository()
        wb_id = repo.create("/test/workbook.xlsx", "Sheet1", "Test Workbook")
        assert wb_id > 0

        wb = repo.get_by_id(wb_id)
        assert wb["display_name"] == "Test Workbook"

        repo.toggle_pin(wb_id)
        wb = repo.get_by_id(wb_id)
        assert wb["is_pinned"] == 1

    def test_extraction_group(self):
        doc_repo = DocumentRepository()
        doc_id = doc_repo.create("/test/doc.pdf", "pdf")

        ext_repo = ExtractionRepository()
        group_id = ext_repo.create_group(doc_id)
        assert group_id > 0

        ext_repo.create_extraction(group_id, doc_id, "invoice_number", "INV-001", 0.95)
        ext_repo.create_extraction(group_id, doc_id, "vendor", "Acme Corp", 0.98)
        ext_repo.create_extraction(group_id, doc_id, "grand_total", "$1,000.00", 0.85)

        fields = ext_repo.get_extractions_for_group(group_id)
        assert len(fields) == 3

        ext_repo.approve_group(group_id)
        group = ext_repo.get_group(group_id)
        assert group["status"] == "approved"

    def test_activity_log(self):
        repo = ActivityLogRepository()
        log_id = repo.log("test_action", "test", "Test details", 100)
        assert log_id > 0

        recent = repo.get_recent(10)
        assert len(recent) >= 1

        by_cat = repo.get_by_category("test")
        assert len(by_cat) >= 1

    def test_settings_store(self):
        repo = SettingsStoreRepository()
        repo.set("theme", "dark")
        repo.set("test_key", "test_value")

        val = repo.get("test_key")
        assert val["value"] == "test_value"

        repo.delete("test_key")
        val = repo.get("test_key")
        assert val is None

    def test_encryption(self):
        enc = EncryptionService()
        enc.initialize("test_password")

        plaintext = "sk-1234567890abcdef"
        encrypted = enc.encrypt(plaintext)
        assert encrypted != plaintext

        decrypted = enc.decrypt(encrypted)
        assert decrypted == plaintext

    def test_project_and_template(self):
        proj_repo = ProjectRepository()
        proj_id = proj_repo.create("Test Project", "A test project")
        assert proj_id > 0

        tmpl_repo = TemplateRepository()
        mapping = json.dumps({"invoice_number": "Invoice #", "vendor": "Vendor"})
        tmpl_id = tmpl_repo.create("Invoice Template", "Standard invoice", mapping, "invoice", True)
        assert tmpl_id > 0

        tmpl_repo.set_default(tmpl_id)

    def test_ai_conversation(self):
        repo = AIConversationRepository()
        repo.add_message("session_1", "user", "Hello", "gpt-4o", 50, 1000)
        repo.add_message("session_1", "assistant", "Hi there!", "gpt-4o", 100, 2000)

        msgs = repo.get_session("session_1")
        assert len(msgs) == 2
