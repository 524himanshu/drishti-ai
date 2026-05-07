from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import hashlib

@dataclass
class StandardPost:
    raw_id: str          # original ID from the source
    source: str          # "twitter", "reddit", "forum"
    source_url: str      # link to original post
    content: str         # the text content
    author_hash: str     # sha256 of author, never raw username
    timestamp: datetime
    project_id: str
    keywords_matched: List[str]

class BaseEngine(ABC):
    def __init__(self, project_id: str, keywords: List[str]):
        self.project_id = project_id
        self.keywords = keywords

    @abstractmethod
    def fetch(self, limit: int = 50) -> List[StandardPost]:
        """Fetch posts from the source matching keywords"""
        pass

    @abstractmethod
    def get_latency_mode(self) -> str:
        """Return 'realtime', 'daily', or 'weekly'"""
        pass

    def normalize(self, raw_id: str, source: str, source_url: str,
                  content: str, author: str, timestamp: datetime) -> StandardPost:
        """Convert raw source data into StandardPost — same for every engine"""
        return StandardPost(
            raw_id=raw_id,
            source=source,
            source_url=source_url,
            content=content,
            author_hash=hashlib.sha256(author.encode()).hexdigest(),
            timestamp=timestamp,
            project_id=self.project_id,
            keywords_matched=[kw for kw in self.keywords if kw.lower() in content.lower()]
        )