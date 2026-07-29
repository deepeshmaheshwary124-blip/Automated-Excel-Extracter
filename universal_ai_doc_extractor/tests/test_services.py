"""Tests for PDF and document services."""

import os
import tempfile
from pathlib import Path

import pytest
from PyPDF2 import PdfWriter

from services.pdf_service import PDFService
from services.document_service import DocumentService


class TestPDFService:
    def setup_method(self):
        self.service = PDFService()

    def create_test_pdf(self, text: str) -> str:
        writer = PdfWriter()
        writer.add_blank_page(612, 792)
        writer.add_blank_page(612, 792)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            writer.write(f.name)
            return f.name

    def test_get_page_count(self):
        path = self.create_test_pdf("Test")
        count = self.service.get_page_count(path)
        assert count == 2
        Path(path).unlink(missing_ok=True)

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            self.service.extract_text("/nonexistent/file.pdf")


class TestDocumentService:
    def setup_method(self):
        self.service = DocumentService()

    def test_unsupported_format(self):
        path = "/tmp/test.xyz"
        Path(path).write_text("test")
        try:
            with pytest.raises(ValueError):
                self.service.extract_text(path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_text_file(self):
        path = "/tmp/test_doc.txt"
        Path(path).write_text("Invoice #123\nTotal: $100", encoding="utf-8")
        try:
            text = self.service.extract_text(path)
            assert "Invoice #123" in text
        finally:
            Path(path).unlink(missing_ok=True)

    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            self.service.extract_text("/nonexistent/file.pdf")
