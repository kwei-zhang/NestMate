from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ExtractedListing(BaseModel):
    """Structured output schema for OpenAI extraction."""

    title: str | None = Field(None, description="Short title summarizing the post")
    intent: str | None = Field(
        None, description="'offering' if renting out a room (招租), 'seeking' if looking for one (求租)"
    )
    has_room: bool | None = Field(None, description="True if the poster has a room/place available")
    mbti: str | None = Field(None, description="MBTI type if mentioned, e.g. INFP")
    has_pets: bool | None = Field(None, description="True if pets are present or allowed")
    pets_note: str | None = Field(None, description="Free text about pets")
    budget_min: int | None = Field(None, description="Min monthly budget in CAD")
    budget_max: int | None = Field(None, description="Max monthly budget in CAD")
    area: str | None = Field(None, description="Toronto/GTA area, e.g. North York, Scarborough")
    move_in_date: date | None = Field(None, description="Desired move-in date if mentioned")
    gender_pref: str | None = Field(None, description="Gender preference if any")
    contact_type: str | None = Field(None, description="One of wechat|phone|xhs|email")
    contact_value: str | None = Field(None, description="The contact handle/number")


class ListingPublic(BaseModel):
    """Public payload — never includes contact_value."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    source_url: str | None
    title: str | None
    raw_text: str
    status: str
    intent: str | None
    has_room: bool | None
    mbti: str | None
    has_pets: bool | None
    pets_note: str | None
    budget_min: int | None
    budget_max: int | None
    area: str | None
    move_in_date: date | None
    gender_pref: str | None
    contact_type: str | None  # type is fine to show; value is gated
    created_at: datetime
    published_at: datetime | None


class ListingAdmin(ListingPublic):
    """Admin/review payload — includes contact + staleness fields."""

    contact_value: str | None
    extracted_json: dict | None
    source_last_modified: datetime | None
    last_checked_at: datetime | None
    check_state: str
    deleted_at_source: bool


class ContactOut(BaseModel):
    contact_type: str | None
    contact_value: str | None


class IngestIn(BaseModel):
    source_url: str | None = None
    raw_text: str
    last_edited_at: datetime | None = None


class ListingUpdate(BaseModel):
    title: str | None = None
    intent: str | None = None
    has_room: bool | None = None
    mbti: str | None = None
    has_pets: bool | None = None
    pets_note: str | None = None
    budget_min: int | None = None
    budget_max: int | None = None
    area: str | None = None
    move_in_date: date | None = None
    gender_pref: str | None = None
    contact_type: str | None = None
    contact_value: str | None = None


class NativePostIn(BaseModel):
    title: str | None = None
    raw_text: str
    intent: str | None = None
    has_room: bool | None = None
    mbti: str | None = None
    has_pets: bool | None = None
    pets_note: str | None = None
    budget_min: int | None = None
    budget_max: int | None = None
    area: str | None = None
    move_in_date: date | None = None
    gender_pref: str | None = None
    contact_type: str
    contact_value: str
