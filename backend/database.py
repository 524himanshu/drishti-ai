from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path
import os
import re

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Convert public Render Postgres hostname to internal hostname to avoid hairpinning and SSL drops
    DATABASE_URL = re.sub(r'\.[a-z]+-postgres\.render\.com', '', DATABASE_URL)
    
    if DATABASE_URL.startswith("postgresql"):
        if ".render.com" not in DATABASE_URL:
            # Internal network connection: use prefer for sslmode
            engine = create_engine(
                DATABASE_URL,
                connect_args={"sslmode": "prefer"},
                pool_pre_ping=True
            )
        else:
            # External network connection: require SSL
            engine = create_engine(
                DATABASE_URL,
                connect_args={"sslmode": "require"},
                pool_pre_ping=True
            )
    else:
        engine = create_engine(DATABASE_URL)
else:
    engine = create_engine("sqlite:///./drishti.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()