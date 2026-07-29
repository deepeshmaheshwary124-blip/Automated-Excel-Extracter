"""AI Assistant chat page."""

import logging
import uuid
from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTextEdit, QScrollArea, QComboBox, QMessageBox,
    QSizePolicy, QSpacerItem,
)

from services.ai_service import AIService
from config.settings import Settings
from database.repositories import AIConversationRepository, ActivityLogRepository
from models.enums import LogCategory
from config.constants import AI_PROVIDERS


logger = logging.getLogger(__name__)


class AIAssistantPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.ai_service = AIService()
        self.settings = Settings()
        self.conv_repo = AIConversationRepository()
        self.log_repo = ActivityLogRepository()
        self._history: list[dict] = []

        self._setup_ui()
        self._add_welcome_message()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("AI Assistant")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()

        provider_layout = QHBoxLayout()
        provider_layout.setSpacing(8)
        prov_label = QLabel("Provider:")
        prov_label.setObjectName("statLabel")
        provider_layout.addWidget(prov_label)

        self.provider_combo = QComboBox()
        for key, name in AI_PROVIDERS.items():
            self.provider_combo.addItem(name, key)
        current_provider = self.settings.ai_provider
        idx = self.provider_combo.findData(current_provider)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)

        self.new_chat_btn = QPushButton("New Chat")
        self.new_chat_btn.setObjectName("secondaryBtn")
        self.new_chat_btn.clicked.connect(self._new_chat)

        provider_layout.addWidget(self.provider_combo)
        provider_layout.addWidget(self.new_chat_btn)
        header.addLayout(provider_layout)

        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        self.chat_container = QFrame()
        self.chat_container.setObjectName("card")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setSpacing(12)
        self.chat_layout.setContentsMargins(16, 16, 16, 16)
        self.chat_layout.addStretch()

        scroll.setWidget(self.chat_container)
        layout.addWidget(scroll, 1)

        input_area = QFrame()
        input_area.setObjectName("card")
        input_layout = QHBoxLayout(input_area)
        input_layout.setContentsMargins(12, 8, 12, 8)
        input_layout.setSpacing(8)

        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Ask me anything... (e.g., 'Create journal entry for electricity bill $230')")
        self.input_field.setMaximumHeight(80)
        self.input_field.setAcceptRichText(False)

        send_btn = QPushButton("Send")
        send_btn.setObjectName("successBtn")
        send_btn.setFixedWidth(100)
        send_btn.clicked.connect(self._send_message)

        input_layout.addWidget(self.input_field, 1)
        input_layout.addWidget(send_btn)

        layout.addWidget(input_area)

    def _add_welcome_message(self) -> None:
        self._add_message("assistant", "Hello! I'm your AI Document Assistant. I can help you with:\n\n"
                          "• Extract data from invoices, receipts, and documents\n"
                          "• Create journal entries from descriptions\n"
                          "• Find and summarize financial information\n"
                          "• Answer questions about your documents\n\n"
                          "Try asking: *\"I paid electricity today $230\"* or *\"Show me how to extract an invoice\"*")

    def _add_message(self, role: str, content: str) -> None:
        msg_frame = QFrame()
        is_user = role == "user"
        msg_layout = QVBoxLayout(msg_frame)
        msg_layout.setContentsMargins(0, 0, 0, 0)
        msg_layout.setSpacing(4)

        role_label = QLabel("You" if is_user else "AI Assistant")
        role_label.setObjectName("statLabel")
        role_label.setStyleSheet(
            f"font-weight: 600; font-size: 12px; color: {'#6c63ff' if is_user else '#00d4aa'};"
        )

        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet(
            f"font-size: 13px; padding: 8px 12px; border-radius: 8px; "
            f"background-color: {'#2e2f52' if is_user else '#252640'}; "
            f"color: #e8e9f0;"
        )
        content_label.setTextFormat(Qt.RichText)

        msg_layout.addWidget(role_label)
        msg_layout.addWidget(content_label)

        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg_frame)
        self._history.append({"role": "user" if is_user else "assistant", "content": content})

    def _send_message(self) -> None:
        text = self.input_field.toPlainText().strip()
        if not text:
            return

        self.input_field.clear()
        self._add_message("user", text)

        provider = self.provider_combo.currentData()

        response = self.ai_service.chat(text, provider, "", self._history[:-1])
        self._add_message("assistant", response)

    def _new_chat(self) -> None:
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        self._history.clear()
        self._add_welcome_message()
