"""Workbook Manager page for Excel workbook operations."""

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QFileDialog,
    QHeaderView, QMessageBox, QLineEdit, QSplitter,
)

from database.repositories import WorkbookRepository, ActivityLogRepository
from services.excel_service import ExcelService
from models.enums import LogCategory
from utils.helpers import format_file_size


logger = logging.getLogger(__name__)


class WorkbookManagerPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.wb_repo = WorkbookRepository()
        self.excel_service = ExcelService()
        self.log_repo = ActivityLogRepository()

        self._setup_ui()
        self._load_workbooks()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Workbook Manager")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search workbooks...")
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self._search_workbooks)
        header.addWidget(self.search_input)

        layout.addLayout(header)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.new_btn = QPushButton("New Workbook")
        self.open_btn = QPushButton("Open Workbook")
        self.open_btn.setObjectName("secondaryBtn")
        self.duplicate_btn = QPushButton("Duplicate")
        self.duplicate_btn.setObjectName("secondaryBtn")
        self.validate_btn = QPushButton("Validate")
        self.validate_btn.setObjectName("secondaryBtn")
        self.backup_btn = QPushButton("Backup")
        self.backup_btn.setObjectName("secondaryBtn")

        btn_row.addWidget(self.new_btn)
        btn_row.addWidget(self.open_btn)
        btn_row.addWidget(self.duplicate_btn)
        btn_row.addWidget(self.validate_btn)
        btn_row.addWidget(self.backup_btn)
        btn_row.addStretch()

        layout.addLayout(btn_row)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Path", "Sheets", "Rows", "Size", "Status", "Last Opened"]
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(300)

        layout.addWidget(self.table, 1)

        self.new_btn.clicked.connect(self._create_workbook)
        self.open_btn.clicked.connect(self._open_workbook)
        self.duplicate_btn.clicked.connect(self._duplicate_workbook)
        self.validate_btn.clicked.connect(self._validate_workbook)
        self.backup_btn.clicked.connect(self._backup_workbook)

    def _load_workbooks(self) -> None:
        workbooks = self.wb_repo.get_all()
        self._populate_table(workbooks)

    def _populate_table(self, workbooks: list[dict]) -> None:
        self.table.setRowCount(len(workbooks))

        for i, wb in enumerate(workbooks):
            path = Path(wb.get("file_path", ""))
            self.table.setItem(i, 0, QTableWidgetItem(wb.get("display_name", path.stem)))
            self.table.setItem(i, 1, QTableWidgetItem(str(path)))
            self.table.setItem(i, 2, QTableWidgetItem(str(wb.get("column_count", 0))))
            self.table.setItem(i, 3, QTableWidgetItem(str(wb.get("row_count", 0))))

            size = ""
            try:
                if path.exists():
                    size = format_file_size(path.stat().st_size)
            except OSError:
                size = "N/A"
            self.table.setItem(i, 4, QTableWidgetItem(size))

            valid = wb.get("is_valid", True)
            status_item = QTableWidgetItem("Valid" if valid else "Error")
            status_item.setForeground(Qt.green if valid else Qt.red)
            self.table.setItem(i, 5, status_item)

            last_opened = wb.get("last_opened", "")
            if last_opened:
                last_opened = str(last_opened)[:19]
            self.table.setItem(i, 6, QTableWidgetItem(last_opened))

    def _search_workbooks(self, query: str) -> None:
        if not query.strip():
            self._load_workbooks()
            return
        results = self.wb_repo.search(query)
        self._populate_table(results)

    def _create_workbook(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Create Workbook", "", "Excel Files (*.xlsx)"
        )
        if not path:
            return

        try:
            self.excel_service.create_workbook(path, ["Date", "Description", "Amount", "Category"])
            self.wb_repo.create(path, "Data", Path(path).stem)
            self.log_repo.log("workbook_created", LogCategory.WORKBOOK.value, path)
            self._load_workbooks()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create workbook: {e}")

    def _open_workbook(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Workbook", "", "Excel Files (*.xlsx *.xlsm)"
        )
        if not path:
            return

        try:
            sheets = self.excel_service.get_sheet_names(path)
            wb_id = self.wb_repo.create(path, sheets[0] if sheets else "Data", Path(path).stem)

            result = self.excel_service.validate_workbook(path)
            info = result.get("info", {})
            first_sheet = sheets[0] if sheets else ""
            max_rows = info.get(f"sheet_{first_sheet}_rows", 0)
            max_cols = info.get(f"sheet_{first_sheet}_cols", 0)
            self.wb_repo.update_stats(wb_id, max_rows, max_cols)

            self.log_repo.log("workbook_opened", LogCategory.WORKBOOK.value, path)
            self._load_workbooks()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open workbook: {e}")

    def _duplicate_workbook(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select", "Select a workbook first.")
            return

        src_path = self.table.item(row, 1).text()
        src = Path(src_path)
        if not src.exists():
            QMessageBox.warning(self, "Error", "Source workbook not found.")
            return

        from shutil import copy2
        dst = src.parent / f"{src.stem}_copy{src.suffix}"
        try:
            copy2(str(src), str(dst))
            self.wb_repo.create(str(dst), "Data", f"{src.stem}_copy")
            self.log_repo.log("workbook_duplicated", LogCategory.WORKBOOK.value, str(dst))
            self._load_workbooks()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Duplicate failed: {e}")

    def _validate_workbook(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select", "Select a workbook first.")
            return

        path = self.table.item(row, 1).text()
        result = self.excel_service.validate_workbook(path)

        if result["valid"]:
            QMessageBox.information(self, "Validation", "Workbook is valid.")
        else:
            QMessageBox.warning(
                self, "Validation Issues",
                f"Errors: {', '.join(result['errors'])}\n"
                f"Warnings: {', '.join(result['warnings'])}"
            )

    def _backup_workbook(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select", "Select a workbook first.")
            return

        path = self.table.item(row, 1).text()
        src = Path(path)
        if not src.exists():
            QMessageBox.warning(self, "Error", "Workbook not found.")
            return

        from config.constants import BACKUPS_DIR
        backup_path = BACKUPS_DIR / f"{src.stem}_backup_{src.name}"
        try:
            self.excel_service.backup_workbook(path, str(backup_path))
            QMessageBox.information(self, "Backup", f"Backup saved to:\n{backup_path}")
            self.log_repo.log("workbook_backup", LogCategory.BACKUP.value, str(backup_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Backup failed: {e}")
