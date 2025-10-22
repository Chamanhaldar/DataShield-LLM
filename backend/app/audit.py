from __future__ import annotations

import logging
from typing import Any

from .auth import UserContext

logger = logging.getLogger("sentinel.audit")


def audit_log(
    user: UserContext,
    payload: dict[str, Any],
    masked_input: str,
    output: str,
    leak_detected: bool,
    secret_id: str | None,
    leak_details: list[dict[str, Any]] | None = None,
) -> None:
    entry = {
        "user_id": user.id,
        "session_id": payload.get("session_id"),
        "policy": payload.get("policy"),
        "masked_input": masked_input,
        "output": output if not leak_detected else "[REDACTED]",
        "leak_detected": leak_detected,
        "secret_id": secret_id,
        "leak_details": leak_details or [],
    }
    logger.info("audit_event", extra={"audit": entry})
