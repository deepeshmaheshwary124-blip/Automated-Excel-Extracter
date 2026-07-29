"""Backup and restore dialog."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog,
)

from database.repositories import BackupRepository, WorkbookRepository
from config.constants import BACKUPS_DIR


class BackupRestoreDialog(QDialog):
    def __init__(self, workbook_id: int = 0, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Backup & Restore")
        self.setMinimumSize(500, 400)
        self.setModal(True)

        self.workbook_id = workbook_id
        self.backup_repo = BackupRepository()
        self.wb_repo = WorkbookRepository()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Backup Manager")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(title)

        self.backup_list = QListWidget()
        layout.addWidget(self.backup_list, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        create_btn = QPushButton("Create Backup")
        create_btn.clicked.connect(self._create_backup)

        restore_btn = QPushButton("Restore Selected")
        restore_btn.setObjectName("successBtn")
        restore_btn.clicked.connect(self._restore_backup)

        delete_btn = QPushButton("Delete Selected")
        delete_btn.setObjectName("dangerBtn")
        delete_btn.clicked.connect(self._delete_backup)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondaryBtn")
        close_btn.clicked.connect(self.accept)

        btn_row.addWidget(create_btn)
        btn_row.addWidget(restore_btn)
        btn_row.addWidget(delete_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self._load_backups()

    def _load_backups(self) -> None:
        self.backup_list.clear()
        backups = self.backup_repo.get_for_workbook(self.workbook_id)
        for b in backups:
            path = Path(b["file_path"])
            size = path.stat().st_size if path.exists() else 0
            size_str = f"{size / 1024:.1f} KB" if size > 0 else "N/A"
            item = QListWidgetItem(f"{b['created_at'][:19]}  ({size_str})")
            item.setData(Qt.UserRole, b["id"])
            item.setData(Qt.UserRole + 1, b["file_path"])
            self.backup_list.addItem(item)

        if not backups:
            self.backup_list.addItem("No backups yet")

    def _create_backup(self) -> None:
        from datetime import datetime
        import shutil

        wb = self.wb_repo.get_by_id(self.workbook_id)
        if not wb:
            QMessageBox.warning(self, "Error", "Workbook not found.")
            return

        src = Path(wb["file_path"])
        if not src.exists():
            QMessageBox.warning(self, "Error", "Workbook file not found.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{src.stem}_{timestamp}{src.suffix}"
        backup_path = BACKUPS_DIR / backup_name

        try:
            shutil.copy2(str(src), str(backup_path))
            self.backup_repo.create(self.workbook_id, str(backup_path), backup_path.stat().st_size)
            QMessageBox.information(self, "Done", f"Backup created:\n{backup_path}")
            self._load_backups()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Backup failed: {e}")

    def _restore_backup(self) -> None:
        item = self.backup_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            return

        backup_path = item.data(Qt.UserRole + 1)
        wb = self.wb_repo.get_by_id(self.workbook_id)
        if not wb:
            return

        reply = QMessageBox.question(
            self, "Confirm Restore",
            "This will overwrite the current workbook. Continue?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        import shutil
        try:
            shutil.copy2(backup_path, wb["file_path"])
            QMessageBox.information(self, "Restored", "Workbook restored from backup.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Restore failed: {e}")

    def _delete_backup(self) -> None:
        item = self.backup_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            return

        backup_id = item.data(Qt.UserRole)
        backup_path = item.data(Qt.UserRole + 1)

        reply = QMessageBox.question(
            self, "Confirm Delete", "Delete this backup?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                Path(backup_path).unlink(missing_ok=True)
                self.backup_repo.delete("DELETE FROM backups WHERE id = ?", (backup_id,))
                self._load_backups()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete failed: {e}")
