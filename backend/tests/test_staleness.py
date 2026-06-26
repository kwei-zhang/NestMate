from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import httpx

from app.models import Listing
from app.services.staleness import check_listing


def _make(db, **kwargs) -> Listing:
    base = dict(
        source="xhs",
        source_url="https://www.xiaohongshu.com/explore/x",
        raw_text="原始正文",
        status="published",
        published_at=datetime.now(UTC),
    )
    base.update(kwargs)
    listing = Listing(**base)
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def _resp(status_code=200, headers=None, text=""):
    return httpx.Response(status_code, headers=headers or {}, text=text)


def test_404_archives_as_deleted(db_session):
    listing = _make(db_session)
    with patch("app.services.staleness._fetch", return_value=_resp(404)):
        outcome = check_listing(db_session, listing)
    assert outcome == "archived_deleted"
    assert listing.status == "archived"
    assert listing.deleted_at_source is True


def test_last_modified_change_triggers_ai_stale(db_session):
    old = datetime(2026, 1, 1, tzinfo=UTC)
    listing = _make(db_session, source_last_modified=old)
    headers = {"Last-Modified": "Wed, 01 Jun 2026 00:00:00 GMT"}
    with patch("app.services.staleness._fetch", return_value=_resp(200, headers, "已找到室友")), patch(
        "app.services.staleness.judge_staleness", return_value=(True, "STALE: found")
    ):
        outcome = check_listing(db_session, listing)
    assert outcome == "archived_stale"
    assert listing.status == "archived"


def test_last_modified_change_info_update(db_session):
    from app.schemas.listing import ExtractedListing

    old = datetime(2026, 1, 1, tzinfo=UTC)
    listing = _make(db_session, source_last_modified=old)
    headers = {"Last-Modified": "Wed, 01 Jun 2026 00:00:00 GMT"}
    with patch("app.services.staleness._fetch", return_value=_resp(200, headers, "新预算1500")), patch(
        "app.services.staleness.judge_staleness", return_value=(False, "ACTIVE")
    ), patch(
        "app.services.staleness.extract_listing",
        return_value=ExtractedListing(budget_max=1500),
    ):
        outcome = check_listing(db_session, listing)
    assert outcome == "updated"
    assert listing.status == "published"
    assert listing.budget_max == 1500
    assert listing.check_state == "ok"


def test_expired_after_one_month(db_session):
    old = datetime.now(UTC) - timedelta(days=40)
    listing = _make(db_session, source_url=None, published_at=old)
    outcome = check_listing(db_session, listing)
    assert outcome == "archived_expired"
    assert listing.status == "archived"


def test_network_failure_does_not_delete(db_session):
    listing = _make(db_session)
    with patch("app.services.staleness._fetch", return_value=None):
        outcome = check_listing(db_session, listing)
    assert outcome == "unreachable"
    assert listing.status == "published"
