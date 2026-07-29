"""AI client factory - creates appropriate client based on provider."""

import logging
from typing import Optional

from ai.base_client import AIBaseClient
from ai.openai_client import OpenAIClient
from ai.claude_client import ClaudeClient
from ai.gemini_client import GeminiClient
from ai.openrouter_client import OpenRouterClient
from ai.ollama_client import OllamaClient
from services.encryption_service import EncryptionService
from database.repositories import SettingsStoreRepository


logger = logging.getLogger(__name__)


class AIClientFactory:
    _clients: dict[str, AIBaseClient] = {}

    @staticmethod
    def create_client(provider: str, model: str = "") -> Optional[AIBaseClient]:
        cache_key = f"{provider}:{model}"
        if cache_key in AIClientFactory._clients:
            return AIClientFactory._clients[cache_key]

        encryption = EncryptionService()
        settings_repo = SettingsStoreRepository()

        encrypted_key = settings_repo.get(f"api_key_{provider}")
        if not encrypted_key:
            logger.warning("No API key found for provider: %s", provider)
            return None

        try:
            api_key = encryption.decrypt(encrypted_key["value"])
        except Exception as e:
            logger.error("Failed to decrypt API key for %s: %s", provider, e)
            return None

        client: Optional[AIBaseClient] = None
        if provider == "openai":
            client = OpenAIClient(api_key, model or "gpt-4o")
        elif provider == "claude":
            client = ClaudeClient(api_key, model or "claude-3-opus-20240229")
        elif provider == "gemini":
            client = GeminiClient(api_key, model or "gemini-1.5-pro")
        elif provider == "openrouter":
            client = OpenRouterClient(api_key, model or "openai/gpt-4o")
        elif provider == "ollama":
            client = OllamaClient("", model or "llama3")
        else:
            logger.error("Unknown AI provider: %s", provider)
            return None

        AIClientFactory._clients[cache_key] = client
        return client

    @staticmethod
    def clear_cache() -> None:
        AIClientFactory._clients.clear()
