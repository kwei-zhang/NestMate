from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps import get_current_user, get_current_user_optional
from app.models import Listing, User
from app.schemas.listing import ContactOut, ListingEdit, ListingPublic, NativePostIn
from app.services.ai_extract import extract_listing

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("", response_model=list[ListingPublic])
def list_listings(
    db: Session = Depends(get_db),
    area: str | None = None,
    budget_min: int | None = None,
    budget_max: int | None = None,
    has_room: bool | None = None,
    has_pets: bool | None = None,
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


@router.get("/mine", response_model=list[ListingPublic])
def my_listings(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[Listing]:
    """The current user's own posts in all states (published/hidden/expired/…)."""
    stmt = (
        select(Listing)
        .where(Listing.created_by == user.id)
        .order_by(Listing.updated_at.desc())
    )
    return list(db.scalars(stmt).all())


def _can_view(listing: Listing | None, viewer: User | None) -> bool:
    """Published posts are public; non-published are visible only to an admin or
    the post's author."""
    if listing is None:
        return False
    if listing.status == "published":
        return True
    if viewer is None:
        return False
    return viewer.role == "admin" or listing.created_by == viewer.id


@router.get("/{listing_id}", response_model=ListingPublic)
def get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_current_user_optional),
) -> Listing:
    listing = db.get(Listing, listing_id)
    if not _can_view(listing, viewer):
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.get("/{listing_id}/contact", response_model=ContactOut)
def get_contact(
    listing_id: int,
    db: Session = Depends(get_db),
    viewer: User = Depends(get_current_user),  # auth required
) -> ContactOut:
    listing = db.get(Listing, listing_id)
    if not _can_view(listing, viewer):
        raise HTTPException(status_code=404, detail="Listing not found")
    return ContactOut(contact_type=listing.contact_type, contact_value=listing.contact_value)


@router.post("", response_model=ListingPublic, status_code=201)
def create_native_post(
    body: NativePostIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Listing:
    """User-submitted post. Published immediately (no review for native posts).

    AI-extractable attributes (MBTI, lifestyle highlights) are derived from the
    text rather than asked of the user. Extraction failures never block posting.
    """
    listing = Listing(
        source="native",
        raw_text=body.raw_text,
        status="published",
        published_at=datetime.now(UTC),
        created_by=user.id,
        **body.model_dump(exclude={"raw_text"}),
    )
    try:
        extracted = extract_listing(body.raw_text)
        listing.mbti = extracted.mbti
        listing.highlights = extracted.highlights or None
    except Exception:
        pass
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.patch("/{listing_id}", response_model=ListingPublic)
def edit_own_listing(
    listing_id: int,
    body: ListingEdit,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Listing:
    """Author edits their own post (title, content, tags, etc.).

    Only the author can edit — admins moderate by hiding, not by rewriting content."""
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.created_by != user.id:
        raise HTTPException(status_code=403, detail="Not your listing")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(listing, field, value)
    listing.updated_at = datetime.now(UTC)  # resets the auto-hide clock
    db.commit()
    db.refresh(listing)
    return listing


@router.post("/{listing_id}/republish", response_model=ListingPublic)
def republish_own_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Listing:
    """Author re-activates their own expired/archived post. Cannot un-hide an
    admin-moderated ('hidden') post."""
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.created_by != user.id:
        raise HTTPException(status_code=403, detail="Not your listing")
    if listing.status not in ("expired", "archived"):
        raise HTTPException(status_code=400, detail="Listing is not expired/archived")
    listing.status = "published"
    listing.updated_at = datetime.now(UTC)
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
