"""AI-powered document extraction service."""

import json
import logging
import time
from typing import Any, Optional

from ai.factory import AIClientFactory
from ai.extraction_parser import ExtractionParser
from ai.prompt_templates import (
    EXTRACTION_SYSTEM_PROMPT,
    CHAT_SYSTEM_PROMPT,
    JOURNAL_ENTRY_PROMPT,
    SUMMARIZE_PROMPT,
)
from config.constants import FIELD_DEFINITIONS, HEADER_FIELDS
from database.repositories import (
    ActivityLogRepository,
    AIConversationRepository,
    ExtractionRepository,
    DocumentRepository,
)
from models.enums import LogCategory


logger = logging.getLogger(__name__)


class AIService:
    def __init__(self) -> None:
        self.log_repo = ActivityLogRepository()
        self.conv_repo = AIConversationRepository()
        self.extraction_repo = ExtractionRepository()
        self.doc_repo = DocumentRepository()
        self._current_session: Optional[str] = None

    @property
    def current_session(self) -> str:
        if self._current_session is None:
            import uuid
            self._current_session = str(uuid.uuid4())
        return self._current_session

    def extract_from_text(self, text: str, provider: str = "openai",
                          model: str = "") -> dict[str, Any]:
        start = time.time()
        client = AIClientFactory.create_client(provider, model)
        if client is None:
            raise ValueError(f"No client available for provider: {provider}")

        fields_to_extract = HEADER_FIELDS + ["items"]
        raw_result = client.extract_fields(text, fields_to_extract)
        parsed = ExtractionParser.parse_ai_response(raw_result)

        elapsed = int((time.time() - start) * 1000)
        self.log_repo.log(
            "ai_extraction",
            LogCategory.AI_REQUEST.value,
            f"Extracted {len(parsed['fields'])} fields via {client.name()}",
            elapsed,
        )

        return parsed

    def chat(self, message: str, provider: str = "openai",
             model: str = "", history: Optional[list[dict]] = None) -> str:
        start = time.time()
        client = AIClientFactory.create_client(provider, model)
        if client is None:
            return "AI provider not configured. Please set up an API key in Settings."

        messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
        if history:
            messages.extend(history[-20:])
        messages.append({"role": "user", "content": message})

        try:
            response = client.chat(messages, temperature=0.3)
        except Exception as e:
            logger.error("AI chat failed: %s", e)
            return f"Sorry, I encountered an error: {str(e)}"

        elapsed = int((time.time() - start) * 1000)
        self.conv_repo.add_message(
            self.current_session, "user", message, client.name(), 0, elapsed
        )
        self.conv_repo.add_message(
            self.current_session, "assistant", response, client.name(), 0, elapsed
        )
        self.log_repo.log(
            "ai_chat", LogCategory.AI_REQUEST.value,
            f"Chat with {client.name()}", elapsed,
        )

        return response

    def create_journal_entry(self, description: str, provider: str = "openai",
                             model: str = "") -> dict[str, Any]:
        client = AIClientFactory.create_client(provider, model)
        if client is None:
            return {"error": "AI not configured"}

        prompt = JOURNAL_ENTRY_PROMPT.format(description=description)
        response = client.chat([
            {"role": "system", "content": "You create journal entries. Return only JSON."},
            {"role": "user", "content": prompt},
        ])

        try:
            response = response.strip()
            if response.startswith("```"):
                response = response.split("\n", 1)[-1].rsplit("```", 1)[0]
            return json.loads(response)
        except (json.JSONDecodeError, ValueError):
            return {"error": "Failed to parse journal entry", "raw": response}

    def summarize(self, data: str, provider: str = "openai",
                  model: str = "") -> str:
        client = AIClientFactory.create_client(provider, model)
        if client is None:
            return "AI not configured"

        prompt = SUMMARIZE_PROMPT.format(data=data[:10000])
        return client.chat([
            {"role": "system", "content": "You summarize financial data concisely."},
            {"role": "user", "content": prompt},
        ])
