"""Encryption service for API keys and sensitive data."""

import base64
import hashlib
import logging
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


logger = logging.getLogger(__name__)


class EncryptionService:
    _instance: Optional["EncryptionService"] = None
    _fernet: Optional[Fernet] = None
    _salt: bytes = b"ai_doc_extractor_salt_2024"

    def __new__(cls) -> "EncryptionService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, password: Optional[str] = None) -> None:
        if self._fernet is not None:
            return
        key = self._derive_key(password)
        self._fernet = Fernet(key)
        logger.debug("Encryption service initialized")

    def _derive_key(self, password: Optional[str] = None) -> bytes:
        if password is None:
            machine_id = self._get_machine_id()
            password = f"ai_doc_extractor_default_{machine_id}"

        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=self._salt, iterations=600000)
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def _get_machine_id(self) -> str:
        try:
            import uuid
            return str(uuid.uuid4())
        except Exception:
            return "default_machine_id"

    def encrypt(self, plaintext: str) -> str:
        if self._fernet is None:
            self.initialize()
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        if self._fernet is None:
            self.initialize()
        return self._fernet.decrypt(ciphertext.encode()).decode()

    @staticmethod
    def hash_file(file_path: str) -> str:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def hash_string(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()
