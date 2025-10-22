from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from .config import get_settings

_settings = get_settings()
_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI | None:
    global _client
    if _settings.openai_api_key is None:
        return None
    if _client is None:
        _client = AsyncOpenAI(api_key=_settings.openai_api_key)
    return _client


async def call_llm(prompt: str, policy: str) -> str:
    client = _get_client()
    if client is None:
        return f"[MOCK_RESPONSE] {prompt}"

    response: Any = await client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        extra_headers={"x-sentinel-policy": policy},
    )
    if hasattr(response, "output_text"):
        return response.output_text
    candidate = getattr(response, "output", None)
    return str(candidate)
