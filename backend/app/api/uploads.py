from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.deps import get_current_user
from app.models import User
from app.services.images import ALLOWED_TYPES, MAX_BYTES, save_image_bytes

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/image")
async def upload_image(
    file: UploadFile,
    _user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Accept one image from a logged-in user; return its served URL."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported image type")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image too large (max 8MB)")
    url = save_image_bytes(data, file.content_type)
    return {"url": url}
