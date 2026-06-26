from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_token
from app.models import User


def _extract_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    token = _extract_bearer(authorization)
    user_id = decode_token(token, "access") if token else None
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_current_user_optional(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    token = _extract_bearer(authorization)
    if not token:
        return None
    user_id = decode_token(token, "access")
    if user_id is None:
        return None
    return db.get(User, user_id)


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return user
