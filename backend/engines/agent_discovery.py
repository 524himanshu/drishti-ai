from duckduckgo_search import DDGS
from typing import List, Dict
import re

FORUM_PATTERNS = [
    "reddit.com", "forum", "community", "patient",
    "healthunlocked", "patientlikeme", "drugs.com/comments"
]

def discover_sources(topic: str, max_results: int = 8) -> List[Dict]:
    discovered = []

    queries = [
        f"{topic} patient forum discussion",
        f"{topic} side effects community Reddit",
        f"{topic} India patient experience forum"
    ]

    seen_domains = set()

    with DDGS() as ddgs:
        for query in queries:
            try:
                results = list(ddgs.text(query, max_results=5))
                for r in results:
                    url = r.get("href", "")
                    title = r.get("title", "")
                    snippet = r.get("body", "")

                    # Check if it looks like a forum/community
                    is_forum = any(p in url.lower() for p in FORUM_PATTERNS)
                    domain = re.sub(r'https?://(www\.)?', '', url).split('/')[0]

                    if domain not in seen_domains:
                        seen_domains.add(domain)
                        discovered.append({
                            "url": url,
                            "title": title,
                            "snippet": snippet[:150],
                            "domain": domain,
                            "is_forum": is_forum,
                            "suggested_engine": "reddit" if "reddit" in url else "forum",
                            "status": "pending_approval"
                        })
            except Exception as e:
                print(f"Discovery error: {e}")
                continue

    # Sort forums first
    discovered.sort(key=lambda x: x["is_forum"], reverse=True)
    return discovered[:max_results]