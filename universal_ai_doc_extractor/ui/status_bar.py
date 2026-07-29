"""Application status bar."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QStatusBar, QLabel, QProgressBar, QHBoxLayout, QWidget


class AppStatusBar(QStatusBar):
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 0 8px;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setMaximumHeight(16)
        self.progress_bar.setVisible(False)

        self.db_status = QLabel("DB: Connected")
        self.db_status.setStyleSheet("padding: 0 8px; color: #00d4aa;")

        self.addWidget(self.status_label, 1)
        self.addWidget(self.progress_bar)
        self.addPermanentWidget(self.db_status)

    def set_status(self, text: str) -> None:
        self.status_label.setText(text)

    def show_progress(self, visible: bool = True) -> None:
        self.progress_bar.setVisible(visible)
        if visible:
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))

    def set_progress(self, value: int, maximum: int = 100) -> None:
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, maximum)
        self.progress_bar.setValue(value)

    def set_db_status(self, connected: bool) -> None:
        self.db_status.setText(f"DB: {'Connected' if connected else 'Disconnected'}")
        self.db_status.setStyleSheet(
            f"padding: 0 8px; color: {'#00d4aa' if connected else '#ff6b6b'};"
        )
