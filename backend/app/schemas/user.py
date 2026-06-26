from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider: str
    email: str | None
    display_name: str | None
    avatar_url: str | None
    role: str
    created_at: datetime


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str


class FavoriteIn(BaseModel):
    personal_status: str | None = None
    note: str | None = None


class FavoriteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    listing_id: int
    personal_status: str
    note: str | None
    created_at: datetime
