from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from .config import get_settings


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class UserContext:
    id: str
    roles: list[str]
    scopes: list[str]


class PolicyError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> UserContext:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")
    settings = get_settings()
    try:
        payload: dict[str, Any] = jwt.decode(
            credentials.credentials,
            settings.token_vault_key,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except jwt.PyJWTError as exc:  # type: ignore[attr-defined]
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    return UserContext(
        id=str(payload.get("sub")),
        roles=list(payload.get("roles", [])),
        scopes=list(payload.get("scopes", [])),
    )


def authorize(user: UserContext, action: str, resource_owner: str | None = None) -> None:
    scope = f"sanitize:{action}"
    if scope in user.scopes:
        if resource_owner and resource_owner != user.id and "admin" not in user.roles:
            raise PolicyError("Insufficient privileges for resource owner")
        return
    if "admin" in user.roles:
        return
    raise PolicyError("Access denied")


def require_scope(action: str) -> Callable[[UserContext], UserContext]:
    def dependency(user: UserContext = Depends(get_current_user)) -> UserContext:
        authorize(user, action)
        return user

    return dependency
