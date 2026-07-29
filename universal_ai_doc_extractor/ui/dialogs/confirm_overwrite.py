"""Confirmation dialog for overwrite operations."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QFrame,
)


class ConfirmOverwriteDialog(QDialog):
    def __init__(self, title: str = "Confirm", message: str = "",
                 detail: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(480, 220)
        self.setModal(True)
        self._dont_ask_again = False

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)

        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        layout.addWidget(msg_label)

        if detail:
            detail_label = QLabel(detail)
            detail_label.setWordWrap(True)
            detail_label.setObjectName("statLabel")
            layout.addWidget(detail_label)

        layout.addStretch()

        self.dont_ask_cb = QCheckBox("Don't ask me again")
        self.dont_ask_cb.setObjectName("statLabel")
        layout.addWidget(self.dont_ask_cb)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(self.reject)

        confirm_btn = QPushButton("Confirm")
        confirm_btn.setObjectName("dangerBtn")
        confirm_btn.clicked.connect(self.accept)

        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(confirm_btn)
        layout.addLayout(btn_row)

    @property
    def dont_ask_again(self) -> bool:
        return self.dont_ask_cb.isChecked()
