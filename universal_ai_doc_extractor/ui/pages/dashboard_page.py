"""Dashboard page with analytics cards and charts."""

import logging
from datetime import datetime, timedelta
from typing import Any

from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QScrollArea, QSizePolicy,
)

from database.repositories import (
    DocumentRepository,
    ExtractionRepository,
    ActivityLogRepository,
    WorkbookRepository,
)
from utils.helpers import format_duration, parse_confidence_color
from ui.widgets.stat_card import StatCard
from ui.widgets.chart_widget import ChartWidget
from ui.widgets.activity_timeline import ActivityTimeline


logger = logging.getLogger(__name__)


class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.doc_repo = DocumentRepository()
        self.ext_repo = ExtractionRepository()
        self.log_repo = ActivityLogRepository()
        self.wb_repo = WorkbookRepository()

        self._setup_ui()
        self._refresh_data()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        header = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Overview of your document extraction activity")
        subtitle.setObjectName("subtitleLabel")

        header.addWidget(title)
        header.addWidget(subtitle)
        header.addStretch()

        refresh_btn = QLabel("Auto-refreshing...")
        refresh_btn.setObjectName("statLabel")
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(16)
        layout.addLayout(self.cards_layout)

        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        self.doc_chart = ChartWidget("Daily Documents Processed", "bar")
        self.activity_chart = ChartWidget("7-Day Activity", "line")

        charts_row.addWidget(self.doc_chart, 3)
        charts_row.addWidget(self.activity_chart, 2)
        layout.addLayout(charts_row)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)

        self.timeline = ActivityTimeline()
        self.recent_docs = QFrame()
        self.recent_docs.setObjectName("card")
        self._setup_recent_docs()

        bottom_row.addWidget(self.timeline, 2)
        bottom_row.addWidget(self.recent_docs, 1)
        layout.addLayout(bottom_row)

        timer = QTimer(self)
        timer.timeout.connect(self._refresh_data)
        timer.start(30000)

    def _setup_recent_docs(self) -> None:
        layout = QVBoxLayout(self.recent_docs)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        title = QLabel("Recent Documents")
        title.setObjectName("sectionLabel")
        layout.addWidget(title)

        self.recent_list = QVBoxLayout()
        self.recent_list.setSpacing(4)
        layout.addLayout(self.recent_list)

    def _create_stat_cards(self) -> None:
        for i in reversed(range(self.cards_layout.count())):
            item = self.cards_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        total_docs = self.doc_repo.count_by_status("extracted")
        pending_review = self.ext_repo.get_pending_review_count()
        workbooks = len(self.wb_repo.get_all())

        cards = [
            StatCard("Documents Processed", str(total_docs), "+12%", "#6c63ff"),
            StatCard("Pending Review", str(pending_review), "", "#ffb84d"),
            StatCard("Workbooks Active", str(workbooks), "3 opened today", "#00d4aa"),
            StatCard("AI Requests", "Today: 5", "98% success", "#4dc9f6"),
        ]

        for i, card in enumerate(cards):
            self.cards_layout.addWidget(card, i // 4, i % 4)

    def _refresh_data(self) -> None:
        try:
            self._create_stat_cards()
            self._update_charts()
            self._update_recent_docs()
            self._update_timeline()
        except Exception as e:
            logger.error("Dashboard refresh failed: %s", e)

    def _update_charts(self) -> None:
        try:
            daily = self.log_repo.get_daily_counts(14)
            dates = [r["date"][-5:] for r in daily[-7:]]
            counts = [r["count"] for r in daily[-7:]]
            if dates and counts:
                self.doc_chart.update_data(dates, counts, "Documents")
        except Exception as e:
            logger.error("Chart update failed: %s", e)

    def _update_recent_docs(self) -> None:
        for i in reversed(range(self.recent_list.count())):
            item = self.recent_list.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        docs = self.doc_repo.get_recent(5)
        for doc in docs:
            label = QLabel(f"  {doc.get('file_path', 'Unknown')[:50]}")
            label.setStyleSheet("padding: 6px 8px; border-radius: 4px; font-size: 12px;")
            label.setObjectName("statLabel")
            self.recent_list.addWidget(label)

    def _update_timeline(self) -> None:
        try:
            logs = self.log_repo.get_recent(10)
            self.timeline.update_entries(logs)
        except Exception as e:
            logger.error("Timeline update failed: %s", e)
