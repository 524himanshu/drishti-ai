from engines.base import BaseEngine, StandardPost
from typing import List
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import requests
import os

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

class TwitterEngine(BaseEngine):
    BASE_URL = "https://api.twitterapi.io/twitter/tweet/advanced_search"

    def __init__(self, project_id: str, keywords: List[str]):
        super().__init__(project_id, keywords)
        self.api_key = os.getenv("TWITTER_API_KEY")

    def get_latency_mode(self) -> str:
        return "realtime"

    def fetch(self, limit: int = 50) -> List[StandardPost]:
        posts = []
        query = " OR ".join(self.keywords) + " lang:en -is:retweet"

        headers = {
            "X-API-Key": self.api_key
        }
        params = {
            "query": query,
            "maxResults": min(limit, 100)
        }

        try:
            if self.api_key and "placeholder" not in self.api_key and not self.api_key.startswith("your_"):
                response = requests.get(self.BASE_URL, headers=headers, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                tweets = data.get("tweets", [])

                for tweet in tweets:
                    post = self.normalize(
                        raw_id=tweet["id"],
                        source="twitter",
                        source_url=f"https://twitter.com/i/web/status/{tweet['id']}",
                        content=tweet["text"],
                        author=tweet.get("author", {}).get("userName", "unknown"),
                        timestamp=datetime.strptime(
                            tweet["createdAt"], "%a %b %d %H:%M:%S +0000 %Y"
                        ),
                    )
                    posts.append(post)
        except Exception as e:
            print(f"TwitterEngine API call failed: {e}")

        return posts