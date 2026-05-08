from ingestion import save_posts, process_unprocessed_posts
from routers.signals import router as signals_router
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models.post import Post
from engines.twitter import TwitterEngine
from ingestion import save_posts

app = FastAPI(title="DrishtiAI", version="1.0")
app.include_router(signals_router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest/test")
def test_ingest(db: Session = Depends(get_db)):
    engine_instance = TwitterEngine(
        project_id="test-project",
        keywords=["metformin nausea", "ozempic side effects", "drug reaction", "adverse reaction medication", "hospitalized after taking"]
    )
    posts = engine_instance.fetch(limit=20)
    result = save_posts(posts, db)
    return {
        "fetched": len(posts),
        "saved": result["saved"],
        "skipped": result["skipped"]
    }

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.timestamp.desc()).limit(20).all()
    return [
        {
            "id": str(p.id),
            "source": p.source,
            "content": p.content[:100],
            "keywords_matched": p.keywords_matched,
            "timestamp": p.timestamp,
            "is_processed": p.is_processed
        }
        for p in posts
    ]
    
@app.post("/process")
def process_posts(db: Session = Depends(get_db)):
    result = process_unprocessed_posts(db)
    return result   

from engines.agent_discovery import discover_sources

@app.get("/discover")
def discover_new_sources(topic: str = "diabetes medication side effects"):
    results = discover_sources(topic)
    return {
        "topic": topic,
        "discovered": results,
        "total": len(results)
    }
    
@app.get("/")
def root():
    return {
        "project": "DrishtiAI",
        "status": "running",
        "docs": "/docs"
        "health": "/health"
    }