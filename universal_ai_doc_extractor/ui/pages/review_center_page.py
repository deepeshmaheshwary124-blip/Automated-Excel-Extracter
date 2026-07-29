"""Review Center page for reviewing and editing extracted fields."""

import logging
from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QSplitter, QMessageBox, QTextEdit, QComboBox,
)

from database.repositories import ExtractionRepository, DocumentRepository, ActivityLogRepository
from models.enums import LogCategory, ReviewAction
from utils.helpers import parse_confidence_color


logger = logging.getLogger(__name__)


class ReviewCenterPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.ext_repo = ExtractionRepository()
        self.doc_repo = DocumentRepository()
        self.log_repo = ActivityLogRepository()
        self._current_group_id: Optional[int] = None

        self._setup_ui()
        self._load_pending()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Review Center")
        title.setObjectName("titleLabel")
        header.addWidget(title)

        self.pending_label = QLabel("0 pending reviews")
        self.pending_label.setObjectName("statLabel")
        header.addWidget(self.pending_label)
        header.addStretch()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setObjectName("secondaryBtn")
        self.refresh_btn.clicked.connect(self._load_pending)
        header.addWidget(self.refresh_btn)

        layout.addLayout(header)

        splitter = QSplitter(Qt.Horizontal)

        left_panel = QFrame()
        left_panel.setObjectName("card")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(12, 12, 12, 12)

        left_header = QLabel("Pending Extractions")
        left_header.setObjectName("sectionLabel")
        left_layout.addWidget(left_header)

        self.extraction_list = QTableWidget()
        self.extraction_list.setColumnCount(3)
        self.extraction_list.setHorizontalHeaderLabels(["Document", "Confidence", "Status"])
        self.extraction_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.extraction_list.setSelectionMode(QTableWidget.SingleSelection)
        self.extraction_list.horizontalHeader().setStretchLastSection(True)
        self.extraction_list.verticalHeader().setVisible(False)
        self.extraction_list.itemSelectionChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self.extraction_list, 1)

        splitter.addWidget(left_panel)

        right_panel = QFrame()
        right_panel.setObjectName("card")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(12, 12, 12, 12)

        right_header = QLabel("Extracted Fields")
        right_header.setObjectName("sectionLabel")
        right_layout.addWidget(right_header)

        self.fields_table = QTableWidget()
        self.fields_table.setColumnCount(4)
        self.fields_table.setHorizontalHeaderLabels(["Field", "Value", "Confidence", "Status"])
        self.fields_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.fields_table.horizontalHeader().setStretchLastSection(True)
        self.fields_table.verticalHeader().setVisible(False)
        right_layout.addWidget(self.fields_table, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.approve_btn = QPushButton("Approve All")
        self.approve_btn.setObjectName("successBtn")
        self.approve_btn.clicked.connect(lambda: self._review_action("approve"))

        self.reject_btn = QPushButton("Reject")
        self.reject_btn.setObjectName("dangerBtn")
        self.reject_btn.clicked.connect(lambda: self._review_action("reject"))

        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.setObjectName("secondaryBtn")
        self.edit_btn.clicked.connect(self._edit_field)

        self.draft_btn = QPushButton("Save Draft")
        self.draft_btn.setObjectName("secondaryBtn")
        self.draft_btn.clicked.connect(lambda: self._review_action("save_draft"))

        btn_row.addWidget(self.approve_btn)
        btn_row.addWidget(self.reject_btn)
        btn_row.addWidget(self.edit_btn)
        btn_row.addWidget(self.draft_btn)
        btn_row.addStretch()
        right_layout.addLayout(btn_row)

        splitter.addWidget(right_panel)
        splitter.setSizes([300, 500])
        layout.addWidget(splitter, 1)

    def _load_pending(self) -> None:
        self.extraction_list.setRowCount(0)
        self.fields_table.setRowCount(0)
        self._current_group_id = None

        from database.connection import DatabaseConnection
        db = DatabaseConnection()
        rows = db.execute(
            """SELECT eg.id, eg.overall_confidence, eg.status, d.file_path
               FROM extraction_groups eg
               JOIN documents d ON d.id = eg.document_id
               WHERE eg.status IN ('pending_review', 'draft')
               ORDER BY eg.created_at DESC LIMIT 50"""
        ).fetchall()

        self.extraction_list.setRowCount(len(rows))
        for i, row in enumerate(rows):
            path_item = QTableWidgetItem(str(row["file_path"])[:50])
            confidence = row["overall_confidence"] or 0
            conf_item = QTableWidgetItem(f"{confidence:.0%}")
            conf_item.setForeground(Qt.green if confidence >= 0.7 else Qt.yellow)
            status_item = QTableWidgetItem(str(row["status"]).replace("_", " ").title())
            self.extraction_list.setItem(i, 0, path_item)
            self.extraction_list.setItem(i, 1, conf_item)
            self.extraction_list.setItem(i, 2, status_item)
            self.extraction_list.item(i, 0).setData(Qt.UserRole, row["id"])

        self.pending_label.setText(f"{len(rows)} pending reviews")

    def _on_selection_changed(self) -> None:
        row = self.extraction_list.currentRow()
        if row < 0:
            return

        group_id = self.extraction_list.item(row, 0).data(Qt.UserRole)
        self._current_group_id = group_id
        self._load_fields(group_id)

    def _load_fields(self, group_id: int) -> None:
        fields = self.ext_repo.get_extractions_for_group(group_id)
        self.fields_table.setRowCount(len(fields))

        for i, f in enumerate(fields):
            self.fields_table.setItem(i, 0, QTableWidgetItem(f["field_name"].replace("_", " ").title()))
            self.fields_table.setItem(i, 1, QTableWidgetItem(str(f["field_value"])[:50]))

            conf = f["confidence"] or 0
            conf_item = QTableWidgetItem(f"{conf:.0%}")
            conf_item.setForeground(parse_confidence_color(conf))
            self.fields_table.setItem(i, 2, conf_item)

            status_item = QTableWidgetItem(str(f["status"]).replace("_", " ").title())
            self.fields_table.setItem(i, 3, status_item)

    def _review_action(self, action: str) -> None:
        if not self._current_group_id:
            QMessageBox.information(self, "Select", "Select an extraction to review.")
            return

        try:
            if action == "approve":
                self.ext_repo.approve_group(self._current_group_id)
                self.log_repo.log("extraction_approved", LogCategory.EXTRACTION.value,
                                  f"Group {self._current_group_id} approved")
            elif action == "reject":
                self.ext_repo.update(
                    "UPDATE extraction_groups SET status = 'rejected', updated_at = datetime('now') WHERE id = ?",
                    (self._current_group_id,),
                )
            elif action == "save_draft":
                pass

            self._load_pending()
            self.fields_table.setRowCount(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Review action failed: {e}")

    def _edit_field(self) -> None:
        row = self.fields_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select", "Select a field to edit.")
            return

        current_value = self.fields_table.item(row, 1).text()
        field_name = self.fields_table.item(row, 0).text()

        from PySide6.QtWidgets import QInputDialog
        new_value, ok = QInputDialog.getText(
            self, f"Edit {field_name}", "New value:", text=current_value
        )

        if ok and new_value != current_value:
            self.fields_table.setItem(row, 1, QTableWidgetItem(new_value))
            self.log_repo.log("field_edited", LogCategory.EXTRACTION.value,
                              f"{field_name}: {current_value} -> {new_value}")
