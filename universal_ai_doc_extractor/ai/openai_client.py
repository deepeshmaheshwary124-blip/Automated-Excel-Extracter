"""OpenAI API client implementation."""

import json
import logging
import time
from typing import Any

import requests

from ai.base_client import AIBaseClient


logger = logging.getLogger(__name__)


class OpenAIClient(AIBaseClient):
    BASE_URL = "https://api.openai.com/v1"

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        super().__init__(api_key, model)

    def name(self) -> str:
        return f"OpenAI ({self.model})"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.1) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        resp = requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers=self._headers(),
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def extract_fields(self, text: str, fields: list[str]) -> dict[str, Any]:
        fields_str = ", ".join(fields)
        prompt = f"""Extract the following fields from the document text below.
Return ONLY valid JSON (no markdown, no code blocks).

Fields to extract: {fields_str}

For each field, return:
- "value": the extracted value (or null if not found)
- "confidence": a float between 0.0 and 1.0
- "reasoning": brief explanation

Also include "items" array if line items/products are present, each with:
product_name, sku, description, quantity, unit_price, line_total

Document text:
{text[:15000]}"""

        response = self.chat([
            {"role": "system", "content": "You are a precise document data extraction assistant. Return only valid JSON."},
            {"role": "user", "content": prompt},
        ], temperature=0.05)

        return self._parse_response(response, fields)

    def _parse_response(self, response: str, fields: list[str]) -> dict[str, Any]:
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[-1]
            response = response.rsplit("```", 1)[0]

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse AI response as JSON, trying to extract")
            try:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(response[start:end])
            except (json.JSONDecodeError, ValueError):
                pass

            return {f: {"value": None, "confidence": 0.0, "reasoning": "Parse failed"} for f in fields}
