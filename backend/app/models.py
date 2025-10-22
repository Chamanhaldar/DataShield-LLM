from datetime import datetime

from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class TokenMapping(Base):
    __tablename__ = "token_mappings"

    session_id: Mapped[str] = mapped_column(String(128), index=True)
    owner_id: Mapped[str] = mapped_column(String(64))
    ciphertext: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    detector_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
