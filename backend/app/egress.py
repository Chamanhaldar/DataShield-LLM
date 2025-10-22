from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status

from .detector import detect_and_tokenize


async def sanitize_output(
    llm_output: str,
    token_map: dict[str, dict[str, str]],
    policy: str,
) -> tuple[str, bool, list[dict[str, Any]]]:
    sanitized = llm_output
    for placeholder, data in token_map.items():
        sanitized = sanitized.replace(placeholder, data["synthetic"])

    masked_output, leak_map = await detect_and_tokenize(sanitized)
    leakage = bool(leak_map)
    leak_details: list[dict[str, Any]] = []
    if leakage:
        for placeholder, info in leak_map.items():
            leak_details.append({"placeholder": placeholder, "info": info})
        if policy == "block-on-leak":
            raise HTTPException(
                status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS,
                detail="Sensitive data leakage prevented",
            )
        sanitized = masked_output

    return sanitized, leakage, leak_details
