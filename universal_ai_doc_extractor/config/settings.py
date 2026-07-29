"""Centralized settings manager with JSON persistence."""

import json
import logging
from pathlib import Path
from typing import Any, Optional

from config.constants import get_config_path, AppConfig


logger = logging.getLogger(__name__)


class Settings:
    _instance: Optional["Settings"] = None
    _config: AppConfig
    _dirty: bool = False
    _extra: dict[str, Any] = {}

    def __new__(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._config = AppConfig()
        self._extra = {}
        self._load()
        logger.info("Settings initialized")

    def _load(self) -> None:
        config_path = get_config_path()
        if not config_path.exists():
            self.save()
            return
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            config_data = {}
            extra_data = {}
            for key, value in data.items():
                if hasattr(self._config, key):
                    config_data[key] = value
                else:
                    extra_data[key] = value
            self._config = AppConfig(**config_data)
            self._extra = extra_data
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("Failed to load config, using defaults: %s", e)

    def save(self) -> None:
        config_path = get_config_path()
        data = self._config.model_dump()
        data.update(self._extra)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            json.dumps(data, indent=2, default=str), encoding="utf-8"
        )
        self._dirty = False

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self._config, key):
            return getattr(self._config, key)
        return self._extra.get(key, default)

    def set(self, key: str, value: Any) -> None:
        if hasattr(self._config, key):
            setattr(self._config, key, value)
        else:
            self._extra[key] = value
        self._dirty = True

    def get_all(self) -> dict[str, Any]:
        data = self._config.model_dump()
        data.update(self._extra)
        return data

    @property
    def theme(self) -> str:
        return self._config.theme

    @theme.setter
    def theme(self, value: str) -> None:
        self._config.theme = value
        self._dirty = True

    @property
    def ai_provider(self) -> str:
        return self._config.ai_provider

    @ai_provider.setter
    def ai_provider(self, value: str) -> None:
        self._config.ai_provider = value
        self._dirty = True

    @property
    def ocr_engine(self) -> str:
        return self._config.ocr_engine

    @ocr_engine.setter
    def ocr_engine(self, value: str) -> None:
        self._config.ocr_engine = value
        self._dirty = True
