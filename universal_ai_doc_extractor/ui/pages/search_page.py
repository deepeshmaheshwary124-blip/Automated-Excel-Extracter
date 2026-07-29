"""Global Search page - searches across all data entities."""

import logging
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QMessageBox,
)

from database.connection import DatabaseConnection
from database.repositories import (
    DocumentRepository, WorkbookRepository, ActivityLogRepository,
    ProjectRepository,
)


logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self) -> None:
        self.doc_repo = DocumentRepository()
        self.wb_repo = WorkbookRepository()
        self.log_repo = ActivityLogRepository()
        self.proj_repo = ProjectRepository()

    def search_all(self, query: str) -> dict[str, list[dict]]:
        results = {
            "documents": [],
            "workbooks": [],
            "projects": [],
            "logs": [],
            "invoices": [],
        }

        if not query or len(query.strip()) < 2:
            return results

        q = f"%{query}%"

        results["documents"] = self.doc_repo.fetch_all(
            "SELECT id, file_path, file_type, status, created_at FROM documents "
            "WHERE file_path LIKE ? OR file_type LIKE ? ORDER BY created_at DESC LIMIT 20",
            (q, q),
        )

        results["workbooks"] = self.wb_repo.fetch_all(
            "SELECT id, file_path, display_name, sheet_name, row_count FROM workbooks "
            "WHERE file_path LIKE ? OR display_name LIKE ? ORDER BY last_opened DESC LIMIT 20",
            (q, q),
        )

        results["projects"] = self.proj_repo.fetch_all(
            "SELECT id, name, description FROM projects "
            "WHERE name LIKE ? OR description LIKE ? ORDER BY last_opened DESC LIMIT 10",
            (q, q),
        )

        results["logs"] = self.log_repo.fetch_all(
            "SELECT id, action, category, details, created_at FROM activity_logs "
            "WHERE action LIKE ? OR category LIKE ? OR details LIKE ? "
            "ORDER BY created_at DESC LIMIT 20",
            (q, q, q),
        )

        results["invoices"] = self.doc_repo.fetch_all(
            "SELECT d.id, d.file_path, d.created_at, e.field_value as invoice_number "
            "FROM documents d "
            "JOIN extractions e ON e.document_id = d.id "
            "WHERE e.field_name = 'invoice_number' AND e.field_value LIKE ? "
            "ORDER BY d.created_at DESC LIMIT 20",
            (q,),
        )

        return results


class SearchPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.search_service = SearchService()

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Global Search")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search invoices, customers, products, documents, workbooks...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet("font-size: 14px; padding: 8px 16px;")
        self.search_input.returnPressed.connect(self._do_search)

        search_btn = QPushButton("Search")
        search_btn.setObjectName("successBtn")
        search_btn.setFixedWidth(100)
        search_btn.clicked.connect(self._do_search)

        search_row.addWidget(self.search_input, 1)
        search_row.addWidget(search_btn)
        layout.addLayout(search_row)

        self.tabs = QTabWidget()

        self.doc_table = self._make_result_table(["ID", "File", "Type", "Status", "Date"])
        self.wb_table = self._make_result_table(["ID", "Name", "Sheet", "Rows", "Path"])
        self.proj_table = self._make_result_table(["ID", "Name", "Description"])
        self.log_table = self._make_result_table(["ID", "Action", "Category", "Details", "Date"])
        self.inv_table = self._make_result_table(["ID", "Invoice #", "File", "Date"])

        self.tabs.addTab(self._wrap_table(self.doc_table), "Documents")
        self.tabs.addTab(self._wrap_table(self.wb_table), "Workbooks")
        self.tabs.addTab(self._wrap_table(self.inv_table), "Invoices")
        self.tabs.addTab(self._wrap_table(self.proj_table), "Projects")
        self.tabs.addTab(self._wrap_table(self.log_table), "Activity Logs")

        layout.addWidget(self.tabs, 1)

    def _make_result_table(self, headers: list[str]) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        return table

    def _wrap_table(self, table: QTableWidget) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(table)
        return frame

    def _do_search(self) -> None:
        query = self.search_input.text().strip()
        if len(query) < 2:
            return

        results = self.search_service.search_all(query)

        self._populate_table(self.doc_table, results["documents"],
                             ["id", "file_path", "file_type", "status", "created_at"])
        self._populate_table(self.wb_table, results["workbooks"],
                             ["id", "display_name", "sheet_name", "row_count", "file_path"])
        self._populate_table(self.proj_table, results["projects"],
                             ["id", "name", "description"])
        self._populate_table(self.log_table, results["logs"],
                             ["id", "action", "category", "details", "created_at"])
        self._populate_table(self.inv_table, results["invoices"],
                             ["id", "invoice_number", "file_path", "created_at"])

        total = sum(len(v) for v in results.values())
        tab_title = f"Search Results ({total})"
        self.tabs.setTabText(0, tab_title)
        QTimer.singleShot(100, lambda: self.tabs.setTabText(0, "Documents"))

    def _populate_table(self, table: QTableWidget, rows: list[dict],
                        keys: list[str]) -> None:
        table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, key in enumerate(keys):
                val = str(row.get(key, ""))[:60]
                table.setItem(i, j, QTableWidgetItem(val))
