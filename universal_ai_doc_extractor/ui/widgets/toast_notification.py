"""Toast notification widget for transient status messages."""

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QColor


class ToastNotification(QFrame):
    _instances: list["ToastNotification"] = []

    def __init__(self, message: str, toast_type: str = "info",
                 duration_ms: int = 4000, parent=None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self._opacity = 0.0

        colors = {
            "success": ("#00d4aa", "#0a2e28"),
            "error": ("#ff6b6b", "#2e1414"),
            "warning": ("#ffb84d", "#2e2414"),
            "info": ("#4dc9f6", "#14242e"),
        }
        border_color, bg_color = colors.get(toast_type, colors["info"])

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            QLabel {{
                color: #e8e9f0;
                font-size: 13px;
                padding: 4px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(8)

        icons = {"success": "✓", "error": "✗", "warning": "!", "info": "ℹ"}
        icon_label = QLabel(icons.get(toast_type, "ℹ"))
        icon_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {border_color};")
        layout.addWidget(icon_label)

        self.msg_label = QLabel(message)
        self.msg_label.setWordWrap(True)
        layout.addWidget(self.msg_label, 1)

        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("background: transparent; border: none; font-size: 16px; color: #6b6d8a;")
        close_btn.clicked.connect(self._fade_out)
        layout.addWidget(close_btn)

        self.adjustSize()

        if parent:
            parent_rect = parent.geometry()
            x = parent_rect.right() - self.width() - 20
            y = parent_rect.top() + 60 + len(ToastNotification._instances) * 70
            self.move(x, y)

        QTimer.singleShot(duration_ms, self._fade_out)
        ToastNotification._instances.append(self)

    def _fade_out(self) -> None:
        if self in ToastNotification._instances:
            ToastNotification._instances.remove(self)
        self.close()
        self.deleteLater()

    @staticmethod
    def show_message(parent, message: str, toast_type: str = "info",
                     duration_ms: int = 4000) -> None:
        toast = ToastNotification(message, toast_type, duration_ms, parent)
        toast.show()
