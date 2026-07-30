"""AI provider abstract base and factory."""

# Re-export AIBaseClient from its canonical module so that
# both `from ai import AIBaseClient` and
# `from ai.base_client import AIBaseClient` resolve to the same class.
from ai.base_client import AIBaseClient  # noqa: F401

__all__ = ["AIBaseClient"]
