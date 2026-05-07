from transformers import pipeline
from typing import Dict

# Load once at module level
print("Loading sentiment model...")
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    truncation=True,
    max_length=512
)
print("Sentiment model loaded.")

def analyze_sentiment(text: str) -> Dict:
    try:
        result = sentiment_pipeline(text[:512])[0]
        label = result["label"].lower()  # "positive", "negative", "neutral"
        score = result["score"]

        return {
            "sentiment": label,
            "sentiment_score": round(score, 4)
        }
    except Exception as e:
        print(f"Sentiment error: {e}")
        return {"sentiment": "neutral", "sentiment_score": 0.5}