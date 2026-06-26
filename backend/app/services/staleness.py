"""Daily staleness check for published xhs-sourced listings.

Rules (per plan):
 1. Source URL returns 404/410  -> post deleted -> archive.
 2. Last-Modified changed       -> fetch body, let AI judge stale vs. info change.
 3. source_last_modified > 1 month old -> archive (fallback).
Network failures never auto-delete; they just leave last_checked_at updated.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models import Listing
from app.services.ai_extract import extract_listing, judge_staleness
from app.services.listing_service import apply_extraction

STALE_AFTER = timedelta(days=30)


def _as_aware(dt: datetime | None) -> datetime | None:
    """Normalize to timezone-aware UTC (DB backends like SQLite drop tzinfo)."""
    if dt is None:
        return None
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def _archive(listing: Listing, *, deleted: bool = False) -> None:
    listing.status = "archived"
    listing.check_state = "auto_archived"
    if deleted:
        listing.deleted_at_source = True


def _fetch(url: str) -> httpx.Response | None:
    try:
        return httpx.get(url, timeout=15, follow_redirects=True)
    except httpx.HTTPError:
        return None


def check_listing(db: Session, listing: Listing) -> str:
    """Run the staleness rules for one listing. Returns an outcome string."""
    now = datetime.now(UTC)
    listing.last_checked_at = now
    outcome = "ok"

    if listing.source_url:
        resp = _fetch(listing.source_url)
        if resp is None:
            db.commit()
            return "unreachable"  # do not delete on network failure
        if resp.status_code in (404, 410):
            _archive(listing, deleted=True)
            db.commit()
            return "archived_deleted"

        # Compare Last-Modified header against what we last saw.
        last_mod_header = resp.headers.get("Last-Modified")
        new_last_mod: datetime | None = None
        if last_mod_header:
            try:
                new_last_mod = parsedate_to_datetime(last_mod_header)
            except (TypeError, ValueError):
                new_last_mod = None

        prev_last_mod = _as_aware(listing.source_last_modified)
        changed = (
            new_last_mod is not None
            and prev_last_mod is not None
            and new_last_mod > prev_last_mod
        )
        if changed:
            listing.check_state = "changed_needs_ai"
            is_stale, _reason = judge_staleness(listing.raw_text, resp.text)
            if is_stale:
                _archive(listing)
                outcome = "archived_stale"
            else:
                # Info changed but still active: re-extract and refresh.
                extracted = extract_listing(resp.text, listing.source_url)
                apply_extraction(listing, extracted)
                listing.raw_text = resp.text
                listing.check_state = "ok"
                outcome = "updated"
            if new_last_mod:
                listing.source_last_modified = new_last_mod
            db.commit()
            return outcome
        if new_last_mod:
            listing.source_last_modified = new_last_mod

    # Fallback: too old.
    ref = _as_aware(listing.source_last_modified) or _as_aware(listing.published_at)
    if ref is not None and now - ref > STALE_AFTER:
        _archive(listing)
        outcome = "archived_expired"

    db.commit()
    return outcome


def hide_expired_native(db: Session) -> int:
    """Auto-hide published native posts not modified in over a month."""
    cutoff = datetime.now(UTC) - STALE_AFTER
    listings = db.scalars(
        select(Listing).where(Listing.status == "published", Listing.source == "native")
    ).all()
    hidden = 0
    for listing in listings:
        updated = _as_aware(listing.updated_at)
        if updated is not None and updated < cutoff:
            listing.status = "expired"
            hidden += 1
    db.commit()
    return hidden


def run_staleness_check() -> dict[str, int]:
    """Daily job: re-check xhs listings and auto-hide stale native posts."""
    counts: dict[str, int] = {}
    db = SessionLocal()
    try:
        listings = db.scalars(
            select(Listing).where(Listing.status == "published", Listing.source == "xhs")
        ).all()
        for listing in listings:
            outcome = check_listing(db, listing)
            counts[outcome] = counts.get(outcome, 0) + 1
        counts["native_expired"] = hide_expired_native(db)
    finally:
        db.close()
    return counts
