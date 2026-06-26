def test_list_published(client, published_listing):
    resp = client.get("/listings")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    # Contact value must never appear in the public payload.
    assert "contact_value" not in data[0]
    assert data[0]["contact_type"] == "wechat"


def test_filter_by_area_and_budget(client, published_listing):
    assert len(client.get("/listings", params={"area": "North York"}).json()) == 1
    assert len(client.get("/listings", params={"area": "Scarborough"}).json()) == 0
    # Searcher ceiling 1200 -> listing.budget_min 900 fits
    assert len(client.get("/listings", params={"budget_max": 1200}).json()) == 1
    assert len(client.get("/listings", params={"budget_max": 800}).json()) == 0
    assert len(client.get("/listings", params={"has_pets": True}).json()) == 1
    # published_listing has has_room=False (it's a 求租/seeking post).
    assert len(client.get("/listings", params={"has_room": False}).json()) == 1
    assert len(client.get("/listings", params={"has_room": True}).json()) == 0


def test_detail_excludes_contact(client, published_listing):
    resp = client.get(f"/listings/{published_listing.id}")
    assert resp.status_code == 200
    assert "contact_value" not in resp.json()


def test_contact_requires_auth(client, published_listing):
    resp = client.get(f"/listings/{published_listing.id}/contact")
    assert resp.status_code == 401


def test_contact_returns_value_when_authed(client, published_listing, auth_headers):
    resp = client.get(f"/listings/{published_listing.id}/contact", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["contact_type"] == "wechat"
    assert body["contact_value"] == "abc123"
