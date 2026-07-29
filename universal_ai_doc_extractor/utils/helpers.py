"""Utility helpers for the application."""

import hashlib
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def format_duration(ms: int) -> str:
    if ms < 1000:
        return f"{ms}ms"
    elif ms < 60000:
        return f"{ms / 1000:.1f}s"
    return f"{ms / 60000:.1f}m"


def format_percentage(value: float) -> str:
    return f"{value * 100:.1f}%"


def truncate_text(text: str, max_len: int = 100) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "_", name)


def compute_file_hash(file_path: str) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def date_range(days: int) -> tuple[str, str]:
    end = datetime.now()
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


def parse_confidence_color(confidence: float) -> str:
    if confidence >= 0.9:
        return "#00d4aa"
    elif confidence >= 0.7:
        return "#ffb84d"
    return "#ff6b6b"


def safe_json_parse(text: str) -> Optional[dict[str, Any]]:
    try:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            text = text.rsplit("```", 1)[0]
        return json.loads(text)
    except (json.JSONDecodeError, ValueError, AttributeError):
        return None


def is_image_file(path: str) -> bool:
    ext = Path(path).suffix.lower()
    return ext in {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}


def is_pdf_file(path: str) -> bool:
    return Path(path).suffix.lower() == ".pdf"


def is_excel_file(path: str) -> bool:
    return Path(path).suffix.lower() in {".xlsx", ".xlsm"}
