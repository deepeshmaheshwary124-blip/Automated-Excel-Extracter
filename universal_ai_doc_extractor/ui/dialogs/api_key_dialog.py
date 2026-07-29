"""API key management dialog."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFormLayout, QMessageBox,
)

from config.constants import AI_PROVIDERS
from services.encryption_service import EncryptionService
from database.repositories import SettingsStoreRepository


class APIKeyDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Manage API Keys")
        self.setFixedSize(480, 300)
        self.setModal(True)

        self.encryption = EncryptionService()
        self.store_repo = SettingsStoreRepository()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("AI Provider API Keys")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(title)

        desc = QLabel("Keys are encrypted (AES-256) and stored locally.")
        desc.setObjectName("statLabel")
        layout.addWidget(desc)

        form = QFormLayout()
        form.setSpacing(12)

        self.provider_combo = QComboBox()
        for key, name in AI_PROVIDERS.items():
            self.provider_combo.addItem(name, key)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_change)
        form.addRow("Provider:", self.provider_combo)

        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.Password)
        self.key_input.setPlaceholderText("Enter API key")
        form.addRow("API Key:", self.key_input)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statLabel")
        form.addRow("", self.status_label)

        layout.addLayout(form)
        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        test_btn = QPushButton("Test Connection")
        test_btn.setObjectName("secondaryBtn")
        test_btn.clicked.connect(self._test_key)

        save_btn = QPushButton("Save Key")
        save_btn.clicked.connect(self._save_key)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondaryBtn")
        close_btn.clicked.connect(self.accept)

        btn_row.addWidget(test_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self._on_provider_change()

    def _on_provider_change(self) -> None:
        provider = self.provider_combo.currentData()
        encrypted = self.store_repo.get(f"api_key_{provider}")
        if encrypted and encrypted.get("value"):
            try:
                decrypted = self.encryption.decrypt(encrypted["value"])
                masked = decrypted[:8] + "..." + decrypted[-4:] if len(decrypted) > 12 else "****"
                self.status_label.setText(f"Saved key: {masked}")
                self.status_label.setStyleSheet("color: #00d4aa; font-size: 12px;")
            except Exception:
                self.status_label.setText("Key exists (encrypted)")
                self.status_label.setStyleSheet("color: #ffb84d; font-size: 12px;")
        else:
            self.status_label.setText("No key saved")
            self.status_label.setStyleSheet("color: #6b6d8a; font-size: 12px;")

    def _save_key(self) -> None:
        provider = self.provider_combo.currentData()
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "No Key", "Please enter an API key.")
            return

        encrypted = self.encryption.encrypt(key)
        self.store_repo.set(f"api_key_{provider}", encrypted, 1)
        self.key_input.clear()
        self._on_provider_change()
        QMessageBox.information(self, "Saved", f"API key for {provider} saved securely.")

    def _test_key(self) -> None:
        provider = self.provider_combo.currentData()
        key = self.key_input.text().strip()

        if not key:
            encrypted = self.store_repo.get(f"api_key_{provider}")
            if encrypted:
                try:
                    key = self.encryption.decrypt(encrypted["value"])
                except Exception:
                    QMessageBox.warning(self, "Error", "Could not decrypt saved key.")
                    return

        if not key:
            QMessageBox.warning(self, "No Key", "Enter or save an API key first.")
            return

        from ai.factory import AIClientFactory
        AIClientFactory.clear_cache()
        client = AIClientFactory.create_client(provider)
        if client is None:
            QMessageBox.critical(self, "Error", "Could not create AI client.")
            return

        try:
            response = client.chat([{"role": "user", "content": "Reply with OK"}])
            QMessageBox.information(self, "Success", f"Connection OK!\nResponse: {response[:100]}")
        except Exception as e:
            QMessageBox.critical(self, "Failed", str(e))
