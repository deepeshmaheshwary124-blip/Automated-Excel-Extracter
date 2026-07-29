"""Password prompt dialog for protected PDFs."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QMessageBox,
)


class PasswordPromptDialog(QDialog):
    def __init__(self, file_path: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Password Required")
        self.setFixedSize(420, 200)
        self.setModal(True)
        self._password = ""

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        icon_label = QLabel("🔒")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 36px;")
        layout.addWidget(icon_label)

        msg = QLabel(f"This document is password protected:")
        msg.setAlignment(Qt.AlignCenter)
        msg.setObjectName("statLabel")
        layout.addWidget(msg)

        if file_path:
            file_label = QLabel(file_path.split("/")[-1].split("\\")[-1])
            file_label.setAlignment(Qt.AlignCenter)
            file_label.setStyleSheet("font-weight: 600; font-size: 13px; padding: 4px;")
            layout.addWidget(file_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter document password...")
        self.password_input.returnPressed.connect(self._accept)
        layout.addWidget(self.password_input)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(self.reject)

        self.unlock_btn = QPushButton("Unlock")
        self.unlock_btn.setObjectName("successBtn")
        self.unlock_btn.clicked.connect(self._accept)

        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self.unlock_btn)
        layout.addLayout(btn_row)

        self.password_input.setFocus()

    def _accept(self) -> None:
        pwd = self.password_input.text().strip()
        if not pwd:
            QMessageBox.warning(self, "No Password", "Please enter the document password.")
            return
        self._password = pwd
        self.accept()

    @property
    def password(self) -> str:
        return self._password
