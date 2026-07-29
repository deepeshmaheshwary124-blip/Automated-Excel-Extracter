"""Ollama local model client implementation."""

import json
import logging
from typing import Any

import requests

from ai.base_client import AIBaseClient


logger = logging.getLogger(__name__)


class OllamaClient(AIBaseClient):
    BASE_URL = "http://localhost:11434"

    def __init__(self, api_key: str = "", model: str = "llama3"):
        super().__init__(api_key, model)

    def name(self) -> str:
        return f"Ollama (local: {self.model})"

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.1) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        resp = requests.post(
            f"{self.BASE_URL}/api/chat",
            json=payload,
            timeout=300,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]

    def extract_fields(self, text: str, fields: list[str]) -> dict[str, Any]:
        fields_str = ", ".join(fields)
        prompt = f"""Extract fields from document text. Return ONLY valid JSON.

Fields: {fields_str}

Each field: value, confidence (0-1), reasoning. Include items array.

Text:
{text[:10000]}"""

        return self._parse_response(
            self.chat([
                {"role": "system", "content": "You extract structured data. Return only JSON."},
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
