from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps import require_admin
from app.models import Listing
from app.schemas.listing import IngestIn, ListingAdmin, ListingUpdate
from app.services.ai_extract import extract_listing
from app.services.listing_service import apply_extraction
from app.services.staleness import check_listing
from app.services.xhs_fetch import fetch_post

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.post("/ingest", response_model=ListingAdmin, status_code=201)
def ingest(body: IngestIn, db: Session = Depends(get_db)) -> Listing:
    """Ingest a xhs post -> AI extracts -> stored as pending_review draft.

    The admin can paste text/images, or just provide the link and let the backend
    auto-fetch both (best-effort; xiaohongshu may block it)."""
    text = body.raw_text

    # Auto-fetch text from the link when not pasted (best-effort; no images).
    if body.source_url and not text:
        text = fetch_post(body.source_url).text

    if not text:
        raise HTTPException(
            status_code=400,
            detail="No text: provide raw_text or a fetchable source_url",
        )

    extracted = extract_listing(text, body.source_url)
    listing = Listing(
        source="xhs",
        source_url=body.source_url,
        raw_text=text,
        status="pending_review",
        source_last_modified=body.last_edited_at,
    )
    apply_extraction(listing, extracted)
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.get("/listings", response_model=list[ListingAdmin])
def admin_list(
    db: Session = Depends(get_db),
    status: str | None = Query(None),
) -> list[Listing]:
    stmt = select(Listing).order_by(Listing.created_at.desc())
    if status:
        stmt = stmt.where(Listing.status == status)
    return list(db.scalars(stmt).all())


@router.patch("/listings/{listing_id}", response_model=ListingAdmin)
def admin_update(
    listing_id: int, body: ListingUpdate, db: Session = Depends(get_db)
) -> Listing:
    """Correct AI-extracted fields on xhs-sourced drafts during review.

    Admins may NOT edit user-submitted (native) posts — only their authors can.
    For native posts, admins moderate via hide/unhide instead."""
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.source == "native":
        raise HTTPException(
            status_code=403,
            detail="Admins cannot edit user posts; hide them instead",
        )
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(listing, field, value)
    db.commit()
    db.refresh(listing)
    return listing


@router.post("/listings/{listing_id}/hide", response_model=ListingAdmin)
def admin_hide(listing_id: int, db: Session = Depends(get_db)) -> Listing:
    """Moderation: hide a listing from public view (any source)."""
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    listing.status = "hidden"
    db.commit()
    db.refresh(listing)
    return listing


@router.post("/listings/{listing_id}/unhide", response_model=ListingAdmin)
def admin_unhide(listing_id: int, db: Session = Depends(get_db)) -> Listing:
    """Restore a hidden listing to published."""
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    listing.status = "published"
    db.commit()
    db.refresh(listing)
    return listing


@router.post("/listings/{listing_id}/publish", response_model=ListingAdmin)
def admin_publish(listing_id: int, db: Session = Depends(get_db)) -> Listing:
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    listing.status = "published"
    if listing.published_at is None:
        listing.published_at = datetime.now(UTC)
    db.commit()
    db.refresh(listing)
    return listing


@router.get("/stale", response_model=list[ListingAdmin])
def admin_stale(db: Session = Depends(get_db)) -> list[Listing]:
    """Listings flagged by the staleness job (auto-archived or needing AI review)."""
    stmt = (
        select(Listing)
        .where(or_(Listing.check_state == "auto_archived", Listing.check_state == "changed_needs_ai"))
        .order_by(Listing.last_checked_at.desc().nulls_last())
    )
    return list(db.scalars(stmt).all())


@router.post("/recheck/{listing_id}", response_model=ListingAdmin)
def admin_recheck(listing_id: int, db: Session = Depends(get_db)) -> Listing:
    """Manually run the staleness check for one listing."""
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    check_listing(db, listing)
    db.refresh(listing)
    return listing
