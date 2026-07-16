from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.post import Post
from engines.base import StandardPost
from pipeline import run_pipeline
from typing import List

def save_posts(posts: List[StandardPost], db: Session) -> dict:
    saved = 0
    skipped = 0

    for post in posts:
        db_post = Post(
            source=post.source,
            source_url=post.source_url,
            content=post.content,
            author_hash=post.author_hash,
            timestamp=post.timestamp,
            project_id=post.project_id,
            keywords_matched=post.keywords_matched,
            raw_id=post.raw_id,
            is_processed=False
        )

        try:
            db.add(db_post)
            db.commit()
            saved += 1
        except IntegrityError:
            db.rollback()
            skipped += 1

    return {"saved": saved, "skipped": skipped}


def process_unprocessed_posts(db: Session) -> dict:
    unprocessed = db.query(Post).filter(
        Post.is_processed == False
    ).limit(10).all()

    processed = 0

    for post in unprocessed:
        try:
            result = run_pipeline(post.content)

            post.entities = result["entities"]
            post.sentiment = result["sentiment"]
            post.sentiment_score = result["sentiment_score"]
            post.is_adverse_event = result["is_adverse_event"]
            post.adverse_confidence = result["adverse_confidence"]
            post.shap_explanation = result["shap_explanation"]
            post.has_pii = result["has_pii"]
            post.pii_types = result["pii_types"]
            if result["has_pii"]:
                post.content = result["masked_content"]
            post.is_processed = True

            db.commit()
            processed += 1

        except Exception as e:
            print(f"Pipeline error on post {post.id}: {e}")
            db.rollback()
            continue

    return {"processed": processed, "remaining": len(unprocessed) - processed}