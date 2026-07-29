"""Templates page for managing extraction templates."""

import json
import logging
from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QListWidget, QListWidgetItem, QTextEdit,
    QSplitter, QMessageBox, QLineEdit, QInputDialog,
)

from database.repositories import TemplateRepository, ActivityLogRepository
from models.enums import LogCategory


logger = logging.getLogger(__name__)


class TemplatesPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.tmpl_repo = TemplateRepository()
        self.log_repo = ActivityLogRepository()

        self._setup_ui()
        self._load_templates()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Templates")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        splitter = QSplitter(Qt.Horizontal)

        left_panel = QFrame()
        left_panel.setObjectName("card")
        left_layout = QVBoxLayout(left_panel)

        left_header = QLabel("Saved Templates")
        left_header.setObjectName("sectionLabel")
        left_layout.addWidget(left_header)

        self.template_list = QListWidget()
        left_layout.addWidget(self.template_list, 1)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self._add_template)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("dangerBtn")
        self.delete_btn.clicked.connect(self._delete_template)
        self.set_default_btn = QPushButton("Set Default")
        self.set_default_btn.setObjectName("secondaryBtn")
        self.set_default_btn.clicked.connect(self._set_default)

        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.delete_btn)
        btn_row.addWidget(self.set_default_btn)
        left_layout.addLayout(btn_row)

        splitter.addWidget(left_panel)

        right_panel = QFrame()
        right_panel.setObjectName("card")
        right_layout = QVBoxLayout(right_panel)

        right_header = QLabel("Template Details")
        right_header.setObjectName("sectionLabel")
        right_layout.addWidget(right_header)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Template name")
        right_layout.addWidget(self.name_input)

        self.mapping_editor = QTextEdit()
        self.mapping_editor.setPlaceholderText(
            '{\n  "invoice_number": "Invoice #",\n  "vendor": "Vendor Name",\n  "date": "Date",\n  "grand_total": "Total"\n}'
        )
        right_layout.addWidget(self.mapping_editor, 1)

        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self._save_template)
        right_layout.addWidget(save_btn)

        splitter.addWidget(right_panel)
        splitter.setSizes([300, 500])
        layout.addWidget(splitter, 1)

        self.template_list.currentItemChanged.connect(self._on_template_selected)

    def _load_templates(self) -> None:
        self.template_list.clear()
        templates = self.tmpl_repo.get_all()
        for tmpl in templates:
            name = tmpl["name"]
            if tmpl["is_default"]:
                name += " (Default)"
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, tmpl["id"])
            self.template_list.addItem(item)

    def _on_template_selected(self, current: QListWidgetItem, previous: Any) -> None:
        if not current:
            return
        tmpl_id = current.data(Qt.UserRole)
        tmpl = self.tmpl_repo.get_by_id(tmpl_id)
        if tmpl:
            self.name_input.setText(tmpl["name"])
            try:
                mapping = json.loads(tmpl["field_mapping"])
                self.mapping_editor.setPlainText(json.dumps(mapping, indent=2))
            except (json.JSONDecodeError, ValueError):
                self.mapping_editor.setPlainText(tmpl["field_mapping"])

    def _add_template(self) -> None:
        name, ok = QInputDialog.getText(self, "New Template", "Template name:")
        if ok and name.strip():
            try:
                self.tmpl_repo.create(name.strip())
                self.log_repo.log("template_created", LogCategory.SYSTEM.value, name)
                self._load_templates()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _delete_template(self) -> None:
        item = self.template_list.currentItem()
        if not item:
            return
        tmpl_id = item.data(Qt.UserRole)

        reply = QMessageBox.question(self, "Confirm", "Delete this template?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.tmpl_repo.delete("DELETE FROM templates WHERE id = ?", (tmpl_id,))
            self.log_repo.log("template_deleted", LogCategory.SYSTEM.value, item.text())
            self._load_templates()

    def _set_default(self) -> None:
        item = self.template_list.currentItem()
        if not item:
            return
        tmpl_id = item.data(Qt.UserRole)
        self.tmpl_repo.set_default(tmpl_id)
        self.log_repo.log("template_default", LogCategory.SYSTEM.value, item.text())
        self._load_templates()

    def _save_template(self) -> None:
        item = self.template_list.currentItem()
        if not item:
            return
        tmpl_id = item.data(Qt.UserRole)
        name = self.name_input.text().strip()
        mapping = self.mapping_editor.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Error", "Name is required.")
            return

        try:
            if mapping:
                json.loads(mapping)
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", str(e))
            return

        self.tmpl_repo.update(
            "UPDATE templates SET name = ?, field_mapping = ?, updated_at = datetime('now') WHERE id = ?",
            (name, mapping, tmpl_id),
        )
        self.log_repo.log("template_saved", LogCategory.SYSTEM.value, name)
        self._load_templates()
