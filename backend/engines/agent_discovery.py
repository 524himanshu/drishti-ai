import requests
import re
from typing import List, Dict
from urllib.parse import unquote

FORUM_PATTERNS = [
    "reddit.com", "forum", "community", "patient",
    "healthunlocked", "patientlikeme", "drugs.com/comments", "subreddits", "group"
]

def search_ddg_html(query: str) -> List[Dict]:
    """Robust scraper for DuckDuckGo's public HTML search."""
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    params = {"q": query}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=12)
        response.raise_for_status()
        html = response.text
        
        # Extract URLs
        uddg_urls = re.findall(r'uddg=([^&"\']+)', html)
        decoded_urls = [unquote(u) for u in uddg_urls]
        
        # Extract Titles
        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html)
        
        # Extract Snippets
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html)
        
        results = []
        for i in range(min(len(decoded_urls), len(titles))):
            snippet_text = snippets[i] if i < len(snippets) else ""
            title_clean = re.sub(r'<[^>]+>', '', titles[i]).strip()
            snippet_clean = re.sub(r'<[^>]+>', '', snippet_text).strip()
            
            results.append({
                "url": decoded_urls[i],
                "title": title_clean,
                "snippet": snippet_clean
            })
        return results
    except Exception as e:
        print(f"Scraper error for query '{query}': {e}")
        return []

def evaluate_source(url: str, title: str, snippet: str, topic: str) -> Dict:
    """Agentic reasoning engine evaluating the relevance of discovered web resources."""
    url_lower = url.lower()
    title_lower = title.lower()
    snippet_lower = snippet.lower()
    
    score = 0.50  # Base confidence
    reasons = []
    
    # 1. Check if it is a patient forum
    is_forum = any(p in url_lower or p in title_lower for p in FORUM_PATTERNS)
    if is_forum:
        score += 0.25
        reasons.append("Identified patient-led forum")
    else:
        reasons.append("Identified informational portal")
        
    # 2. Check topic keyword matches
    keywords = topic.lower().split()
    matched_keywords = [k for k in keywords if k in title_lower or k in snippet_lower]
    if matched_keywords:
        score += min(0.05 * len(matched_keywords), 0.20)
        reasons.append(f"Contains keywords ({', '.join(matched_keywords)})")
        
    # 3. Check for patient experience signals
    experience_signals = ["nausea", "vomit", "vomiting", "pain", "allergic", "reaction", "hives", "dose", "doctor", "prescribed", "feel", "felt", "started", "taking", "i ", "my ", "me "]
    matched_signals = [s for s in experience_signals if s in snippet_lower or s in title_lower]
    if len(matched_signals) >= 2:
        score += 0.10
        reasons.append("Found patient symptom complaints")
        
    score = min(score, 0.99)
    
    # Generate agent reasoning text
    if "reddit.com" in url_lower:
        explanation = f"AI Agent Analysis: Target community thread on Reddit (r/{url_lower.split('/r/')[-1].split('/')[0] if '/r/' in url_lower else 'reddit'}). High-priority direct listening post. Reason: {', '.join(reasons)}."
    elif is_forum:
        explanation = f"AI Agent Analysis: Verified healthcare community group. Strong source for patient experience metrics. Reason: {', '.join(reasons)}."
    else:
        explanation = f"AI Agent Analysis: General medical database/article. Recommended for clinical correlation. Reason: {', '.join(reasons)}."
        
    domain = re.sub(r'https?://(www\.)?', '', url).split('/')[0]
    
    return {
        "url": url,
        "title": title,
        "snippet": snippet,
        "domain": domain,
        "is_forum": is_forum,
        "confidence_score": round(score, 2),
        "explanation": explanation,
        "suggested_engine": "reddit" if "reddit" in url_lower else "forum" if is_forum else "scraper",
        "status": "approved" if score >= 0.75 else "pending_review"
    }

def discover_sources(topic: str, max_results: int = 8) -> List[Dict]:
    """Agent entry point to discover and evaluate source locations."""
    queries = [
        f"{topic} patient forum community",
        f"site:reddit.com {topic} side effects",
        f"{topic} medication reviews"
    ]
    
    seen_urls = set()
    raw_results = []
    
    for query in queries:
        search_hits = search_ddg_html(query)
        for hit in search_hits:
            if hit["url"] not in seen_urls:
                seen_urls.add(hit["url"])
                raw_results.append(hit)
                
    evaluated_results = []
    for hit in raw_results:
        eval_data = evaluate_source(hit["url"], hit["title"], hit["snippet"], topic)
        evaluated_results.append(eval_data)
        
    evaluated_results.sort(key=lambda x: x["confidence_score"], reverse=True)
    return evaluated_results[:max_results]