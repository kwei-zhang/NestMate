from datetime import UTC, datetime, timedelta

from app.core.security import create_access_token
from app.models import User
from app.services.staleness import hide_expired_native


def _other_user_headers(db_session) -> dict[str, str]:
    other = User(provider="google", provider_id="g2", email="other@example.com")
    db_session.add(other)
    db_session.commit()
    db_session.refresh(other)
    return {"Authorization": f"Bearer {create_access_token(other.id)}"}


def test_author_can_edit_own_post(client, own_listing, auth_headers):
    resp = client.patch(
        f"/listings/{own_listing.id}",
        json={"title": "新标题", "raw_text": "改了内容", "highlights": ["🚭 不抽烟"]},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "新标题"
    assert body["raw_text"] == "改了内容"
    assert body["highlights"] == ["🚭 不抽烟"]


def test_non_author_cannot_edit(client, own_listing, db_session):
    resp = client.patch(
        f"/listings/{own_listing.id}",
        json={"title": "恶意修改"},
        headers=_other_user_headers(db_session),
    )
    assert resp.status_code == 403


def test_edit_requires_auth(client, own_listing):
    resp = client.patch(f"/listings/{own_listing.id}", json={"title": "x"})
    assert resp.status_code == 401


def _make_admin(db_session, user) -> dict[str, str]:
    user.role = "admin"
    db_session.commit()
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def test_admin_cannot_edit_native_post(client, own_listing, db_session, user):
    headers = _make_admin(db_session, user)
    resp = client.patch(
        f"/admin/listings/{own_listing.id}",
        json={"title": "admin 改的"},
        headers=headers,
    )
    assert resp.status_code == 403


def test_admin_can_hide_and_unhide(client, own_listing, db_session, user):
    headers = _make_admin(db_session, user)

    hide = client.post(f"/admin/listings/{own_listing.id}/hide", headers=headers)
    assert hide.status_code == 200
    assert hide.json()["status"] == "hidden"
    # Hidden posts disappear from the public list and detail.
    assert len(client.get("/listings").json()) == 0
    assert client.get(f"/listings/{own_listing.id}").status_code == 404

    unhide = client.post(f"/admin/listings/{own_listing.id}/unhide", headers=headers)
    assert unhide.status_code == 200
    assert unhide.json()["status"] == "published"
    assert len(client.get("/listings").json()) == 1


def test_my_listings_includes_hidden(client, own_listing, auth_headers, db_session):
    own_listing.status = "expired"
    db_session.commit()
    resp = client.get("/listings/mine", headers=auth_headers)
    assert resp.status_code == 200
    mine = resp.json()
    assert len(mine) == 1
    assert mine[0]["status"] == "expired"
    # ...but it stays out of the public list.
    assert len(client.get("/listings").json()) == 0


def test_author_can_republish_expired(client, own_listing, auth_headers, db_session):
    own_listing.status = "expired"
    db_session.commit()
    resp = client.post(f"/listings/{own_listing.id}/republish", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "published"


def test_cannot_republish_admin_hidden(client, own_listing, auth_headers, db_session):
    own_listing.status = "hidden"
    db_session.commit()
    resp = client.post(f"/listings/{own_listing.id}/republish", headers=auth_headers)
    assert resp.status_code == 400


def test_hide_expired_native_auto_hides_old_posts(db_session, own_listing):
    own_listing.updated_at = datetime.now(UTC) - timedelta(days=40)
    db_session.commit()
    n = hide_expired_native(db_session)
    assert n == 1
    db_session.refresh(own_listing)
    assert own_listing.status == "expired"


def test_hide_expired_native_keeps_fresh_posts(db_session, own_listing):
    own_listing.updated_at = datetime.now(UTC) - timedelta(days=5)
    db_session.commit()
    assert hide_expired_native(db_session) == 0


def test_admin_can_view_hidden_detail(client, own_listing, db_session, user):
    own_listing.status = "hidden"
    db_session.commit()
    headers = _make_admin(db_session, user)
    # Public/anon gets 404...
    assert client.get(f"/listings/{own_listing.id}").status_code == 404
    # ...admin can view it.
    resp = client.get(f"/listings/{own_listing.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "hidden"


def test_author_can_view_own_expired_detail(client, own_listing, db_session, auth_headers):
    own_listing.status = "expired"
    db_session.commit()
    resp = client.get(f"/listings/{own_listing.id}", headers=auth_headers)
    assert resp.status_code == 200


def test_admin_listings_lists_all_statuses(client, own_listing, db_session, user):
    own_listing.status = "hidden"
    db_session.commit()
    headers = _make_admin(db_session, user)
    all_posts = client.get("/admin/listings", headers=headers).json()
    assert any(p["id"] == own_listing.id for p in all_posts)
    hidden = client.get("/admin/listings", params={"status": "hidden"}, headers=headers).json()
    assert len(hidden) == 1
