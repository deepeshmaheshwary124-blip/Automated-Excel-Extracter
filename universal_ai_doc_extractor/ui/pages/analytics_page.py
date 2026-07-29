"""Analytics page with detailed charts and statistics."""

import logging
from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QComboBox,
)

from database.repositories import ActivityLogRepository
from ui.widgets.chart_widget import ChartWidget


logger = logging.getLogger(__name__)


class AnalyticsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.log_repo = ActivityLogRepository()

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Analytics")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()

        self.period_combo = QComboBox()
        self.period_combo.addItems(["7 Days", "14 Days", "30 Days", "90 Days"])
        self.period_combo.currentTextChanged.connect(self._refresh_charts)
        header.addWidget(QLabel("Period:"))
        header.addWidget(self.period_combo)

        layout.addLayout(header)

        charts_grid = QGridLayout()
        charts_grid.setSpacing(16)

        self.daily_chart = ChartWidget("Documents by Day", "bar")
        self.category_chart = ChartWidget("Activity by Category", "bar")
        self.trend_chart = ChartWidget("Processing Trend", "line")
        self.speed_chart = ChartWidget("Processing Speed (avg ms)", "line")

        charts_grid.addWidget(self.daily_chart, 0, 0)
        charts_grid.addWidget(self.category_chart, 0, 1)
        charts_grid.addWidget(self.trend_chart, 1, 0)
        charts_grid.addWidget(self.speed_chart, 1, 1)

        layout.addLayout(charts_grid, 1)

        self._refresh_charts()

    def _refresh_charts(self) -> None:
        period_text = self.period_combo.currentText()
        days = int(period_text.split()[0]) if period_text else 7

        try:
            daily = self.log_repo.get_daily_counts(days)
            dates = [r["date"][-5:] for r in daily]
            counts = [r["count"] for r in daily]
            if dates and counts:
                self.daily_chart.update_data(dates, counts, "Activities", "#6c63ff")
                self.trend_chart.chart_type = "line"
                self.trend_chart.update_data(dates, counts, "Trend", "#4dc9f6")

            categories = self.log_repo.count_by_category()
            cat_names = [r["category"][:12] for r in categories[:8]]
            cat_counts = [r["count"] for r in categories[:8]]
            if cat_names and cat_counts:
                self.category_chart.update_data(cat_names, cat_counts, "Categories", "#00d4aa")

        except Exception as e:
            logger.error("Analytics refresh failed: %s", e)
