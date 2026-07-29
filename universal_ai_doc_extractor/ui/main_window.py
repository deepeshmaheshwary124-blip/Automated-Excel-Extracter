"""Main application window with sidebar navigation and page management."""

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QAction, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QSplitter,
    QStatusBar, QToolBar, QMenuBar, QMenu, QSizePolicy, QSpacerItem,
)

from config.constants import APP_NAME, APP_VERSION, ensure_dirs
from config.settings import Settings
from themes import ThemeColors
from database.connection import DatabaseConnection
from database.migrations import run_migrations

from ui.sidebar import Sidebar
from ui.status_bar import AppStatusBar
from ui.pages.dashboard_page import DashboardPage
from ui.pages.workbook_manager_page import WorkbookManagerPage
from ui.pages.document_extractor_page import DocumentExtractorPage
from ui.pages.ai_assistant_page import AIAssistantPage
from ui.pages.review_center_page import ReviewCenterPage
from ui.pages.templates_page import TemplatesPage
from ui.pages.activity_logs_page import ActivityLogsPage
from ui.pages.reports_page import ReportsPage
from ui.pages.analytics_page import AnalyticsPage
from ui.pages.settings_page import SettingsPage
from ui.pages.help_page import HelpPage
from ui.pages.about_page import AboutPage
from ui.pages.search_page import SearchPage


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    theme_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.settings = Settings()
        self.current_theme: str = self.settings.theme

        self._setup_window()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_central_widget()
        self._create_status_bar()
        self._create_pages()
        self._connect_signals()
        self._apply_theme()

        logger.info("MainWindow initialized")

    def _setup_window(self) -> None:
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1280, 800)
        self.resize(1440, 900)

    def _create_menu_bar(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")
        file_menu.addAction("New Workbook", self._on_new_workbook)
        file_menu.addAction("Open Workbook...", self._on_open_workbook)
        file_menu.addSeparator()
        file_menu.addAction("Import Documents...", self._on_import_documents)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction("Settings...", lambda: self.navigate_to("settings"))

        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction("Document Extractor", lambda: self.navigate_to("extractor"))
        tools_menu.addAction("AI Assistant", lambda: self.navigate_to("ai_assistant"))
        tools_menu.addAction("Review Center", lambda: self.navigate_to("review"))

        view_menu = menubar.addMenu("&View")
        view_menu.addAction("Dashboard", lambda: self.navigate_to("dashboard"))
        view_menu.addAction("Workbook Manager", lambda: self.navigate_to("workbooks"))
        view_menu.addAction("Search...", lambda: self.navigate_to("search"), "Ctrl+F")
        view_menu.addSeparator()

        theme_menu = view_menu.addMenu("Theme")
        theme_menu.addAction("Dark", lambda: self._set_theme("dark"))
        theme_menu.addAction("Light", lambda: self._set_theme("light"))

        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("Help", lambda: self.navigate_to("help"))
        help_menu.addAction("About", lambda: self.navigate_to("about"))

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        toolbar.addAction("Dashboard", lambda: self.navigate_to("dashboard"))
        toolbar.addAction("Extract", lambda: self.navigate_to("extractor"))
        toolbar.addAction("AI Chat", lambda: self.navigate_to("ai_assistant"))
        toolbar.addAction("Search", lambda: self.navigate_to("search"))
        toolbar.addSeparator()
        toolbar.addAction("Settings", lambda: self.navigate_to("settings"))

    def _create_central_widget(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.setFixedWidth(220)

        self.page_stack = QStackedWidget()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.page_stack, 1)

    def _create_status_bar(self) -> None:
        self.app_status = AppStatusBar()
        self.setStatusBar(self.app_status)

    def _create_pages(self) -> None:
        self.pages: dict[str, QWidget] = {
            "dashboard": DashboardPage(),
            "workbooks": WorkbookManagerPage(),
            "extractor": DocumentExtractorPage(),
            "ai_assistant": AIAssistantPage(),
            "review": ReviewCenterPage(),
            "templates": TemplatesPage(),
            "logs": ActivityLogsPage(),
            "reports": ReportsPage(),
            "analytics": AnalyticsPage(),
            "settings": SettingsPage(),
            "help": HelpPage(),
            "about": AboutPage(),
            "search": SearchPage(),
        }

        for name, page in self.pages.items():
            self.page_stack.addWidget(page)

        self.page_stack.setCurrentWidget(self.pages["dashboard"])

    def _connect_signals(self) -> None:
        self.sidebar.page_selected.connect(self.navigate_to)
        self.theme_changed.connect(self._on_theme_changed)

    def navigate_to(self, page_name: str) -> None:
        if page_name in self.pages:
            self.page_stack.setCurrentWidget(self.pages[page_name])
            self.sidebar.set_active(page_name)

    def _set_theme(self, theme: str) -> None:
        self.current_theme = theme
        self.settings.set("theme", theme)
        self.settings.save()
        self.theme_changed.emit(theme)

    def _on_theme_changed(self, theme: str) -> None:
        self._apply_theme()

    def _apply_theme(self) -> None:
        colors = ThemeColors(self.current_theme)
        self.setStyleSheet(colors.qss())

        for page in self.pages.values():
            page.setStyleSheet(colors.qss())

    def _on_new_workbook(self) -> None:
        self.navigate_to("workbooks")

    def _on_open_workbook(self) -> None:
        self.navigate_to("workbooks")

    def _on_import_documents(self) -> None:
        self.navigate_to("extractor")

    def closeEvent(self, event) -> None:
        self.settings.save()
        DatabaseConnection().close()
        super().closeEvent(event)
