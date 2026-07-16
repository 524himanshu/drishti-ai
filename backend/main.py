from ingestion import save_posts, process_unprocessed_posts
from routers.signals import router as signals_router
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models.post import Post
from engines.twitter import TwitterEngine
from engines.reddit import RedditEngine
from ingestion import save_posts

app = FastAPI(title="DrishtiAI", version="1.0")
app.include_router(signals_router)

def seed_database(db: Session):
    # Surgical cleanup: delete legacy seed or mock posts to ensure only fresh, correctly redacted data exists
    legacy_seeds = db.query(Post).filter(
        (Post.raw_id.like("seed_%")) | (Post.raw_id.like("tw_%"))
    ).all()
    if legacy_seeds:
        print(f"Clearing {len(legacy_seeds)} legacy seed/mock records...")
        for p in legacy_seeds:
            db.delete(p)
        db.commit()

    # Re-seed if no seed posts exist
    if db.query(Post).filter(Post.raw_id.like("seed_%")).count() == 0:
        print("Database is empty of seed data. Seeding fresh, DPDP-compliant patient safety records...")
        from datetime import datetime, timedelta
        
        sample_data = [
            {
                "raw_id": "seed_001",
                "source": "reddit",
                "source_url": "https://www.reddit.com/r/diabetes/comments/seed1",
                "content": "My name is Amit Sharma (Aadhaar: 4321-8765-0912). Started taking Metformin last week for my diabetes and the nausea is absolutely unbearable. Has anyone else experienced this?",
                "author": "amit_sharma_9",
                "timestamp": datetime.utcnow() - timedelta(days=2),
                "keywords_matched": ["metformin nausea"]
            },
            {
                "raw_id": "seed_002",
                "source": "reddit",
                "source_url": "https://www.reddit.com/r/askdocs/comments/seed2",
                "content": "Ozempic side effects are no joke. Constant vomiting and stomach pain. Might need to talk to my doctor Dr. Rajesh Patel at +91 98234-56789 about stopping.",
                "author": "diabetic_warrior",
                "timestamp": datetime.utcnow() - timedelta(days=1),
                "keywords_matched": ["ozempic side effects"]
            },
            {
                "raw_id": "seed_003",
                "source": "twitter",
                "source_url": "https://twitter.com/i/web/status/seed3",
                "content": "Had a severe allergic drug reaction to my new blood pressure medicine. Red hives and swelling all over my body. Spent the night at the clinic.",
                "author": "runner_life",
                "timestamp": datetime.utcnow() - timedelta(hours=12),
                "keywords_matched": ["drug reaction"]
            },
            {
                "raw_id": "seed_004",
                "source": "reddit",
                "source_url": "https://www.reddit.com/r/health/comments/seed4",
                "content": "Hospitalized after taking the wrong dosage of my prescribed blood thinners. Always double check your labels and instructions!",
                "author": "caregiver_today",
                "timestamp": datetime.utcnow() - timedelta(days=3),
                "keywords_matched": ["hospitalized after taking"]
            },
            {
                "raw_id": "seed_005",
                "source": "twitter",
                "source_url": "https://twitter.com/i/web/status/seed5",
                "content": "Been experiencing mild muscle weakness after starting statins. Wondering if this is a standard drug reaction or something to worry about.",
                "author": "patient_voices",
                "timestamp": datetime.utcnow() - timedelta(days=4),
                "keywords_matched": ["drug reaction"]
            }
        ]
        
        for item in sample_data:
            post = Post(
                raw_id=item["raw_id"],
                source=item["source"],
                source_url=item["source_url"],
                content=item["content"],
                author_hash=item["author"],
                timestamp=item["timestamp"],
                project_id="test-project",
                keywords_matched=item["keywords_matched"],
                is_processed=False
            )
            db.add(post)
        db.commit()
        
        # Instantly run pipeline processing
        print("Processing seeded records through NLP pipeline...")
        process_unprocessed_posts(db)
        print("Database seeding complete.")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    
    # Run seeder
    db = next(get_db())
    try:
        seed_database(db)
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest/test")
def test_ingest(db: Session = Depends(get_db)):
    keywords = ["metformin nausea", "ozempic side effects", "drug reaction", "adverse reaction medication", "hospitalized after taking"]
    
    twitter_engine = TwitterEngine(project_id="test-project", keywords=keywords)
    reddit_engine = RedditEngine(project_id="test-project", keywords=keywords)
    
    posts = []
    posts.extend(twitter_engine.fetch(limit=10))
    posts.extend(reddit_engine.fetch(limit=10))
    
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
        "docs": "/docs",
        "health": "/health"
    }