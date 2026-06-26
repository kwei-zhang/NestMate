"""AI extraction of structured roommate-listing fields from raw post text.

Uses OpenAI Structured Outputs (JSON Schema derived from the Pydantic
ExtractedListing model). Missing fields are returned as null — the model is
instructed not to invent values. Results are always human-reviewed before
publishing.
"""
from __future__ import annotations

from app.core.config import settings
from app.schemas.listing import ExtractedListing

SYSTEM_PROMPT = (
    "You extract structured roommate/rental information from Chinese-language "
    "social posts (mainly from 小红书) about housing in Toronto / the GTA / Ontario.\n"
    "Rules:\n"
    "- Distinguish intent: 'offering' = the poster has a room/place to rent out (招租); "
    "'seeking' = the poster is looking for a room/roommate (求租).\n"
    "- has_room = true only when the poster actually has a place available.\n"
    "- Recognize MBTI types (e.g. INFP, ESTJ) when mentioned.\n"
    "- Budgets are monthly in CAD; parse ranges into budget_min/budget_max.\n"
    "- area: normalize to common GTA areas like North York, Scarborough, Downtown, "
    "Markham, Richmond Hill, Waterloo, Mississauga when possible.\n"
    "- Extract contact info: contact_type one of wechat|phone|xhs|email and contact_value.\n"
    "- If a field is not present, return null. Never guess."
)


def extract_listing(raw_text: str, source_url: str | None = None) -> ExtractedListing:
    """Call OpenAI to extract structured fields. Returns ExtractedListing."""
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    user_content = raw_text if not source_url else f"链接: {source_url}\n\n{raw_text}"

    completion = client.beta.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        response_format=ExtractedListing,
        temperature=0,
    )
    parsed = completion.choices[0].message.parsed
    return parsed or ExtractedListing()


def judge_staleness(old_text: str, new_text: str) -> tuple[bool, str]:
    """Given old and new versions of a post, decide if the listing is now stale
    (roommate found / no longer available). Returns (is_stale, reason)."""
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    completion = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You compare two versions of a Chinese roommate/rental post. "
                    "Decide whether the listing is now inactive — e.g. the room is taken, "
                    "a roommate was found, or the post says it's closed (已找到/已出租/已删除). "
                    "Respond with exactly 'STALE: <reason>' or 'ACTIVE: <reason>'."
                ),
            },
            {"role": "user", "content": f"OLD:\n{old_text}\n\nNEW:\n{new_text}"},
        ],
        temperature=0,
    )
    text = (completion.choices[0].message.content or "").strip()
    is_stale = text.upper().startswith("STALE")
    return is_stale, text
