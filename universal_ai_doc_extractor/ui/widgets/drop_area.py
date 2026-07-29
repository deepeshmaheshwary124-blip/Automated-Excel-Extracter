"""Drop area widget for drag-and-drop file upload."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel


class DropArea(QFrame):
    files_dropped = Signal(list)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("dropArea")
        self.setAcceptDrops(True)
        self.setMinimumHeight(200)
        self._drag_active = False

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)

        icon_label = QLabel("📄")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px;")

        self.text_label = QLabel("Drop documents here\nor click Browse to select")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setObjectName("statLabel")
        self.text_label.setStyleSheet("font-size: 14px;")

        format_label = QLabel("PDF, PNG, JPG, TIFF, BMP, DOCX, CSV, TXT")
        format_label.setAlignment(Qt.AlignCenter)
        format_label.setObjectName("statLabel")
        format_label.setStyleSheet("font-size: 11px; color: #6b6d8a;")

        layout.addWidget(icon_label)
        layout.addWidget(self.text_label)
        layout.addWidget(format_label)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._drag_active = True
            self.setProperty("dragActive", True)
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event) -> None:
        self._drag_active = False
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event) -> None:
        self._drag_active = False
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)

        files = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path:
                files.append(path)

        if files:
            self.files_dropped.emit(files)
