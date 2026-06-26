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
    move_in_date: date | None = Field(
        None,
        description="Desired move-in date (ISO). If no year is stated, assume the current year.",
    )
    gender_pref: str | None = Field(None, description="Gender preference if any")
    contact_type: str | None = Field(None, description="One of wechat|phone|xhs|email")
    contact_value: str | None = Field(None, description="The contact handle/number")
    highlights: list[str] = Field(
        default_factory=list,
        description=(
            "Short bullet points of lifestyle rules / key facts, each a concise phrase "
            "with a leading emoji when natural, e.g. '🚭 不抽烟', '🍃 不吸大麻', "
            "'🚫 不带异性回家', '🐱 有猫', '🚇 近地铁'."
        ),
    )


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
    highlights: list[str] | None
    images: list[str] | None
    contact_type: str | None  # type is fine to show; value is gated
    created_by: int | None  # so the frontend can show an "edit" button to the author
    created_at: datetime
    updated_at: datetime
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
    # Optional: if omitted, the backend tries to auto-fetch text from source_url.
    raw_text: str | None = None
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
    highlights: list[str] | None = None
    images: list[str] | None = None
    contact_type: str | None = None
    contact_value: str | None = None


class ListingEdit(BaseModel):
    """Fields an author may edit on their own post (title, content, tags, etc.).

    Excludes mbti (AI-derived) and intent (not used). All optional — only the
    provided fields are applied."""

    title: str | None = None
    raw_text: str | None = None
    area: str | None = None
    budget_min: int | None = None
    budget_max: int | None = None
    has_room: bool | None = None
    has_pets: bool | None = None
    pets_note: str | None = None
    move_in_date: date | None = None
    gender_pref: str | None = None
    highlights: list[str] | None = None
    images: list[str] | None = None
    contact_type: str | None = None
    contact_value: str | None = None


class NativePostIn(BaseModel):
    title: str | None = None
    raw_text: str
    intent: str | None = None
    has_room: bool | None = None
    # mbti is AI-extracted from raw_text, not a manual field.
    has_pets: bool | None = None
    pets_note: str | None = None
    budget_min: int | None = None
    budget_max: int | None = None
    area: str | None = None
    move_in_date: date | None = None
    gender_pref: str | None = None
    contact_type: str
    contact_value: str
    # URLs returned by POST /uploads/image (the user's own uploaded photos).
    images: list[str] = []
