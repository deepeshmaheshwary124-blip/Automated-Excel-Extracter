"""Gemini API client implementation."""

import json
import logging
from typing import Any

import requests

from ai.base_client import AIBaseClient


logger = logging.getLogger(__name__)


class GeminiClient(AIBaseClient):
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        super().__init__(api_key, model)

    def name(self) -> str:
        return f"Gemini ({self.model})"

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.1) -> str:
        parts = []
        for m in messages:
            parts.append({"text": f"[{m['role']}]: {m['content']}"})

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": 4096},
        }

        resp = requests.post(
            f"{self.BASE_URL}/models/{self.model}:generateContent?key={self.api_key}",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def extract_fields(self, text: str, fields: list[str]) -> dict[str, Any]:
        fields_str = ", ".join(fields)
        prompt = f"""Extract the following fields from the document text below.
Return ONLY valid JSON (no markdown, no code blocks).

Fields to extract: {fields_str}

For each field, return value, confidence (0-1), and reasoning.
Include items array for line items.

Document text:
{text[:15000]}"""

        return self._parse_response(
            self.chat([
                {"role": "user", "content": prompt},
            ], temperature=0.05),
            fields,
        )

    def _parse_response(self, response: str, fields: list[str]) -> dict[str, Any]:
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[-1]
            response = response.rsplit("```", 1)[0]
        try:
            return json.loads(response)
        except (json.JSONDecodeError, ValueError):
            try:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(response[start:end])
            except (json.JSONDecodeError, ValueError):
                pass
            return {f: {"value": None, "confidence": 0.0} for f in fields}
