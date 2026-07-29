"""Claude API client implementation."""

import json
import logging
from typing import Any

import requests

from ai.base_client import AIBaseClient


logger = logging.getLogger(__name__)


class ClaudeClient(AIBaseClient):
    BASE_URL = "https://api.anthropic.com/v1"

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        super().__init__(api_key, model)

    def name(self) -> str:
        return f"Claude ({self.model})"

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.1) -> str:
        system_msg = ""
        clean_messages = []
        for m in messages:
            if m["role"] == "system":
                system_msg += m["content"] + "\n"
            else:
                clean_messages.append(m)

        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": clean_messages,
            "temperature": temperature,
        }
        if system_msg:
            payload["system"] = system_msg.strip()

        resp = requests.post(
            f"{self.BASE_URL}/messages",
            headers=self._headers(),
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]

    def extract_fields(self, text: str, fields: list[str]) -> dict[str, Any]:
        fields_str = ", ".join(fields)
        prompt = f"""Extract the following fields from the document text below.
Return ONLY valid JSON (no markdown, no code blocks).

Fields to extract: {fields_str}

For each field, return:
- "value": the extracted value (or null if not found)
- "confidence": a float between 0.0 and 1.0
- "reasoning": brief explanation

Also include "items" array if line items/products are present.

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
        except json.JSONDecodeError:
            try:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(response[start:end])
            except (json.JSONDecodeError, ValueError):
                pass
            return {f: {"value": None, "confidence": 0.0, "reasoning": "Parse failed"} for f in fields}
