"""Theme system with professional dark and light themes."""

from typing import Any, Optional


class ThemeColors:
    def __init__(self, mode: str = "dark") -> None:
        self.mode = mode
        if mode == "dark":
            self._init_dark()
        else:
            self._init_light()

    def _init_dark(self) -> None:
        self.bg_primary = "#1a1b2e"
        self.bg_secondary = "#232441"
        self.bg_tertiary = "#2a2b4a"
        self.bg_card = "#252640"
        self.bg_input = "#2e2f52"
        self.bg_hover = "#32335a"
        self.bg_selected = "#3a3b66"

        self.text_primary = "#e8e9f0"
        self.text_secondary = "#9a9bb4"
        self.text_muted = "#6b6d8a"
        self.text_inverse = "#1a1b2e"

        self.accent_primary = "#6c63ff"
        self.accent_secondary = "#00d4aa"
        self.accent_warning = "#ffb84d"
        self.accent_danger = "#ff6b6b"
        self.accent_info = "#4dc9f6"

        self.border = "#32335a"
        self.border_light = "#3e3f6a"
        self.divider = "#2e2f52"

        self.shadow = "rgba(0, 0, 0, 0.3)"
        self.overlay = "rgba(0, 0, 0, 0.6)"

        self.success = "#00d4aa"
        self.warning = "#ffb84d"
        self.error = "#ff6b6b"
        self.info = "#4dc9f6"

        self.chart_colors = ["#6c63ff", "#00d4aa", "#ffb84d", "#ff6b6b", "#4dc9f6", "#a78bfa"]

    def _init_light(self) -> None:
        self.bg_primary = "#f5f6fa"
        self.bg_secondary = "#ffffff"
        self.bg_tertiary = "#eef0f6"
        self.bg_card = "#ffffff"
        self.bg_input = "#eef0f6"
        self.bg_hover = "#e4e6f0"
        self.bg_selected = "#dcdff0"

        self.text_primary = "#1a1b2e"
        self.text_secondary = "#5a5b72"
        self.text_muted = "#9a9bb4"
        self.text_inverse = "#ffffff"

        self.accent_primary = "#6c63ff"
        self.accent_secondary = "#00b894"
        self.accent_warning = "#e6a800"
        self.accent_danger = "#e74c3c"
        self.accent_info = "#3498db"

        self.border = "#dcdff0"
        self.border_light = "#e8eaf5"
        self.divider = "#eef0f6"

        self.shadow = "rgba(0, 0, 0, 0.08)"
        self.overlay = "rgba(0, 0, 0, 0.3)"

        self.success = "#00b894"
        self.warning = "#e6a800"
        self.error = "#e74c3c"
        self.info = "#3498db"

        self.chart_colors = ["#6c63ff", "#00b894", "#e6a800", "#e74c3c", "#3498db", "#a78bfa"]

    def qss(self) -> str:
        c = self

        return f"""
        /* Global */
        QWidget {{
            background-color: {c.bg_primary};
            color: {c.text_primary};
            font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
            font-size: 13px;
        }}

        QMainWindow {{
            background-color: {c.bg_primary};
        }}

        /* Buttons */
        QPushButton {{
            background-color: {c.accent_primary};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 20px;
            font-weight: 500;
            font-size: 13px;
            min-height: 18px;
        }}
        QPushButton:hover {{
            background-color: {self._lighten(c.accent_primary, 15)};
        }}
        QPushButton:pressed {{
            background-color: {self._darken(c.accent_primary, 10)};
        }}
        QPushButton:disabled {{
            background-color: {c.bg_tertiary};
            color: {c.text_muted};
        }}

        QPushButton#secondaryBtn {{
            background-color: transparent;
            border: 1px solid {c.border};
            color: {c.text_primary};
        }}
        QPushButton#secondaryBtn:hover {{
            background-color: {c.bg_hover};
            border-color: {c.accent_primary};
        }}

        QPushButton#dangerBtn {{
            background-color: {c.accent_danger};
        }}
        QPushButton#dangerBtn:hover {{
            background-color: {self._lighten(c.accent_danger, 15)};
        }}

        QPushButton#successBtn {{
            background-color: {c.accent_secondary};
        }}
        QPushButton#successBtn:hover {{
            background-color: {self._lighten(c.accent_secondary, 15)};
        }}

        QPushButton#iconBtn {{
            background-color: transparent;
            border: none;
            border-radius: 4px;
            padding: 6px;
            min-width: 32px;
            min-height: 32px;
        }}
        QPushButton#iconBtn:hover {{
            background-color: {c.bg_hover};
        }}

        /* Sidebar */
        QWidget#sidebar {{
            background-color: {c.bg_secondary};
            border-right: 1px solid {c.border};
        }}

        QPushButton#sidebarBtn {{
            background-color: transparent;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            text-align: left;
            font-size: 13px;
            color: {c.text_secondary};
            min-height: 20px;
        }}
        QPushButton#sidebarBtn:hover {{
            background-color: {c.bg_hover};
            color: {c.text_primary};
        }}
        QPushButton#sidebarBtn:checked {{
            background-color: {self._with_alpha(c.accent_primary, 15)};
            color: {c.accent_primary};
            font-weight: 600;
        }}

        /* Cards */
        QFrame#card {{
            background-color: {c.bg_card};
            border: 1px solid {c.border};
            border-radius: 12px;
            padding: 20px;
        }}
        QFrame#card:hover {{
            border-color: {c.border_light};
        }}

        QFrame#statCard {{
            background-color: {c.bg_card};
            border: 1px solid {c.border};
            border-radius: 12px;
            padding: 16px;
        }}

        /* Inputs */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {c.bg_input};
            border: 1px solid {c.border};
            border-radius: 6px;
            padding: 8px 12px;
            color: {c.text_primary};
            font-size: 13px;
            selection-background-color: {c.accent_primary};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {c.accent_primary};
        }}

        QComboBox {{
            background-color: {c.bg_input};
            border: 1px solid {c.border};
            border-radius: 6px;
            padding: 8px 12px;
            color: {c.text_primary};
            min-height: 18px;
        }}
        QComboBox:hover {{
            border-color: {c.accent_primary};
        }}
        QComboBox::drop-down {{
            border: none;
            padding-right: 8px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {c.bg_secondary};
            border: 1px solid {c.border};
            border-radius: 6px;
            selection-background-color: {c.accent_primary};
            color: {c.text_primary};
        }}

        /* Tables */
        QTableWidget, QTableView {{
            background-color: {c.bg_card};
            border: 1px solid {c.border};
            border-radius: 8px;
            gridline-color: {c.divider};
            selection-background-color: {self._with_alpha(c.accent_primary, 20)};
            selection-color: {c.text_primary};
        }}
        QHeaderView::section {{
            background-color: {c.bg_tertiary};
            color: {c.text_secondary};
            border: none;
            border-bottom: 1px solid {c.border};
            padding: 10px 12px;
            font-weight: 600;
            font-size: 12px;
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: transparent;
            width: 8px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background-color: {c.border};
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {c.text_muted};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}

        QScrollBar:horizontal {{
            background-color: transparent;
            height: 8px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {c.border};
            border-radius: 4px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {c.text_muted};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}

        /* Labels */
        QLabel#titleLabel {{
            font-size: 24px;
            font-weight: 700;
            color: {c.text_primary};
        }}
        QLabel#subtitleLabel {{
            font-size: 14px;
            color: {c.text_secondary};
        }}
        QLabel#sectionLabel {{
            font-size: 16px;
            font-weight: 600;
            color: {c.text_primary};
        }}
        QLabel#statValue {{
            font-size: 28px;
            font-weight: 700;
            color: {c.text_primary};
        }}
        QLabel#statLabel {{
            font-size: 12px;
            color: {c.text_muted};
        }}
        QLabel#statChange {{
            font-size: 12px;
            font-weight: 600;
        }}

        /* Progress Bar */
        QProgressBar {{
            background-color: {c.bg_tertiary};
            border: none;
            border-radius: 4px;
            height: 8px;
            text-align: center;
            font-size: 10px;
        }}
        QProgressBar::chunk {{
            background-color: {c.accent_primary};
            border-radius: 4px;
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            background-color: {c.bg_card};
            border: 1px solid {c.border};
            border-radius: 8px;
        }}
        QTabBar::tab {{
            background-color: transparent;
            color: {c.text_secondary};
            border: none;
            padding: 10px 20px;
            font-size: 13px;
        }}
        QTabBar::tab:selected {{
            color: {c.accent_primary};
            border-bottom: 2px solid {c.accent_primary};
        }}
        QTabBar::tab:hover {{
            color: {c.text_primary};
        }}

        /* Splitter */
        QSplitter::handle {{
            background-color: {c.border};
            width: 1px;
        }}

        /* Menu */
        QMenuBar {{
            background-color: {c.bg_secondary};
            border-bottom: 1px solid {c.border};
        }}
        QMenuBar::item:selected {{
            background-color: {c.bg_hover};
        }}
        QMenu {{
            background-color: {c.bg_card};
            border: 1px solid {c.border};
            border-radius: 8px;
            padding: 4px;
        }}
        QMenu::item {{
            padding: 8px 32px 8px 16px;
            border-radius: 4px;
        }}
        QMenu::item:selected {{
            background-color: {self._with_alpha(c.accent_primary, 15)};
            color: {c.accent_primary};
        }}

        /* Dialog */
        QDialog {{
            background-color: {c.bg_primary};
        }}

        /* Tooltip */
        QToolTip {{
            background-color: {c.bg_secondary};
            color: {c.text_primary};
            border: 1px solid {c.border};
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 12px;
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {c.bg_secondary};
            border-top: 1px solid {c.border};
            color: {c.text_muted};
            font-size: 12px;
        }}

        /* Group Box */
        QGroupBox {{
            border: 1px solid {c.border};
            border-radius: 8px;
            margin-top: 16px;
            padding: 16px;
            font-weight: 600;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 4px 12px;
            color: {c.text_secondary};
        }}

        /* Drop Area */
        QFrame#dropArea {{
            background-color: {self._with_alpha(c.accent_primary, 5)};
            border: 2px dashed {c.border};
            border-radius: 12px;
        }}
        QFrame#dropArea:hover, QFrame#dropArea[dragActive="true"] {{
            background-color: {self._with_alpha(c.accent_primary, 10)};
            border-color: {c.accent_primary};
        }}
        """

    @staticmethod
    def _lighten(hex_color: str, amount: int = 20) -> str:
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + amount)
        g = min(255, g + amount)
        b = min(255, b + amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def _darken(hex_color: str, amount: int = 20) -> str:
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, r - amount)
        g = max(0, g - amount)
        b = max(0, b - amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def _with_alpha(hex_color: str, alpha: int = 20) -> str:
        hex_color = hex_color.lstrip("#")
        return f"rgba({int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}, {alpha / 100})"
