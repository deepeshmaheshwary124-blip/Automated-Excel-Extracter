"""Tests for OCR service."""

import os
import tempfile
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from services.ocr_service import OCRService


class TestOCRService:
    def setup_method(self):
        self.ocr = OCRService("tesseract")

    def create_test_image(self, text: str) -> str:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img = Image.new("RGB", (400, 100), color="white")
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), text, fill="black")
            img.save(f.name)
            return f.name

    def test_image_preprocessing(self):
        path = self.create_test_image("Test")
        processed = self.ocr.preprocess_image(path)
        assert os.path.exists(processed)
        os.unlink(path)

    def test_ocr_engine_switch(self):
        assert self.ocr.engine_name == "tesseract"
        self.ocr.engine_name = "easyocr"
        assert self.ocr.engine_name == "easyocr"
