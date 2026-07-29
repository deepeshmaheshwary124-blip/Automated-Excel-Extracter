"""Reports page for generating extraction and activity reports."""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QDateEdit, QMessageBox, QGridLayout,
)

from database.repositories import ActivityLogRepository, DocumentRepository, ExtractionRepository
from utils.helpers import format_duration, parse_confidence_color


logger = logging.getLogger(__name__)


class ReportsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.log_repo = ActivityLogRepository()
        self.doc_repo = DocumentRepository()
        self.ext_repo = ExtractionRepository()

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Reports")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()

        self.export_btn = QPushButton("Export Report")
        self.export_btn.clicked.connect(self._export_report)
        header.addWidget(self.export_btn)

        layout.addLayout(header)

        cards = QGridLayout()
        cards.setSpacing(16)

        self.total_docs_card = self._make_info_card("Documents Processed", "0")
        self.success_rate_card = self._make_info_card("Success Rate", "0%")
        self.avg_time_card = self._make_info_card("Avg Processing Time", "0ms")
        self.ai_requests_card = self._make_info_card("AI Requests", "0")

        cards.addWidget(self.total_docs_card, 0, 0)
        cards.addWidget(self.success_rate_card, 0, 1)
        cards.addWidget(self.avg_time_card, 0, 2)
        cards.addWidget(self.ai_requests_card, 0, 3)

        layout.addLayout(cards)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Documents", "Success", "Failed", "Avg Time"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table, 1)

        self._load_report()

    def _make_info_card(self, title: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("statCard")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 12, 16, 12)
        cl.setSpacing(4)

        t = QLabel(title)
        t.setObjectName("statLabel")
        v = QLabel(value)
        v.setObjectName("statValue")
        v.setObjectName("statValue")

        cl.addWidget(t)
        cl.addWidget(v)
        return card

    def _load_report(self) -> None:
        try:
            from database.connection import DatabaseConnection
            db = DatabaseConnection()

            total = db.execute("SELECT COUNT(*) as c FROM documents").fetchone()["c"]
            success = db.execute("SELECT COUNT(*) as c FROM documents WHERE status = 'extracted'").fetchone()["c"]
            failed = db.execute("SELECT COUNT(*) as c FROM documents WHERE status = 'failed'").fetchone()["c"]
            ai_count = db.execute("SELECT COUNT(*) as c FROM ai_conversations").fetchone()["c"]
            avg_time = db.execute("SELECT AVG(processing_time_ms) as avg FROM documents WHERE processing_time_ms > 0").fetchone()["avg"] or 0

            self._update_cards(str(total), f"{(success / total * 100):.0f}%" if total > 0 else "0%",
                               f"{avg_time:.0f}ms", str(ai_count))

            daily = db.execute(
                """SELECT DATE(created_at) as date,
                          COUNT(*) as total,
                          SUM(CASE WHEN status = 'extracted' THEN 1 ELSE 0 END) as success,
                          SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                          AVG(processing_time_ms) as avg_time
                   FROM documents
                   GROUP BY DATE(created_at)
                   ORDER BY date DESC LIMIT 30"""
            ).fetchall()

            self.table.setRowCount(len(daily))
            for i, row in enumerate(daily):
                self.table.setItem(i, 0, QTableWidgetItem(str(row["date"])[:10]))
                self.table.setItem(i, 1, QTableWidgetItem(str(row["total"])))
                self.table.setItem(i, 2, QTableWidgetItem(str(row["success"])))
                self.table.setItem(i, 3, QTableWidgetItem(str(row["failed"])))
                avg = row["avg_time"] or 0
                self.table.setItem(i, 4, QTableWidgetItem(f"{avg:.0f}ms"))

        except Exception as e:
            logger.error("Report load failed: %s", e)

    def _update_cards(self, docs: str, rate: str, avg: str, ai: str) -> None:
        for widget in self.total_docs_card.findChildren(QLabel):
            if widget.objectName() == "statValue":
                widget.setText(docs)
                break

    def _export_report(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        import csv

        path, _ = QFileDialog.getSaveFileName(self, "Export Report", "report.csv", "CSV Files (*.csv)")
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Documents", "Success", "Failed", "Avg Time"])
                for row in range(self.table.rowCount()):
                    writer.writerow([
                        self.table.item(row, 0).text() if self.table.item(row, 0) else "",
                        self.table.item(row, 1).text() if self.table.item(row, 1) else "",
                        self.table.item(row, 2).text() if self.table.item(row, 2) else "",
                        self.table.item(row, 3).text() if self.table.item(row, 3) else "",
                        self.table.item(row, 4).text() if self.table.item(row, 4) else "",
                    ])
            QMessageBox.information(self, "Exported", f"Report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")
