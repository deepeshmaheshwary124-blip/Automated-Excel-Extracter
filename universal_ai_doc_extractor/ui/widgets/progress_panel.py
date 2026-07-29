"""Progress panel widget for extraction status."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar


class ProgressPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("sectionLabel")
        header.addWidget(self.status_label)
        header.addStretch()

        self.count_label = QLabel("0 / 0")
        self.count_label.setObjectName("statLabel")
        header.addWidget(self.count_label)

        layout.addLayout(header)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.detail_label = QLabel("")
        self.detail_label.setObjectName("statLabel")
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)

    def set_status(self, text: str) -> None:
        self.status_label.setText(text)

    def set_maximum(self, maximum: int) -> None:
        self.progress_bar.setRange(0, maximum)

    def set_progress(self, value: int, maximum: int) -> None:
        self.progress_bar.setRange(0, maximum)
        self.progress_bar.setValue(value)
        self.count_label.setText(f"{value} / {maximum}")

    def set_detail(self, text: str) -> None:
        self.detail_label.setText(text)

    def reset(self) -> None:
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready")
        self.count_label.setText("0 / 0")
        self.detail_label.setText("")
