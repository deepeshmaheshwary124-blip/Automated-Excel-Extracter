"""Abstract base class for all AI provider clients."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class AIBaseClient(ABC):
    """Abstract base for all AI provider clients."""

    def __init__(self, api_key: str, model: str = "") -> None:
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def chat(self, messages: list[dict[str, str]], temperature: float = 0.1) -> str:
        """Send a chat request and return the assistant reply."""
        ...

    @abstractmethod
    def extract_fields(self, text: str, fields: list[str]) -> dict[str, Any]:
        """Extract structured fields from document text and return raw JSON dict."""
        ...

    @abstractmethod
    def name(self) -> str:
        """Human-readable name including the model variant."""
        ...
