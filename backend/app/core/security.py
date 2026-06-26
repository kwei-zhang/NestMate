from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from jose import JWTError, jwt

from app.core.config import settings

TokenType = Literal["access", "refresh"]


def _create_token(subject: str, token_type: TokenType, ttl: timedelta) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: int) -> str:
    return _create_token(str(user_id), "access", timedelta(minutes=settings.jwt_access_ttl_min))


def create_refresh_token(user_id: int) -> str:
    return _create_token(str(user_id), "refresh", timedelta(days=settings.jwt_refresh_ttl_days))


def decode_token(token: str, expected_type: TokenType) -> int | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
    if payload.get("type") != expected_type:
        return None
    sub = payload.get("sub")
    if sub is None:
        return None
    try:
        return int(sub)
    except (TypeError, ValueError):
        return None
