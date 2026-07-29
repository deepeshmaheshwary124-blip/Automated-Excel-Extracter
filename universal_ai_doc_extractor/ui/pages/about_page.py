"""About page with application information."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea,
)

from config.constants import APP_NAME, APP_VERSION


class AboutPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card.setMaximumWidth(600)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        card_layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel("AI")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(
            "font-size: 64px; font-weight: 800; color: #6c63ff; "
            "background: rgba(108, 99, 255, 0.1); border-radius: 20px; padding: 20px;"
        )
        card_layout.addWidget(icon_label)

        name = QLabel(APP_NAME)
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet("font-size: 24px; font-weight: 700; color: #e8e9f0;")
        card_layout.addWidget(name)

        version = QLabel(f"Version {APP_VERSION}")
        version.setAlignment(Qt.AlignCenter)
        version.setObjectName("subtitleLabel")
        card_layout.addWidget(version)

        desc = QLabel(
            "Professional document extraction and Excel automation software.\n"
            "Powered by AI and OCR technology.\n\n"
            "Extract data from invoices, receipts, purchase orders,\n"
            "bank statements, and more — directly to Excel."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setObjectName("statLabel")
        card_layout.addWidget(desc)

        tech = QLabel(
            "Tech Stack: Python 3.11 | PySide6 | OpenPyXL | SQLite\n"
            "AI: OpenAI | Claude | Gemini | OpenRouter | Ollama\n"
            "OCR: Tesseract | EasyOCR | OCRmyPDF"
        )
        tech.setAlignment(Qt.AlignCenter)
        tech.setWordWrap(True)
        tech.setStyleSheet("font-size: 11px; color: #6b6d8a; padding: 8px;")
        card_layout.addWidget(tech)

        copyright_label = QLabel("Copyright 2024 AI Document Solutions. All rights reserved.")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("font-size: 11px; color: #6b6d8a;")
        card_layout.addWidget(copyright_label)

        layout.addWidget(card)
