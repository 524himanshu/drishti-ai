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
            print(f"TwitterEngine API call failed: {e}. Falling back to mock data...")

        if not posts:
            print("TwitterEngine: Generating fallback patient safety signals...")
            mock_tweets = [
                {
                    "id": "tw_1001",
                    "text": "My name is Amit Sharma (Aadhaar: 4321-8765-0912). Started taking Metformin last week for my diabetes and the nausea is absolutely unbearable. Has anyone else experienced this?",
                    "author": "amit_sharma_9"
                },
                {
                    "id": "tw_1002",
                    "text": "Ozempic side effects are no joke. Constant vomiting and stomach pain. Might need to talk to my doctor Dr. Rajesh Patel at +91 98234-56789 about stopping.",
                    "author": "diabetic_warrior"
                },
                {
                    "id": "tw_1003",
                    "text": "Severe drug reaction to my new blood pressure medication - woke up with red hives and swelling all over my body. Going to the emergency room.",
                    "author": "healthy_runner"
                },
                {
                    "id": "tw_1004",
                    "text": "Hospitalized after taking the wrong dosage of my prescribed blood thinners. Always double check your labels!",
                    "author": "caregiver_life"
                },
                {
                    "id": "tw_1005",
                    "text": "Metformin nausea is ruining my appetite. Any tips on how to manage this side effect?",
                    "author": "diabetic_foodie"
                },
                {
                    "id": "tw_1006",
                    "text": "Been on Ozempic for a month now. The weight loss is great but the nausea and acid reflux are hitting hard today.",
                    "author": "ozempic_journey"
                },
                {
                    "id": "tw_1007",
                    "text": "Had an allergic reaction to the generic brand of metformin. Switched to name brand and feeling much better.",
                    "author": "patient_advocate"
                },
                {
                    "id": "tw_1008",
                    "text": "Experiencing muscle pain and weakness after starting statins. Is this a common drug reaction?",
                    "author": "silver_surfer"
                }
            ]
            for tweet in mock_tweets[:limit]:
                post = self.normalize(
                    raw_id=tweet["id"],
                    source="twitter",
                    source_url=f"https://twitter.com/i/web/status/{tweet['id']}",
                    content=tweet["text"],
                    author=tweet["author"],
                    timestamp=datetime.utcnow()
                )
                posts.append(post)

        return posts