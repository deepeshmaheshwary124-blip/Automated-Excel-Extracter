"""AI provider abstract base and factory."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class AIBaseClient(ABC):
    def __init__(self, api_key: str, model: str = ""):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def chat(self, messages: list[dict[str, str]], temperature: float = 0.1) -> str:
        ...

    @abstractmethod
    def extract_fields(self, text: str, fields: list[str]) -> dict[str, Any]:
        ...

    @abstractmethod
    def name(self) -> str:
        ...
