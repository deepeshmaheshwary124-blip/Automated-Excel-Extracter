"""Sidebar navigation component."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame,
    QSpacerItem, QSizePolicy, QScrollArea,
)


NAV_ITEMS = [
    ("dashboard", "Dashboard", "🏠"),
    ("search", "Search", "🔍"),
    ("workbooks", "Workbook Manager", "📊"),
    ("extractor", "Document Extractor", "📄"),
    ("ai_assistant", "AI Assistant", "🤖"),
    ("review", "Review Center", "✅"),
    ("templates", "Templates", "📋"),
    ("logs", "Activity Logs", "📝"),
    ("reports", "Reports", "📈"),
    ("analytics", "Analytics", "📉"),
    ("settings", "Settings", "⚙️"),
    ("help", "Help", "❓"),
    ("about", "About", "ℹ️"),
]


class Sidebar(QFrame):
    page_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self._buttons: dict[str, QPushButton] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(4)

        app_label = QLabel("AI Doc\nExtractor")
        app_label.setObjectName("titleLabel")
        app_label.setAlignment(Qt.AlignLeft)
        app_label.setStyleSheet("font-size: 18px; font-weight: 700; padding: 8px 4px 16px 4px;")
        layout.addWidget(app_label)

        for key, label, icon in NAV_ITEMS:
            btn = QPushButton(f"  {label}")
            btn.setObjectName("sidebarBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self._on_click(k))
            self._buttons[key] = btn
            layout.addWidget(btn)

        layout.addStretch(1)

        version_label = QLabel("v2.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("font-size: 11px; color: #6b6d8a; padding: 8px;")
        layout.addWidget(version_label)

    def _on_click(self, key: str) -> None:
        self.set_active(key)
        self.page_selected.emit(key)

    def set_active(self, key: str) -> None:
        for k, btn in self._buttons.items():
            btn.setChecked(k == key)
