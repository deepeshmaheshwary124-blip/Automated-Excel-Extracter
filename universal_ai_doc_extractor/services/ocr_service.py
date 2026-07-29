"""OCR text extraction service with multi-engine support."""

import logging
import tempfile
import time
from pathlib import Path
from typing import Optional

from PIL import Image

from config.constants import OCR_ENGINES
from models.enums import OCREngine


logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self, engine: str = "tesseract") -> None:
        self._engine_name = engine
        self._tesseract = None
        self._easyocr = None

    @property
    def engine_name(self) -> str:
        return self._engine_name

    @engine_name.setter
    def engine_name(self, value: str) -> None:
        if value not in OCR_ENGINES:
            raise ValueError(f"Unsupported OCR engine: {value}")
        self._engine_name = value

    def extract_text(self, image_path: str, language: str = "eng") -> str:
        start = time.time()
        text = ""

        if self._engine_name == "tesseract":
            text = self._extract_tesseract(image_path, language)
        elif self._engine_name == "easyocr":
            text = self._extract_easyocr(image_path, language)
        else:
            text = self._extract_tesseract(image_path, language)

        elapsed = time.time() - start
        logger.info("OCR (%s) extracted %d chars in %.2fs", self._engine_name, len(text), elapsed)
        return text

    def _extract_tesseract(self, image_path: str, language: str = "eng") -> str:
        try:
            import pytesseract
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang=language, config="--oem 3 --psm 6")
            return text.strip()
        except ImportError:
            logger.error("pytesseract not installed")
            raise
        except Exception as e:
            logger.error("Tesseract OCR failed: %s", e)
            raise

    def _extract_easyocr(self, image_path: str, language: str = "en") -> str:
        try:
            import easyocr
            if self._easyocr is None:
                self._easyocr = easyocr.Reader([language], gpu=False)
            results = self._easyocr.readtext(image_path, detail=0)
            return "\n".join(results).strip()
        except ImportError:
            logger.error("easyocr not installed")
            raise
        except Exception as e:
            logger.error("EasyOCR failed: %s", e)
            raise

    def extract_from_pdf_page(self, pdf_path: str, page_num: int = 0,
                              language: str = "eng") -> str:
        try:
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(pdf_path)
            page = pdf[page_num]
            bitmap = page.render(scale=2)
            img_bytes = bitmap.encode("png")
            pdf.close()

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(img_bytes)
                tmp_path = tmp.name

            text = self.extract_text(tmp_path, language)
            Path(tmp_path).unlink(missing_ok=True)
            return text

        except ImportError:
            logger.warning("pypdfium2 not available for OCR PDF pages")
            raise
        except Exception as e:
            logger.error("PDF page OCR failed: %s", e)
            raise

    def preprocess_image(self, image_path: str) -> str:
        try:
            img = Image.open(image_path)
            if img.mode != "RGB":
                img = img.convert("RGB")

            img = img.rotate(self._detect_skew(img), expand=True, fillcolor="white")

            processed_path = image_path
            if image_path.lower().endswith((".tiff", ".tif", ".bmp")):
                processed_path = str(Path(image_path).with_suffix(".png"))
                img.save(processed_path, "PNG")

            return processed_path
        except Exception as e:
            logger.error("Image preprocessing failed: %s", e)
            return image_path

    def _detect_skew(self, image: Image.Image) -> float:
        try:
            import pytesseract
            import math

            osd = pytesseract.image_to_osd(image)
            for line in osd.split("\n"):
                if "Rotate" in line:
                    angle = float(line.split(":")[-1].strip())
                    return -angle if angle > 180 else -angle
            return 0.0
        except Exception:
            return 0.0
