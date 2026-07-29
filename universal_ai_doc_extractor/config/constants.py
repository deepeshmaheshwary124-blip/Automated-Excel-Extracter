"""Application configuration and settings management."""

import os
import json
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel


APP_NAME = "Universal AI Document Extractor"
APP_VERSION = "2.0.0"
APP_AUTHOR = "AI Document Solutions"
ORGANIZATION_NAME = "AIDocExtractor"


def get_app_data_dir() -> Path:
    home = Path.home()
    return home / ".ai_doc_extractor"


def get_db_path() -> Path:
    return get_app_data_dir() / "app_data.db"


def get_logs_dir() -> Path:
    return get_app_data_dir() / "logs"


def get_temp_dir() -> Path:
    return get_app_data_dir() / "temp"


def get_backups_dir() -> Path:
    return get_app_data_dir() / "backups"


def get_config_path() -> Path:
    return get_app_data_dir() / "config.json"


def ensure_dirs():
    for d in [get_app_data_dir(), get_logs_dir(), get_temp_dir(), get_backups_dir()]:
        d.mkdir(parents=True, exist_ok=True)


DB_PATH = get_db_path()
LOGS_DIR = get_logs_dir()
TEMP_DIR = get_temp_dir()
BACKUPS_DIR = get_backups_dir()


SUPPORTED_IMAGE_FORMATS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}
SUPPORTED_DOC_FORMATS = {".pdf", ".docx", ".txt", ".csv"}
SUPPORTED_EXCEL_FORMATS = {".xlsx", ".xlsm"}
ALL_SUPPORTED_FORMATS = SUPPORTED_IMAGE_FORMATS | SUPPORTED_DOC_FORMATS | SUPPORTED_EXCEL_FORMATS

MAX_FILE_SIZE_MB = 100
MAX_BATCH_SIZE = 50
DEFAULT_CHUNK_SIZE = 8192

AI_PROVIDERS = {
    "openai": "OpenAI",
    "claude": "Claude (Anthropic)",
    "gemini": "Gemini (Google)",
    "openrouter": "OpenRouter",
    "ollama": "Ollama (Local)",
}

OCR_ENGINES = {
    "tesseract": "Tesseract OCR",
    "easyocr": "EasyOCR",
    "ocrmypdf": "OCRmyPDF",
}

THEMES = {"dark": "Dark", "light": "Light", "system": "System"}

LOG_LEVELS = {"DEBUG": "Debug", "INFO": "Info", "WARNING": "Warning", "ERROR": "Error"}

FIELD_DEFINITIONS = {
    "invoice_number": "Invoice Number",
    "vendor": "Vendor",
    "customer": "Customer",
    "address": "Address",
    "phone": "Phone",
    "email": "Email",
    "date": "Date",
    "due_date": "Due Date",
    "currency": "Currency",
    "subtotal": "Subtotal",
    "tax": "Tax",
    "discount": "Discount",
    "shipping": "Shipping",
    "grand_total": "Grand Total",
    "payment_method": "Payment Method",
    "reference_number": "Reference Number",
    "purchase_order": "Purchase Order",
    "items": "Invoice Items",
    "product_name": "Product Name",
    "sku": "SKU",
    "description": "Description",
    "quantity": "Quantity",
    "unit_price": "Unit Price",
    "line_total": "Line Total",
}

ITEM_FIELDS = ["product_name", "sku", "description", "quantity", "unit_price", "line_total"]
HEADER_FIELDS = [f for f in FIELD_DEFINITIONS if f not in ITEM_FIELDS and f != "items"]


class AppConfig(BaseModel):
    theme: str = "dark"
    language: str = "en"
    ai_provider: str = "openai"
    ocr_engine: str = "tesseract"
    autosave_interval_minutes: int = 5
    backup_frequency_hours: int = 24
    logging_level: str = "INFO"
    default_workbook_path: Optional[str] = None
    performance_mode: str = "balanced"
    max_recent_files: int = 20
    max_backup_keep: int = 10
    confirm_before_overwrite: bool = True
    auto_delete_temp: bool = True
    temp_file_age_hours: int = 24

    class Config:
        validate_assignment = True
