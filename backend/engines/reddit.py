from engines.base import BaseEngine, StandardPost
from typing import List
from datetime import datetime
import requests
import os

class RedditEngine(BaseEngine):
    BASE_URL = "https://www.reddit.com/search.json"

    def __init__(self, project_id: str, keywords: List[str]):
        super().__init__(project_id, keywords)
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "DrishtiAI/1.0")

    def get_latency_mode(self) -> str:
        return "realtime"

    def fetch(self, limit: int = 50) -> List[StandardPost]:
        posts = []
        # Query combining first few keywords
        query = " OR ".join(f'"{k}"' for k in self.keywords[:3])
        
        headers = {
            "User-Agent": self.user_agent
        }
        params = {
            "q": query,
            "sort": "new",
            "limit": min(limit, 100)
        }

        try:
            response = requests.get(self.BASE_URL, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            children = data.get("data", {}).get("children", [])
            for child in children:
                post_data = child.get("data", {})
                title = post_data.get("title", "")
                selftext = post_data.get("selftext", "")
                content = f"{title}\n{selftext}" if selftext else title
                
                post = self.normalize(
                    raw_id=post_data.get("id", ""),
                    source="reddit",
                    source_url=f"https://www.reddit.com{post_data.get('permalink', '')}",
                    content=content,
                    author=post_data.get("author", "unknown"),
                    timestamp=datetime.utcfromtimestamp(
                        post_data.get("created_utc", datetime.utcnow().timestamp())
                    )
                )
                posts.append(post)
        except Exception as e:
            print(f"RedditEngine error: {e}")

        return posts
