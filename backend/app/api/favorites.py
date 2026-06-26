from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps import get_current_user
from app.models import Favorite, Listing, User
from app.models.favorite import PERSONAL_STATUS_VALUES
from app.schemas.user import FavoriteIn, FavoriteOut

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteOut])
def list_favorites(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[Favorite]:
    return list(
        db.scalars(select(Favorite).where(Favorite.user_id == user.id)).all()
    )


@router.post("/{listing_id}", response_model=FavoriteOut, status_code=201)
def add_favorite(
    listing_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Favorite:
    if db.get(Listing, listing_id) is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    fav = db.get(Favorite, {"user_id": user.id, "listing_id": listing_id})
    if fav is None:
        fav = Favorite(user_id=user.id, listing_id=listing_id)
        db.add(fav)
        db.commit()
        db.refresh(fav)
    return fav


@router.patch("/{listing_id}", response_model=FavoriteOut)
def update_favorite(
    listing_id: int,
    body: FavoriteIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Favorite:
    fav = db.get(Favorite, {"user_id": user.id, "listing_id": listing_id})
    if fav is None:
        raise HTTPException(status_code=404, detail="Favorite not found")
    if body.personal_status is not None:
        if body.personal_status not in PERSONAL_STATUS_VALUES:
            raise HTTPException(status_code=422, detail="Invalid personal_status")
        fav.personal_status = body.personal_status
    if body.note is not None:
        fav.note = body.note
    db.commit()
    db.refresh(fav)
    return fav


@router.delete("/{listing_id}", status_code=204)
def remove_favorite(
    listing_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    fav = db.get(Favorite, {"user_id": user.id, "listing_id": listing_id})
    if fav is not None:
        db.delete(fav)
        db.commit()
