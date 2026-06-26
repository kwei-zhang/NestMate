from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps import get_current_user
from app.models import Listing, User
from app.schemas.listing import ContactOut, ListingPublic, NativePostIn

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("", response_model=list[ListingPublic])
def list_listings(
    db: Session = Depends(get_db),
    area: str | None = None,
    budget_min: int | None = None,
    budget_max: int | None = None,
    has_room: bool | None = None,
    has_pets: bool | None = None,
    mbti: str | None = None,
    intent: str | None = None,
    gender_pref: str | None = None,
    q: str | None = None,
    sort: str = Query("recent", pattern="^(recent|budget_asc|budget_desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> list[Listing]:
    stmt = select(Listing).where(Listing.status == "published")

    if area:
        stmt = stmt.where(Listing.area.ilike(f"%{area}%"))
    if intent:
        stmt = stmt.where(Listing.intent == intent)
    if has_room is not None:
        stmt = stmt.where(Listing.has_room == has_room)
    if has_pets is not None:
        stmt = stmt.where(Listing.has_pets == has_pets)
    if mbti:
        stmt = stmt.where(Listing.mbti.ilike(mbti))
    if gender_pref:
        stmt = stmt.where(Listing.gender_pref == gender_pref)
    if budget_max is not None:
        # listing's lower bound must fit under the searcher's ceiling
        stmt = stmt.where(or_(Listing.budget_min <= budget_max, Listing.budget_min.is_(None)))
    if budget_min is not None:
        stmt = stmt.where(or_(Listing.budget_max >= budget_min, Listing.budget_max.is_(None)))
    if q:
        stmt = stmt.where(
            or_(Listing.raw_text.ilike(f"%{q}%"), Listing.title.ilike(f"%{q}%"))
        )

    if sort == "budget_asc":
        stmt = stmt.order_by(Listing.budget_min.asc().nulls_last())
    elif sort == "budget_desc":
        stmt = stmt.order_by(Listing.budget_max.desc().nulls_last())
    else:
        stmt = stmt.order_by(Listing.published_at.desc().nulls_last(), Listing.id.desc())

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    return list(db.scalars(stmt).all())


@router.get("/{listing_id}", response_model=ListingPublic)
def get_listing(listing_id: int, db: Session = Depends(get_db)) -> Listing:
    listing = db.get(Listing, listing_id)
    if listing is None or listing.status != "published":
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.get("/{listing_id}/contact", response_model=ContactOut)
def get_contact(
    listing_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),  # auth required
) -> ContactOut:
    listing = db.get(Listing, listing_id)
    if listing is None or listing.status != "published":
        raise HTTPException(status_code=404, detail="Listing not found")
    return ContactOut(contact_type=listing.contact_type, contact_value=listing.contact_value)


@router.post("", response_model=ListingPublic, status_code=201)
def create_native_post(
    body: NativePostIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Listing:
    """User-submitted post. Enters pending_review for light moderation."""
    listing = Listing(
        source="native",
        raw_text=body.raw_text,
        status="pending_review",
        created_by=user.id,
        **body.model_dump(exclude={"raw_text"}),
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.post("/{listing_id}/archive", response_model=ListingPublic)
def archive_own_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Listing:
    """Author marks their own listing as resolved (found a roommate)."""
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.created_by != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not your listing")
    listing.status = "archived"
    db.commit()
    db.refresh(listing)
    return listing
