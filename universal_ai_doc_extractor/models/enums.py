"""Enumerations used across the application."""

from enum import Enum, auto


class DocumentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    FAILED = "failed"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class ExtractionFieldStatus(Enum):
    PENDING = "pending"
    HIGH_CONFIDENCE = "high_confidence"
    LOW_CONFIDENCE = "low_confidence"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EDITED = "edited"


class ExtractionStatus(Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WRITTEN = "written"


class DocumentType(Enum):
    PDF = "pdf"
    IMAGE = "image"
    DOCX = "docx"
    CSV = "csv"
    TXT = "txt"
    EXCEL = "excel"
    UNKNOWN = "unknown"


class AIProvider(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"


class OCREngine(Enum):
    TESSERACT = "tesseract"
    EASYOCR = "easyocr"
    OCRMYPDF = "ocrmypdf"


class LogCategory(Enum):
    SYSTEM = "system"
    DOCUMENT = "document"
    EXTRACTION = "extraction"
    WORKBOOK = "workbook"
    AI_REQUEST = "ai_request"
    OCR = "ocr"
    ERROR = "error"
    WARNING = "warning"
    USER_ACTION = "user_action"
    BACKUP = "backup"
    SETTINGS = "settings"


class ThemeMode(Enum):
    DARK = "dark"
    LIGHT = "light"
    SYSTEM = "system"


class QueueItemStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ReviewAction(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    EDIT = "edit"
    SAVE_DRAFT = "save_draft"
