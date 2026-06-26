from datetime import date
from unittest.mock import MagicMock, patch

from app.models import Listing
from app.schemas.listing import ExtractedListing
from app.services.ai_extract import extract_listing
from app.services.listing_service import apply_extraction


def test_extract_injects_current_date_into_prompt():
    fake_client = MagicMock()
    parsed = ExtractedListing(title="x")
    fake_client.beta.chat.completions.parse.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(parsed=parsed))]
    )
    with patch("openai.OpenAI", return_value=fake_client):
        extract_listing("7月1号入住 求室友")

    messages = fake_client.beta.chat.completions.parse.call_args.kwargs["messages"]
    system = messages[0]["content"]
    # Today's date (hence the current year) must be in the system prompt so the
    # model can default a year-less date to the current year.
    assert date.today().isoformat() in system
    assert str(date.today().year) in system


def test_apply_extraction_copies_highlights():
    listing = Listing(source="xhs", raw_text="...")
    extracted = ExtractedListing(
        title="北约克招租",
        intent="offering",
        highlights=["🚭 不抽烟", "🍃 不吸大麻", "🚫 不带异性回家"],
    )
    apply_extraction(listing, extracted)
    assert listing.title == "北约克招租"
    assert listing.highlights == ["🚭 不抽烟", "🍃 不吸大麻", "🚫 不带异性回家"]
    assert listing.extracted_json["intent"] == "offering"
