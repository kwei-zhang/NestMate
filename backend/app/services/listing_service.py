"""Helpers for turning extraction results into Listing column updates."""
from __future__ import annotations

from app.models import Listing
from app.schemas.listing import ExtractedListing

# Fields that map 1:1 from ExtractedListing onto Listing columns.
_EXTRACTED_FIELDS = (
    "title",
    "intent",
    "has_room",
    "mbti",
    "has_pets",
    "pets_note",
    "budget_min",
    "budget_max",
    "area",
    "move_in_date",
    "gender_pref",
    "contact_type",
    "contact_value",
)


def apply_extraction(listing: Listing, extracted: ExtractedListing) -> None:
    """Copy extracted fields onto the listing, keeping the full JSON for audit."""
    data = extracted.model_dump(mode="json")
    for field in _EXTRACTED_FIELDS:
        value = getattr(extracted, field)
        if value is not None:
            setattr(listing, field, value)
    listing.extracted_json = data
