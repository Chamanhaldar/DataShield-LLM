from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class InferenceRequest(BaseModel):
    session_id: str = Field(min_length=3, max_length=128)
    input_text: str = Field(min_length=1, max_length=16000)
    policy: str = Field(default="default")


class InferenceResponse(BaseModel):
    response: str
    secret_id: str | None = None
    leak_detected: bool = False


class LeakEvent(BaseModel):
    blocked_output: str
    leak_details: list[dict[str, Any]]


class TokenMappingRead(BaseModel):
    secret_id: str
    session_id: str
    owner_id: str
    created_at: datetime
    detector_metadata: dict[str, Any]

    class Config:
        from_attributes = True


class TokenMappingDetail(TokenMappingRead):
    mapping: dict[str, dict[str, str]]
