from unittest.mock import patch

import httpx

from app.services import images, xhs_fetch

SAMPLE_HTML = """
<html><head>
<meta property="og:title" content="北约克招租 招室友">
<meta property="og:description" content="INFP 不抽烟 不带异性回家 预算1200">
</head><body></body></html>
"""


def test_fetch_post_parses_text():
    req = httpx.Request("GET", "https://www.xiaohongshu.com/explore/x")
    resp = httpx.Response(200, text=SAMPLE_HTML, request=req)
    with patch("app.services.xhs_fetch.httpx.get", return_value=resp):
        result = xhs_fetch.fetch_post("https://www.xiaohongshu.com/explore/x")
    assert "北约克招租" in result.text
    assert "不带异性回家" in result.text


def test_fetch_post_handles_network_error():
    with patch("app.services.xhs_fetch.httpx.get", side_effect=httpx.ConnectError("x")):
        result = xhs_fetch.fetch_post("https://www.xiaohongshu.com/explore/x")
    assert result.text == ""


def test_save_image_bytes_writes_and_returns_url(tmp_path):
    with patch.object(images, "MEDIA_DIR", tmp_path):
        url = images.save_image_bytes(b"abc", "image/png")
    assert url.endswith(".png")
    assert "/media/" in url
    assert len(list(tmp_path.iterdir())) == 1


def test_upload_image_endpoint(client, auth_headers, tmp_path):
    with patch.object(images, "MEDIA_DIR", tmp_path):
        resp = client.post(
            "/uploads/image",
            files={"file": ("room.png", b"fakebytes", "image/png")},
            headers=auth_headers,
        )
    assert resp.status_code == 200
    assert "/media/" in resp.json()["url"]


def test_upload_image_requires_auth(client):
    resp = client.post(
        "/uploads/image",
        files={"file": ("room.png", b"fakebytes", "image/png")},
    )
    assert resp.status_code == 401


def test_upload_image_rejects_non_image(client, auth_headers):
    resp = client.post(
        "/uploads/image",
        files={"file": ("note.txt", b"hello", "text/plain")},
        headers=auth_headers,
    )
    assert resp.status_code == 415


def test_native_post_stores_images_and_ai_fills_mbti(client, auth_headers):
    from app.schemas.listing import ExtractedListing

    fake = ExtractedListing(mbti="INFP", highlights=["🚭 不抽烟"])
    with patch("app.api.listings.extract_listing", return_value=fake):
        resp = client.post(
            "/listings",
            json={
                "raw_text": "求室友 North York，我是INFP不抽烟",
                "contact_type": "wechat",
                "contact_value": "abc",
                "images": ["http://host/media/a.png", "http://host/media/b.png"],
            },
            headers=auth_headers,
        )
    assert resp.status_code == 201
    body = resp.json()
    assert body["images"] == ["http://host/media/a.png", "http://host/media/b.png"]
    # Native posts publish immediately (no review).
    assert body["status"] == "published"
    # MBTI/highlights come from AI extraction, not the form.
    assert body["mbti"] == "INFP"
    assert body["highlights"] == ["🚭 不抽烟"]


def test_native_post_survives_extraction_failure(client, auth_headers):
    with patch("app.api.listings.extract_listing", side_effect=RuntimeError("no key")):
        resp = client.post(
            "/listings",
            json={"raw_text": "求室友", "contact_type": "wechat", "contact_value": "abc"},
            headers=auth_headers,
        )
    assert resp.status_code == 201
    assert resp.json()["mbti"] is None
