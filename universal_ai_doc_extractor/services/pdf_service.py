"""PDF text extraction service."""

import io
import logging
import tempfile
from pathlib import Path
from typing import Optional

from PyPDF2 import PdfReader


logger = logging.getLogger(__name__)


class PDFService:
    def extract_text(self, file_path: str, password: Optional[str] = None) -> str:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        text_parts: list[str] = []
        try:
            reader = PdfReader(str(path))

            if reader.is_encrypted:
                if password:
                    reader.decrypt(password)
                else:
                    raise ValueError("PDF is password protected")

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text_parts.append(f"--- Page {i + 1} ---\n{page_text}")

            full_text = "\n\n".join(text_parts)
            logger.info("Extracted %d chars from %d pages in %s",
                        len(full_text), len(reader.pages), file_path)
            return full_text

        except ValueError as e:
            if "password" in str(e).lower():
                raise
            raise
        except Exception as e:
            logger.error("PDF extraction failed for %s: %s", file_path, e)
            raise

    def get_page_count(self, file_path: str) -> int:
        try:
            reader = PdfReader(file_path)
            return len(reader.pages)
        except Exception as e:
            logger.error("Failed to get page count for %s: %s", file_path, e)
            return 1

    def extract_page_images(self, file_path: str, page_numbers: Optional[list[int]] = None) -> list[bytes]:
        images: list[bytes] = []
        try:
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(file_path)
            pages_to_extract = page_numbers if page_numbers else list(range(len(pdf)))

            for page_idx in pages_to_extract:
                page = pdf[page_idx]
                bitmap = page.render(scale=2)
                img_bytes = bitmap.encode("png")
                images.append(img_bytes)

            pdf.close()
        except ImportError:
            logger.warning("pypdfium2 not available, cannot extract page images")
        except Exception as e:
            logger.error("Page image extraction failed: %s", e)

        return images
