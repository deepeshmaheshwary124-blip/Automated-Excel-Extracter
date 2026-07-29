"""Document Extractor page with drag-drop and queue processing."""

import logging
import time
from pathlib import Path
from threading import Thread
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot, QThread, QMutex
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QListWidget, QListWidgetItem, QProgressBar,
    QFileDialog, QScrollArea, QGridLayout, QSplitter,
    QMessageBox, QComboBox, QApplication,
)

from config.constants import ALL_SUPPORTED_FORMATS
from database.repositories import DocumentRepository, ActivityLogRepository
from services.document_service import DocumentService
from services.ai_service import AIService
from services.excel_service import ExcelService
from models.enums import LogCategory
from utils.helpers import format_file_size, format_duration
from ui.widgets.drop_area import DropArea
from ui.widgets.progress_panel import ProgressPanel
from ui.widgets.toast_notification import ToastNotification
from ui.dialogs.password_prompt import PasswordPromptDialog


logger = logging.getLogger(__name__)


class DocumentExtractorPage(QWidget):
    extraction_complete = Signal(dict)
    password_required = Signal(str, object)  # file_path, callback

    def __init__(self) -> None:
        super().__init__()
        self.doc_service = DocumentService()
        self.ai_service = AIService()
        self.excel_service = ExcelService()
        self.doc_repo = DocumentRepository()
        self.log_repo = ActivityLogRepository()
        self._password_cache: dict[str, str] = {}

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Document Extractor")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(16)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(12)

        self.drop_area = DropArea()
        left_panel.addWidget(self.drop_area)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.browse_btn = QPushButton("Browse Files")
        self.browse_btn.setObjectName("secondaryBtn")
        self.paste_btn = QPushButton("Paste from Clipboard")
        self.paste_btn.setObjectName("secondaryBtn")
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("secondaryBtn")

        btn_row.addWidget(self.browse_btn)
        btn_row.addWidget(self.paste_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()
        left_panel.addLayout(btn_row)

        self.progress_panel = ProgressPanel()
        left_panel.addWidget(self.progress_panel)

        content.addLayout(left_panel, 3)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(8)

        right_header = QLabel("Queue")
        right_header.setObjectName("sectionLabel")
        right_panel.addWidget(right_header)

        self.queue_list = QListWidget()
        self.queue_list.setObjectName("card")
        self.queue_list.setAlternatingRowColors(True)
        right_panel.addWidget(self.queue_list, 1)

        queue_btn_row = QHBoxLayout()
        queue_btn_row.setSpacing(8)

        self.process_btn = QPushButton("Process All")
        self.process_btn.setObjectName("successBtn")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("dangerBtn")
        self.cancel_btn.setEnabled(False)

        queue_btn_row.addWidget(self.process_btn)
        queue_btn_row.addWidget(self.cancel_btn)
        right_panel.addLayout(queue_btn_row)

        content.addLayout(right_panel, 2)
        layout.addLayout(content)

    def _connect_signals(self) -> None:
        self.browse_btn.clicked.connect(self._browse_files)
        self.drop_area.files_dropped.connect(self._add_files)
        self.process_btn.clicked.connect(self._process_queue)
        self.cancel_btn.clicked.connect(self._cancel_processing)
        self.clear_btn.clicked.connect(self._clear_queue)
        self.password_required.connect(self._on_password_required)

    def _browse_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Documents", "",
            "All Supported (*.pdf *.png *.jpg *.jpeg *.tiff *.tif *.bmp *.docx *.csv *.txt);;"
            "PDF Files (*.pdf);;"
            "Images (*.png *.jpg *.jpeg *.tiff *.tif *.bmp);;"
            "All Files (*)"
        )
        if files:
            self._add_files(files)

    def _add_files(self, file_paths: list[str]) -> None:
        for path in file_paths:
            p = Path(path)
            if not p.exists():
                continue
            if p.suffix.lower() not in ALL_SUPPORTED_FORMATS:
                self.log_repo.log("unsupported_format", LogCategory.WARNING.value,
                                  f"Skipped unsupported: {p.name}")
                continue

            try:
                doc_id = self.doc_repo.create(str(p), p.suffix.lower(), p.stat().st_size)
            except Exception as e:
                logger.error("Failed to add document: %s", e)
                continue

            item = QListWidgetItem(f"{p.name}  ({format_file_size(p.stat().st_size)})")
            item.setData(Qt.UserRole, doc_id)
            item.setData(Qt.UserRole + 1, str(p))
            self.queue_list.addItem(item)

        self.progress_panel.set_status(f"{self.queue_list.count()} files in queue")

    def _clear_queue(self) -> None:
        self.queue_list.clear()
        self.progress_panel.reset()

    def _process_queue(self) -> None:
        if self.queue_list.count() == 0:
            QMessageBox.information(self, "Queue Empty", "Add documents to the queue first.")
            return

        self.process_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_panel.set_maximum(self.queue_list.count())
        self.progress_panel.set_status("Processing...")

        self._processing_cancelled = False
        self._worker_thread = Thread(target=self._process_all, daemon=True)
        self._worker_thread.start()

    def _process_all(self) -> None:
        for i in range(self.queue_list.count()):
            if self._processing_cancelled:
                break

            item = self.queue_list.item(i)
            if not item:
                continue

            doc_id = item.data(Qt.UserRole)
            file_path = item.data(Qt.UserRole + 1)

            self.progress_panel.set_progress(i, self.queue_list.count())
            self.progress_panel.set_status(f"Processing: {Path(file_path).name}")

            password = self._password_cache.get(file_path)

            try:
                text = self.doc_service.extract_text(file_path, password)
                if text and len(text.strip()) > 20:
                    ai_result = self.ai_service.extract_from_text(text)
                    self._save_extraction(doc_id, ai_result, file_path)
                    item.setBackground(Qt.green)
                    ToastNotification.show_message(self, f"Extracted: {Path(file_path).name}", "success")
                else:
                    item.setBackground(Qt.yellow)
                    self.log_repo.log("extraction_low_text", LogCategory.WARNING.value,
                                      f"Low text content in {file_path}")
                    ToastNotification.show_message(self, f"Low text content: {Path(file_path).name}", "warning")
            except ValueError as e:
                if "password" in str(e).lower():
                    pwd = self._get_password_sync(file_path)
                    if pwd:
                        self._password_cache[file_path] = pwd
                        try:
                            text = self.doc_service.extract_text(file_path, pwd)
                            if text and len(text.strip()) > 20:
                                ai_result = self.ai_service.extract_from_text(text)
                                self._save_extraction(doc_id, ai_result, file_path)
                                item.setBackground(Qt.green)
                                ToastNotification.show_message(self, f"Extracted: {Path(file_path).name}", "success")
                                continue
                        except Exception as e2:
                            logger.error("Retry failed for %s: %s", file_path, e2)
                            item.setBackground(Qt.red)
                    else:
                        item.setBackground(Qt.yellow)
                        self.log_repo.log("extraction_skipped", LogCategory.WARNING.value,
                                          f"Password required for {file_path}")
                else:
                    logger.error("Processing failed for %s: %s", file_path, e)
                    item.setBackground(Qt.red)
                    self.log_repo.log("extraction_error", LogCategory.ERROR.value,
                                      f"Failed: {file_path} - {e}")
                    ToastNotification.show_message(self, f"Failed: {Path(file_path).name}", "error")
            except Exception as e:
                logger.error("Processing failed for %s: %s", file_path, e)
                item.setBackground(Qt.red)
                self.log_repo.log("extraction_error", LogCategory.ERROR.value,
                                  f"Failed: {file_path} - {e}")
                ToastNotification.show_message(self, f"Failed: {Path(file_path).name}", "error")

        self.progress_panel.set_progress(self.queue_list.count(), self.queue_list.count())
        self.progress_panel.set_status("Processing complete")
        self.process_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

    def _get_password_sync(self, file_path: str) -> Optional[str]:
        result = [None]

        def callback(pwd: str) -> None:
            result[0] = pwd

        self.password_required.emit(file_path, callback)

        for _ in range(200):
            if result[0] is not None:
                break
            time.sleep(0.05)
            QApplication.processEvents()

        return result[0]

    @Slot(str, object)
    def _on_password_required(self, file_path: str, callback) -> None:
        dialog = PasswordPromptDialog(file_path, self)
        if dialog.exec() == PasswordPromptDialog.Accepted:
            callback(dialog.password)
        else:
            callback(None)

    def _save_extraction(self, doc_id: int, result: dict, file_path: str) -> None:
        from database.repositories import ExtractionRepository
        ext_repo = ExtractionRepository()

        group_id = ext_repo.create_group(doc_id)
        for field_name, field_data in result.get("fields", {}).items():
            ext_repo.create_extraction(
                group_id, doc_id, field_name,
                str(field_data.get("value", "")),
                field_data.get("confidence", 0.0),
            )

    def _cancel_processing(self) -> None:
        self._processing_cancelled = True
        self.progress_panel.set_status("Cancelled")
        self.process_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
