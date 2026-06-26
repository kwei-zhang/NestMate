import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.deps import get_current_user
from app.models import User
from app.schemas.user import RefreshIn, TokenPair, UserOut
from app.services import oauth

router = APIRouter(prefix="/auth", tags=["auth"])

# NOTE: `state` should be persisted (e.g. signed cookie / cache) and verified in
# the callback for CSRF protection. Kept minimal here for the MVP.


@router.get("/google/login")
def google_login() -> RedirectResponse:
    state = secrets.token_urlsafe(16)
    return RedirectResponse(oauth.google_authorize_url(state))


@router.get("/wechat/login")
def wechat_login() -> RedirectResponse:
    state = secrets.token_urlsafe(16)
    return RedirectResponse(oauth.wechat_authorize_url(state))


def _issue_and_redirect(user: User) -> RedirectResponse:
    """Send the user back to the frontend with tokens in the URL fragment."""
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    frag = urlencode({"access_token": access, "refresh_token": refresh})
    return RedirectResponse(f"{settings.frontend_base}/auth/callback#{frag}")


@router.get("/google/callback")
def google_callback(
    code: str = Query(...), db: Session = Depends(get_db)
) -> RedirectResponse:
    profile = oauth.google_exchange(code)
    user = oauth.upsert_user(db, profile)
    return _issue_and_redirect(user)


@router.get("/wechat/callback")
def wechat_callback(
    code: str = Query(...), db: Session = Depends(get_db)
) -> RedirectResponse:
    profile = oauth.wechat_exchange(code)
    user = oauth.upsert_user(db, profile)
    return _issue_and_redirect(user)


@router.post("/refresh", response_model=TokenPair)
def refresh(body: RefreshIn) -> TokenPair:
    user_id = decode_token(body.refresh_token, "refresh")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return TokenPair(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user
