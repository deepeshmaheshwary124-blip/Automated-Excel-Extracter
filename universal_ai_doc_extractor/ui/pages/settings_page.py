"""Settings page for application configuration."""

import logging
from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QLineEdit, QCheckBox, QSpinBox,
    QScrollArea, QGridLayout, QMessageBox, QGroupBox,
    QTabWidget, QFormLayout,
)

from config.settings import Settings
from config.constants import AI_PROVIDERS, OCR_ENGINES, THEMES, LOG_LEVELS
from database.repositories import SettingsStoreRepository
from services.encryption_service import EncryptionService


logger = logging.getLogger(__name__)


class SettingsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.settings = Settings()
        self.store_repo = SettingsStoreRepository()
        self.encryption = EncryptionService()

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Settings")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self._save_settings)
        header.addWidget(self.save_btn)

        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        tabs = QTabWidget(container)

        tabs.addTab(self._create_general_tab(), "General")
        tabs.addTab(self._create_ai_tab(), "AI Provider")
        tabs.addTab(self._create_ocr_tab(), "OCR")
        tabs.addTab(self._create_security_tab(), "Security")
        tabs.addTab(self._create_advanced_tab(), "Advanced")

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(tabs)
        scroll.setWidget(container)

        layout.addWidget(scroll, 1)

    def _create_general_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(12)
        form.setContentsMargins(24, 24, 24, 24)

        self.theme_combo = QComboBox()
        for key, name in THEMES.items():
            self.theme_combo.addItem(name, key)
        form.addRow("Theme:", self.theme_combo)

        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        form.addRow("Language:", self.language_combo)

        self.autosave_spin = QSpinBox()
        self.autosave_spin.setRange(1, 60)
        self.autosave_spin.setSuffix(" min")
        form.addRow("Autosave Interval:", self.autosave_spin)

        self.logging_combo = QComboBox()
        for key, name in LOG_LEVELS.items():
            self.logging_combo.addItem(name, key)
        form.addRow("Logging Level:", self.logging_combo)

        return tab

    def _create_ai_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(12)
        form.setContentsMargins(24, 24, 24, 24)

        self.provider_combo = QComboBox()
        for key, name in AI_PROVIDERS.items():
            self.provider_combo.addItem(name, key)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_change)
        form.addRow("AI Provider:", self.provider_combo)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("e.g., gpt-4o, claude-3-opus-20240229")
        form.addRow("Model:", self.model_input)

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter API key")
        form.addRow("API Key:", self.api_key_input)

        self.test_btn = QPushButton("Test Connection")
        self.test_btn.setObjectName("secondaryBtn")
        self.test_btn.clicked.connect(self._test_connection)
        form.addRow("", self.test_btn)

        return tab

    def _create_ocr_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(12)
        form.setContentsMargins(24, 24, 24, 24)

        self.ocr_combo = QComboBox()
        for key, name in OCR_ENGINES.items():
            self.ocr_combo.addItem(name, key)
        form.addRow("OCR Engine:", self.ocr_combo)

        self.ocr_lang_input = QLineEdit("eng")
        form.addRow("Language:", self.ocr_lang_input)

        return tab

    def _create_security_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(12)
        form.setContentsMargins(24, 24, 24, 24)

        self.auto_delete_temp = QCheckBox("Auto-delete temporary files")
        form.addRow("", self.auto_delete_temp)

        self.confirm_overwrite = QCheckBox("Confirm before overwriting data")
        form.addRow("", self.confirm_overwrite)

        status_label = QLabel("API Keys: Encrypted (AES-256)")
        status_label.setStyleSheet("color: #00d4aa; font-weight: 600;")
        form.addRow("Security Status:", status_label)

        return tab

    def _create_advanced_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(12)
        form.setContentsMargins(24, 24, 24, 24)

        self.backup_spin = QSpinBox()
        self.backup_spin.setRange(1, 168)
        self.backup_spin.setSuffix(" hours")
        form.addRow("Backup Frequency:", self.backup_spin)

        self.max_backup_spin = QSpinBox()
        self.max_backup_spin.setRange(1, 50)
        self.max_backup_spin.setSuffix(" backups")
        form.addRow("Max Backups to Keep:", self.max_backup_spin)

        self.performance_combo = QComboBox()
        self.performance_combo.addItems(["Balanced", "Performance", "Memory Saver"])
        form.addRow("Performance Mode:", self.performance_combo)

        clear_btn = QPushButton("Clear All Logs")
        clear_btn.setObjectName("dangerBtn")
        clear_btn.clicked.connect(self._clear_logs)
        form.addRow("", clear_btn)

        return tab

    def _load_settings(self) -> None:
        idx = self.theme_combo.findData(self.settings.theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

        self.autosave_spin.setValue(self.settings.get("autosave_interval_minutes", 5))
        self.backup_spin.setValue(self.settings.get("backup_frequency_hours", 24))
        self.max_backup_spin.setValue(self.settings.get("max_backup_keep", 10))
        self.auto_delete_temp.setChecked(self.settings.get("auto_delete_temp", True))
        self.confirm_overwrite.setChecked(self.settings.get("confirm_before_overwrite", True))

        log_level = self.settings.logging_level
        idx = self.logging_combo.findData(log_level)
        if idx >= 0:
            self.logging_combo.setCurrentIndex(idx)

        idx = self.ocr_combo.findData(self.settings.ocr_engine)
        if idx >= 0:
            self.ocr_combo.setCurrentIndex(idx)

        idx = self.provider_combo.findData(self.settings.ai_provider)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)
            self._on_provider_change()

    def _on_provider_change(self) -> None:
        provider = self.provider_combo.currentData()
        default_models = {
            "openai": "gpt-4o",
            "claude": "claude-3-opus-20240229",
            "gemini": "gemini-1.5-pro",
            "openrouter": "openai/gpt-4o",
            "ollama": "llama3",
        }
        self.model_input.setText(default_models.get(provider, ""))

        encrypted = self.store_repo.get(f"api_key_{provider}")
        if encrypted and encrypted.get("value"):
            self.api_key_input.setPlaceholderText("API key saved (enter to change)")

    def _save_settings(self) -> None:
        self.settings.theme = self.theme_combo.currentData()
        self.settings.ai_provider = self.provider_combo.currentData()
        self.settings.ocr_engine = self.ocr_combo.currentData()
        self.settings.set("logging_level", self.logging_combo.currentData())
        self.settings.set("autosave_interval_minutes", self.autosave_spin.value())
        self.settings.set("backup_frequency_hours", self.backup_spin.value())
        self.settings.set("max_backup_keep", self.max_backup_spin.value())
        self.settings.set("auto_delete_temp", self.auto_delete_temp.isChecked())
        self.settings.set("confirm_before_overwrite", self.confirm_overwrite.isChecked())
        self.settings.save()

        api_key = self.api_key_input.text().strip()
        if api_key:
            provider = self.provider_combo.currentData()
            encrypted = self.encryption.encrypt(api_key)
            self.store_repo.set(f"api_key_{provider}", encrypted, 1)

        QMessageBox.information(self, "Saved", "Settings saved successfully.")

        from ui.main_window import MainWindow
        parent = self.window()
        if isinstance(parent, MainWindow):
            parent._set_theme(self.settings.theme)

    def _test_connection(self) -> None:
        provider = self.provider_combo.currentData()
        api_key = self.api_key_input.text().strip()

        if not api_key:
            encrypted = self.store_repo.get(f"api_key_{provider}")
            if encrypted:
                try:
                    api_key = self.encryption.decrypt(encrypted["value"])
                except Exception:
                    pass

        if not api_key and provider != "ollama":
            QMessageBox.warning(self, "No Key", "Please enter an API key.")
            return

        from ai.factory import AIClientFactory
        AIClientFactory.clear_cache()
        client = AIClientFactory.create_client(provider, self.model_input.text().strip())

        if client is None:
            QMessageBox.critical(self, "Error", "Failed to create AI client.")
            return

        try:
            response = client.chat([
                {"role": "user", "content": "Respond with just: OK"}
            ])
            QMessageBox.information(self, "Success", f"Connection successful!\nResponse: {response[:100]}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection failed:\n{e}")

    def _clear_logs(self) -> None:
        reply = QMessageBox.question(self, "Confirm", "Clear all activity logs?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            from database.connection import DatabaseConnection
            db = DatabaseConnection()
            db.execute("DELETE FROM activity_logs")
            db.commit()
            QMessageBox.information(self, "Done", "All logs cleared.")
