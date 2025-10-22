from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from . import detector, egress, llm, models, vault  # noqa: F401
from .audit import audit_log
from .auth import UserContext, get_current_user, require_scope
from .config import get_settings
from .database import Base, engine, get_session
from .schemas import InferenceRequest, InferenceResponse, TokenMappingDetail

settings = get_settings()
logging.basicConfig(level=settings.log_level)

app = FastAPI(title=settings.project_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
    allow_origins=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/healthz", tags=["health"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post(f"{settings.api_prefix}/inference", response_model=InferenceResponse)
async def inference(
    request: InferenceRequest,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> InferenceResponse:
    if request.policy not in settings.allowed_policies:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported policy")

    masked_text, token_map = await detector.detect_and_tokenize(request.input_text)

    secret_id: str | None = None
    if token_map:
        secret_id = await vault.store_tokens(request.session_id, token_map, user, db)

    llm_response = await llm.call_llm(masked_text, request.policy)
    sanitized_output, leak, leak_details = await egress.sanitize_output(llm_response, token_map, request.policy)

    audit_log(
        user,
        request.model_dump(),
        masked_input=masked_text,
        output=sanitized_output,
        leak_detected=leak,
        secret_id=secret_id,
        leak_details=leak_details,
    )

    return InferenceResponse(response=sanitized_output, secret_id=secret_id if not leak else None, leak_detected=leak)


@app.get(f"{settings.api_prefix}/secret/{{secret_id}}", response_model=TokenMappingDetail)
async def get_secret(
    secret_id: str,
    user: UserContext = Depends(require_scope("view")),
    db: AsyncSession = Depends(get_session),
) -> TokenMappingDetail:
    entry, mapping = await vault.retrieve_tokens(secret_id, user, db)
    return TokenMappingDetail(
        secret_id=str(entry.id),
        session_id=entry.session_id,
        owner_id=entry.owner_id,
        created_at=entry.created_at,
        detector_metadata=entry.detector_metadata,
        mapping=mapping,
    )
