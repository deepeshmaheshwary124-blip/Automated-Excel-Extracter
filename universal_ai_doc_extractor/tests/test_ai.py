"""Tests for AI extraction parser."""

import json

import pytest

from ai.extraction_parser import ExtractionParser


class TestExtractionParser:
    def test_parse_header_fields(self):
        response = {
            "invoice_number": {"value": "INV-001", "confidence": 0.95, "reasoning": "Found clearly"},
            "vendor": {"value": "Acme Corp", "confidence": 0.98, "reasoning": "Standard format"},
            "grand_total": 7352.41,
            "date": "2024-01-15",
        }

        parsed = ExtractionParser.parse_ai_response(response)
        assert parsed["fields"]["invoice_number"]["value"] == "INV-001"
        assert parsed["fields"]["vendor"]["value"] == "Acme Corp"
        assert parsed["fields"]["grand_total"]["value"] == 7352.41
        assert parsed["fields"]["date"]["value"] == "2024-01-15"

    def test_parse_items(self):
        response = {
            "items": [
                {
                    "product_name": {"value": "Web Development", "confidence": 0.9},
                    "quantity": 40,
                    "unit_price": 150,
                    "line_total": 6000,
                },
                {
                    "product_name": "Cloud Hosting",
                    "quantity": 1,
                    "unit_price": 500,
                },
            ]
        }

        parsed = ExtractionParser.parse_ai_response(response)
        assert len(parsed["items"]) == 2
        assert parsed["items"][0]["product_name"]["value"] == "Web Development"
        assert parsed["items"][1]["product_name"]["value"] == "Cloud Hosting"

    def test_low_confidence_detection(self):
        response = {
            "invoice_number": {"value": "INV-001", "confidence": 0.95},
            "vendor": {"value": "Unknown", "confidence": 0.45},
            "grand_total": {"value": "$100", "confidence": 0.60},
        }

        parsed = ExtractionParser.parse_ai_response(response)
        low = ExtractionParser.get_low_confidence_fields(parsed, 0.7)
        field_names = [f[0] for f in low]
        assert "vendor" in field_names
        assert "grand_total" in field_names

    def test_overall_confidence(self):
        response = {
            "invoice_number": {"value": "001", "confidence": 0.9},
            "vendor": {"value": "ACME", "confidence": 0.8},
            "date": {"value": "2024-01-01", "confidence": 0.7},
        }

        parsed = ExtractionParser.parse_ai_response(response)
        assert parsed["overall_confidence"] == pytest.approx(0.8, 0.1)

    def test_fields_to_extraction_dict(self):
        response = {
            "invoice_number": {"value": "INV-001", "confidence": 0.95},
            "vendor": {"value": "ACME", "confidence": 0.98},
        }

        parsed = ExtractionParser.parse_ai_response(response)
        d = ExtractionParser.fields_to_extraction_dict(parsed)
        assert d["invoice_number"] == "INV-001"
        assert d["vendor"] == "ACME"
        assert "confidence" in d
