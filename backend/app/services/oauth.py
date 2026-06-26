"""Google + WeChat OAuth helpers and user upsert.

Both providers follow the same shape: redirect the browser to the provider's
authorize URL, then exchange the returned `code` for the user's profile. We then
upsert a local user keyed by (provider, provider_id) and issue our own JWTs.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import User


@dataclass
class OAuthProfile:
    provider: str
    provider_id: str
    email: str | None
    display_name: str | None
    avatar_url: str | None


def _redirect_uri(provider: str) -> str:
    return f"{settings.oauth_redirect_base}/auth/{provider}/callback"


# ---------------- Google ----------------

def google_authorize_url(state: str) -> str:
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": _redirect_uri("google"),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)


def google_exchange(code: str) -> OAuthProfile:
    token_resp = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": _redirect_uri("google"),
            "grant_type": "authorization_code",
        },
        timeout=10,
    )
    token_resp.raise_for_status()
    access_token = token_resp.json()["access_token"]
    info = httpx.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    info.raise_for_status()
    data = info.json()
    return OAuthProfile(
        provider="google",
        provider_id=data["sub"],
        email=data.get("email"),
        display_name=data.get("name"),
        avatar_url=data.get("picture"),
    )


# ---------------- WeChat (开放平台网站应用) ----------------

def wechat_authorize_url(state: str) -> str:
    params = {
        "appid": settings.wechat_appid,
        "redirect_uri": _redirect_uri("wechat"),
        "response_type": "code",
        "scope": "snsapi_login",
        "state": state,
    }
    return "https://open.weixin.qq.com/connect/qrconnect?" + urlencode(params) + "#wechat_redirect"


def wechat_exchange(code: str) -> OAuthProfile:
    token_resp = httpx.get(
        "https://api.weixin.qq.com/sns/oauth2/access_token",
        params={
            "appid": settings.wechat_appid,
            "secret": settings.wechat_secret,
            "code": code,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )
    token_resp.raise_for_status()
    token = token_resp.json()
    access_token = token["access_token"]
    openid = token["openid"]
    info = httpx.get(
        "https://api.weixin.qq.com/sns/userinfo",
        params={"access_token": access_token, "openid": openid},
        timeout=10,
    )
    info.raise_for_status()
    data = info.json()
    return OAuthProfile(
        provider="wechat",
        provider_id=data.get("unionid") or openid,
        email=None,
        display_name=data.get("nickname"),
        avatar_url=data.get("headimgurl"),
    )


# ---------------- Upsert ----------------

def upsert_user(db: Session, profile: OAuthProfile) -> User:
    user = db.scalar(
        select(User).where(
            User.provider == profile.provider, User.provider_id == profile.provider_id
        )
    )
    is_admin = bool(profile.email and profile.email.lower() in settings.admin_email_set)
    if user is None:
        user = User(
            provider=profile.provider,
            provider_id=profile.provider_id,
            email=profile.email,
            display_name=profile.display_name,
            avatar_url=profile.avatar_url,
            role="admin" if is_admin else "user",
        )
        db.add(user)
    else:
        # Refresh profile fields on each login
        user.email = profile.email or user.email
        user.display_name = profile.display_name or user.display_name
        user.avatar_url = profile.avatar_url or user.avatar_url
        if is_admin:
            user.role = "admin"
    db.commit()
    db.refresh(user)
    return user
