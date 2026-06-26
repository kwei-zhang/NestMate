"""Best-effort text fetcher for a xiaohongshu note page.

Given a post URL, pull the visible text (Open Graph title/description) so the
admin can ingest a post by pasting just the link. xiaohongshu has aggressive
anti-scraping, so this can return empty text or hit a risk-control page — callers
must treat it as best-effort and let the admin paste content manually as a
fallback.
"""
from __future__ import annotations

from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

from app.core.config import settings

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


@dataclass
class FetchedPost:
    text: str = ""


def _meta(soup: BeautifulSoup, key: str) -> str | None:
    tag = soup.find("meta", attrs={"property": key}) or soup.find("meta", attrs={"name": key})
    return tag.get("content") if tag else None


def fetch_post(url: str) -> FetchedPost:
    headers = {"User-Agent": UA, "Referer": "https://www.xiaohongshu.com/"}
    if settings.xhs_cookie:
        headers["Cookie"] = settings.xhs_cookie
    try:
        resp = httpx.get(url, headers=headers, timeout=20, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError:
        return FetchedPost()

    soup = BeautifulSoup(resp.text, "html.parser")
    title = _meta(soup, "og:title") or ""
    desc = _meta(soup, "og:description") or _meta(soup, "description") or ""
    text = "\n".join(t for t in (title, desc) if t).strip()
    return FetchedPost(text=text)
