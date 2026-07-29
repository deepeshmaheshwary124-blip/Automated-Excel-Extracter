"""Stat card widget for dashboard metrics."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout


class StatCard(QFrame):
    def __init__(self, title: str, value: str, change: str = "", color: str = "#6c63ff") -> None:
        super().__init__()
        self.setObjectName("statCard")
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("statLabel")

        value_label = QLabel(value)
        value_label.setObjectName("statValue")

        change_label = QLabel(change)
        change_label.setObjectName("statChange")
        if change and "+" in change:
            change_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")
        else:
            change_label.setStyleSheet(f"color: #6b6d8a; font-size: 12px;")

        indicator = QFrame()
        indicator.setFixedSize(4, 40)
        indicator.setStyleSheet(f"background-color: {color}; border-radius: 2px;")

        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        top_row.addWidget(indicator)
        top_row.addWidget(title_label)
        top_row.addStretch()

        layout.addLayout(top_row)
        layout.addWidget(value_label)
        layout.addWidget(change_label)
