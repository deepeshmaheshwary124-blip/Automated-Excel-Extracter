"""Data models for the application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class Document:
    id: Optional[int] = None
    file_path: str = ""
    file_type: str = ""
    file_size: int = 0
    page_count: int = 1
    file_hash: str = ""
    status: str = "pending"
    text_content: str = ""
    ocr_engine_used: str = ""
    processing_time_ms: int = 0
    error_message: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


@dataclass
class Extraction:
    id: Optional[int] = None
    document_id: int = 0
    workbook_id: Optional[int] = None
    field_name: str = ""
    field_value: str = ""
    confidence: float = 0.0
    status: str = "pending"
    reviewed_by: str = ""
    reviewed_at: str = ""
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


@dataclass
class ExtractionGroup:
    id: Optional[int] = None
    document_id: int = 0
    workbook_id: Optional[int] = None
    status: str = "pending_review"
    overall_confidence: float = 0.0
    fields: list[Extraction] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Workbook:
    id: Optional[int] = None
    project_id: Optional[int] = None
    file_path: str = ""
    sheet_name: str = ""
    display_name: str = ""
    row_count: int = 0
    column_count: int = 0
    is_pinned: bool = False
    is_valid: bool = True
    backup_path: str = ""
    last_error: str = ""
    created_at: str = ""
    updated_at: str = ""
    last_opened: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


@dataclass
class Project:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    path: str = ""
    is_pinned: bool = False
    created_at: str = ""
    updated_at: str = ""
    last_opened: str = ""


@dataclass
class AIConversation:
    id: Optional[int] = None
    session_id: str = ""
    role: str = ""
    content: str = ""
    model_used: str = ""
    tokens_used: int = 0
    duration_ms: int = 0
    created_at: str = ""


@dataclass
class ActivityLog:
    id: Optional[int] = None
    action: str = ""
    category: str = ""
    details: str = ""
    duration_ms: int = 0
    status: str = "success"
    user: str = ""
    created_at: str = ""


@dataclass
class Template:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    field_mapping: str = ""
    document_type: str = ""
    is_default: bool = False
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Backup:
    id: Optional[int] = None
    workbook_id: int = 0
    file_path: str = ""
    file_size: int = 0
    checksum: str = ""
    created_at: str = ""


@dataclass
class QueueItem:
    id: Optional[int] = None
    document_id: int = 0
    file_path: str = ""
    status: str = "queued"
    priority: int = 0
    error_message: str = ""
    retry_count: int = 0
    created_at: str = ""
    updated_at: str = ""
