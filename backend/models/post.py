from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import uuid
from datetime import datetime
import hashlib

class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String, nullable=False)
    source_url = Column(String)
    content = Column(Text, nullable=False)
    author_hash = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    project_id = Column(String, nullable=False)
    keywords_matched = Column(JSON)
    entities = Column(JSON)
    sentiment = Column(String)
    sentiment_score = Column(Float)
    is_adverse_event = Column(Boolean, default=False)
    adverse_confidence = Column(Float)
    shap_explanation = Column(JSON)
    has_pii = Column(Boolean, default=False)
    pii_types = Column(JSON)
    is_processed = Column(Boolean, default=False)
    raw_id = Column(String, unique=True)