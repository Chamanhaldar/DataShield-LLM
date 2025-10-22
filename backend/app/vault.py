from __future__ import annotations

import json

from cryptography.fernet import Fernet
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import UserContext, authorize
from .config import get_settings
from .models import TokenMapping

_settings = get_settings()
fernet = Fernet(_settings.token_vault_key.encode())


async def store_tokens(
    session_id: str,
    mapping: dict[str, dict[str, str]],
    owner: UserContext,
    db: AsyncSession,
) -> str:
    payload = json.dumps(mapping)
    ciphertext = fernet.encrypt(payload.encode()).decode()
    metadata = {
        "count": len(mapping),
        "labels": sorted({item["label"] for item in mapping.values()}),
    }
    entry = TokenMapping(
        session_id=session_id,
        owner_id=owner.id,
        ciphertext=ciphertext,
        detector_metadata=metadata,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return str(entry.id)


async def retrieve_tokens(
    secret_id: str,
    user: UserContext,
    db: AsyncSession,
) -> tuple[TokenMapping, dict[str, dict[str, str]]]:
    try:
        token_id = int(secret_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid secret id") from exc
    result = await db.execute(select(TokenMapping).where(TokenMapping.id == token_id))
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret not found")
    authorize(user, "view", entry.owner_id)
    decrypted = fernet.decrypt(entry.ciphertext.encode()).decode()
    return entry, json.loads(decrypted)
