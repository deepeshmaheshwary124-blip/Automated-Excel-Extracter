"""Activity timeline widget showing recent actions."""

from datetime import datetime
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QScrollArea


class ActivityTimeline(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        title = QLabel("Recent Activity")
        title.setObjectName("sectionLabel")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        self.timeline_widget = QFrame()
        self.timeline_widget.setStyleSheet("background: transparent;")
        self.timeline_layout = QVBoxLayout(self.timeline_widget)
        self.timeline_layout.setSpacing(6)
        self.timeline_layout.setContentsMargins(0, 0, 0, 0)

        scroll.setWidget(self.timeline_widget)
        layout.addWidget(scroll, 1)

        self._add_placeholder()

    def _add_placeholder(self) -> None:
        label = QLabel("No recent activity")
        label.setAlignment(Qt.AlignCenter)
        label.setObjectName("statLabel")
        self.timeline_layout.addWidget(label)

    def update_entries(self, entries: list[dict[str, Any]]) -> None:
        for i in reversed(range(self.timeline_layout.count())):
            w = self.timeline_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        if not entries:
            self._add_placeholder()
            return

        for entry in entries[:10]:
            action = entry.get("action", "Unknown")
            category = entry.get("category", "")
            created = entry.get("created_at", "")

            row = QFrame()
            row.setStyleSheet("background: transparent;")
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(0, 4, 0, 4)
            row_layout.setSpacing(2)

            action_text = action.replace("_", " ").title()
            action_label = QLabel(action_text)
            action_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #e8e9f0;")

            time_str = ""
            if created:
                try:
                    dt = datetime.fromisoformat(created)
                    time_str = dt.strftime("%b %d, %I:%M %p")
                except (ValueError, TypeError):
                    time_str = str(created)[:19]

            time_label = QLabel(time_str)
            time_label.setStyleSheet("font-size: 11px; color: #6b6d8a;")

            row_layout.addWidget(action_label)
            row_layout.addWidget(time_label)
            self.timeline_layout.addWidget(row)

            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet("background-color: #2e2f52;")
            self.timeline_layout.addWidget(sep)
