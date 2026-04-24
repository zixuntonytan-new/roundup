from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Headline, Tag, HeadlineTag

router = APIRouter(prefix="/headlines", tags=["headlines"])


@router.get("/")
def list_headlines(
    desk: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    flagged: Optional[bool] = Query(None),
    importance: Optional[int] = Query(None),
    days: Optional[int] = Query(None),        # filter by fetched_at recency
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    query = db.query(Headline)
    if desk:
        query = query.filter(Headline.desk == desk)
    if flagged is not None:
        query = query.filter(Headline.flagged == flagged)
    if importance:
        query = query.filter(Headline.importance >= importance)
    if tag:
        query = query.join(HeadlineTag).join(Tag).filter(Tag.name == tag)
    if days is not None:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Headline.fetched_at >= cutoff)

    headlines = query.order_by(Headline.published_at.desc()).offset(offset).limit(limit).all()

    return [
        {
            "id": h.id,
            "source": h.source,
            "desk": h.desk,
            "title": h.title,
            "url": h.url,
            "summary": h.summary,
            "published_at": h.published_at,
            "fetched_at": h.fetched_at,
            "importance": h.importance,
            "flagged": h.flagged,
            "tags": [t.name for t in h.tags],
        }
        for h in headlines
    ]


@router.patch("/{headline_id}/flag")
def toggle_flag(headline_id: int, db: Session = Depends(get_db)):
    h = db.query(Headline).filter_by(id=headline_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Headline not found")
    h.flagged = not h.flagged
    db.commit()
    return {"id": headline_id, "flagged": h.flagged}


@router.patch("/{headline_id}/importance")
def set_importance(headline_id: int, importance: int = Query(..., ge=1, le=3), db: Session = Depends(get_db)):
    h = db.query(Headline).filter_by(id=headline_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Headline not found")
    h.importance = importance
    db.commit()
    return {"id": headline_id, "importance": h.importance}


@router.post("/{headline_id}/tags/{tag_name}")
def add_tag(headline_id: int, tag_name: str, db: Session = Depends(get_db)):
    h = db.query(Headline).filter_by(id=headline_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Headline not found")
    tag = db.query(Tag).filter_by(name=tag_name).first()
    if not tag:
        tag = Tag(name=tag_name)
        db.add(tag)
        db.commit()
    if tag not in h.tags:
        h.tags.append(tag)
        db.commit()
    return {"id": headline_id, "tags": [t.name for t in h.tags]}


@router.delete("/{headline_id}/tags/{tag_name}")
def remove_tag(headline_id: int, tag_name: str, db: Session = Depends(get_db)):
    h = db.query(Headline).filter_by(id=headline_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Headline not found")
    tag = db.query(Tag).filter_by(name=tag_name).first()
    if tag and tag in h.tags:
        h.tags.remove(tag)
        db.commit()
    return {"id": headline_id, "tags": [t.name for t in h.tags]}
