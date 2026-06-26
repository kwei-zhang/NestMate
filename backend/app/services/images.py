"""Save user-uploaded images locally and serve them from /media.

Only used for native (user-submitted) posts — users upload their own photos,
so there is no scraping or AI verification involved.
"""
from __future__ import annotations

import mimetypes
from pathlib import Path
from uuid import uuid4

from app.core.config import settings

MEDIA_DIR = Path(settings.media_dir)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_BYTES = 8 * 1024 * 1024  # 8 MB


def save_image_bytes(data: bytes, content_type: str) -> str:
    """Persist image bytes to the media dir; return the served URL."""
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    ext = mimetypes.guess_extension(content_type) or ".jpg"
    name = f"{uuid4().hex}{ext}"
    (MEDIA_DIR / name).write_bytes(data)
    return f"{settings.media_base}/media/{name}"
