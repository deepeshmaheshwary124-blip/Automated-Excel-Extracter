"""Parse AI extraction responses into structured extraction models."""

import json
import logging
from typing import Any, Optional

from config.constants import FIELD_DEFINITIONS, ITEM_FIELDS, HEADER_FIELDS


logger = logging.getLogger(__name__)


class ExtractionParser:
    @staticmethod
    def parse_ai_response(response: dict[str, Any]) -> dict[str, Any]:
        parsed = {
            "fields": {},
            "items": [],
            "overall_confidence": 0.0,
        }

        for field_name in HEADER_FIELDS:
            if field_name in response:
                field_data = response[field_name]
                if isinstance(field_data, dict):
                    parsed["fields"][field_name] = {
                        "value": field_data.get("value"),
                        "confidence": float(field_data.get("confidence", 0.0)),
                        "reasoning": field_data.get("reasoning", ""),
                    }
                else:
                    parsed["fields"][field_name] = {
                        "value": field_data,
                        "confidence": 0.8,
                        "reasoning": "Direct value",
                    }
            else:
                parsed["fields"][field_name] = {
                    "value": None,
                    "confidence": 0.0,
                    "reasoning": "Not found in document",
                }

        raw_items = response.get("items", [])
        if isinstance(raw_items, list):
            for item in raw_items:
                if isinstance(item, dict):
                    parsed_item = {}
                    for item_field in ITEM_FIELDS:
                        if item_field in item:
                            val = item[item_field]
                            if isinstance(val, dict):
                                parsed_item[item_field] = {
                                    "value": val.get("value"),
                                    "confidence": float(val.get("confidence", 0.8)),
                                }
                            else:
                                parsed_item[item_field] = {
                                    "value": val,
                                    "confidence": 0.8,
                                }
                    if parsed_item:
                        parsed["items"].append(parsed_item)

        confidences = [
            f["confidence"] for f in parsed["fields"].values()
            if f["confidence"] > 0
        ]
        if confidences:
            parsed["overall_confidence"] = sum(confidences) / len(confidences)

        return parsed

    @staticmethod
    def get_low_confidence_fields(parsed: dict[str, Any],
                                  threshold: float = 0.7) -> list[tuple[str, Any]]:
        low = []
        for field_name, field_data in parsed["fields"].items():
            if field_data["confidence"] < threshold:
                low.append((field_name, field_data))
        return low

    @staticmethod
    def fields_to_extraction_dict(parsed: dict[str, Any]) -> dict[str, Any]:
        result = {}
        for field_name, field_data in parsed["fields"].items():
            result[field_name] = field_data.get("value")
        result["items"] = parsed.get("items", [])
        result["confidence"] = parsed.get("overall_confidence", 0.0)
        return result
