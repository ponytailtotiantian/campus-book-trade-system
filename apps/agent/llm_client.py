"""Thin DeepSeek OpenAI-compatible client wrapper."""
from __future__ import annotations

import logging
import os
from typing import Any


logger = logging.getLogger(__name__)

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"


class DeepSeekConfigurationError(RuntimeError):
    """Raised when required DeepSeek configuration is missing."""


class DeepSeekRuntimeError(RuntimeError):
    """Raised when the DeepSeek client cannot be initialized."""


class DeepSeekAPIError(RuntimeError):
    """Raised when the DeepSeek API call fails."""


class DeepSeekClient:
    """Reads DeepSeek settings from environment variables and wraps OpenAI client."""

    def __init__(self) -> None:
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        self.model = os.getenv("DEEPSEEK_MODEL", DEFAULT_DEEPSEEK_MODEL).strip()
        if not self.model:
            self.model = DEFAULT_DEEPSEEK_MODEL
        self._client: Any | None = None

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = self._build_client()
        return self._client

    def _build_client(self) -> Any:
        if not self.api_key:
            raise DeepSeekConfigurationError("DEEPSEEK_API_KEY is not configured.")
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - depends on environment setup
            raise DeepSeekRuntimeError("openai package is not installed.") from exc
        return OpenAI(api_key=self.api_key, base_url=DEEPSEEK_BASE_URL, timeout=30.0)

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> Any:
        if not self.api_key:
            raise DeepSeekConfigurationError("DEEPSEEK_API_KEY is not configured.")

        kwargs: dict[str, Any] = {"model": self.model, "messages": messages}
        if tools:
            kwargs["tools"] = tools

        try:
            return self.client.chat.completions.create(**kwargs)
        except DeepSeekConfigurationError:
            raise
        except Exception as exc:
            logger.warning("DeepSeek API call failed: %s", exc)
            raise DeepSeekAPIError(str(exc)) from exc
