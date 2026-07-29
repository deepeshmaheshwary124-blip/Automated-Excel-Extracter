"""Activity Logs page for viewing system logs."""

import logging
from datetime import datetime
from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QLineEdit, QMessageBox,
)

from database.repositories import ActivityLogRepository


logger = logging.getLogger(__name__)


class ActivityLogsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.log_repo = ActivityLogRepository()
        self._setup_ui()
        self._load_logs()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Activity Logs")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "system", "document", "extraction", "workbook",
                                    "ai_request", "ocr", "error", "backup", "user_action"])
        self.filter_combo.currentTextChanged.connect(self._filter_logs)
        header.addWidget(QLabel("Category:"))
        header.addWidget(self.filter_combo)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setObjectName("secondaryBtn")
        self.refresh_btn.clicked.connect(self._load_logs)
        header.addWidget(self.refresh_btn)

        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Time", "Action", "Category", "Details", "Duration", "Status"]
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)

        layout.addWidget(self.table, 1)

    def _load_logs(self) -> None:
        logs = self.log_repo.get_recent(200)
        self._populate_table(logs)

    def _filter_logs(self, category: str) -> None:
        if category == "All":
            self._load_logs()
        else:
            logs = self.log_repo.get_by_category(category, 200)
            self._populate_table(logs)

    def _populate_table(self, logs: list[dict]) -> None:
        self.table.setRowCount(len(logs))

        for i, log_entry in enumerate(logs):
            created = str(log_entry.get("created_at", ""))[:19]
            self.table.setItem(i, 0, QTableWidgetItem(created))
            self.table.setItem(i, 1, QTableWidgetItem(log_entry.get("action", "").replace("_", " ").title()))
            self.table.setItem(i, 2, QTableWidgetItem(log_entry.get("category", "")))
            self.table.setItem(i, 3, QTableWidgetItem(str(log_entry.get("details", ""))[:100]))

            duration = log_entry.get("duration_ms", 0)
            duration_str = f"{duration}ms" if duration else ""
            self.table.setItem(i, 4, QTableWidgetItem(duration_str))

            status = log_entry.get("status", "")
            status_item = QTableWidgetItem(status.title())
            if status == "error":
                status_item.setForeground(Qt.red)
            elif status == "success":
                status_item.setForeground(Qt.green)
            self.table.setItem(i, 5, status_item)
