from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.post import Post
from datetime import datetime, timedelta

router = APIRouter(prefix="/signals", tags=["signals"])

@router.get("/feed")
def get_signal_feed(
    project_id: str = "test-project",
    adverse_only: bool = False,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(Post).filter(
        Post.project_id == project_id,
        Post.is_processed == True
    )

    if adverse_only:
        query = query.filter(Post.is_adverse_event == True)

    posts = query.order_by(Post.timestamp.desc()).limit(limit).all()

    return [
        {
            "id": str(p.id),
            "source": p.source,
            "source_url": p.source_url,
            "content": p.content,
            "sentiment": p.sentiment,
            "sentiment_score": p.sentiment_score,
            "is_adverse_event": p.is_adverse_event,
            "adverse_confidence": p.adverse_confidence,
            "shap_explanation": p.shap_explanation,
            "entities": p.entities,
            "has_pii": p.has_pii,
            "pii_types": p.pii_types,
            "keywords_matched": p.keywords_matched,
            "timestamp": p.timestamp
        }
        for p in posts
    ]

@router.get("/stats")
def get_stats(
    project_id: str = "test-project",
    db: Session = Depends(get_db)
):
    total = db.query(Post).filter(Post.project_id == project_id).count()
    processed = db.query(Post).filter(
        Post.project_id == project_id,
        Post.is_processed == True
    ).count()
    adverse = db.query(Post).filter(
        Post.project_id == project_id,
        Post.is_adverse_event == True
    ).count()
    pii_flagged = db.query(Post).filter(
        Post.project_id == project_id,
        Post.has_pii == True
    ).count()

    return {
        "total_posts": total,
        "processed": processed,
        "adverse_events": adverse,
        "pii_flagged": pii_flagged,
        "adverse_rate": round(adverse / processed, 4) if processed > 0 else 0
    }

@router.get("/trends")
def get_trends(
    project_id: str = "test-project",
    days: int = 7,
    db: Session = Depends(get_db)
):
    since = datetime.utcnow() - timedelta(days=days)

    posts = db.query(Post).filter(
        Post.project_id == project_id,
        Post.is_processed == True,
        Post.timestamp >= since
    ).all()

    # Group by date
    by_date = {}
    for post in posts:
        date_str = post.timestamp.strftime("%Y-%m-%d")
        if date_str not in by_date:
            by_date[date_str] = {
                "date": date_str,
                "total": 0,
                "adverse": 0,
                "negative": 0
            }
        by_date[date_str]["total"] += 1
        if post.is_adverse_event:
            by_date[date_str]["adverse"] += 1
        if post.sentiment == "negative":
            by_date[date_str]["negative"] += 1

    return sorted(by_date.values(), key=lambda x: x["date"])