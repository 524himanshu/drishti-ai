from transformers import pipeline
from typing import Dict

sentiment_pipeline = None

def get_sentiment_pipeline():
    global sentiment_pipeline

    if sentiment_pipeline is None:
        print("Loading sentiment model...")

        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            truncation=True,
            max_length=512
        )

        print("Sentiment model loaded.")

    return sentiment_pipeline


def analyze_sentiment(text: str) -> Dict:
    try:
        pipeline_instance = get_sentiment_pipeline()

        result = pipeline_instance(text[:512])[0]

        label = result["label"].lower()
        score = result["score"]

        return {
            "sentiment": label,
            "sentiment_score": round(score, 4)
        }

    except Exception as e:
        print(f"Sentiment error: {e}")

        return {
            "sentiment": "neutral",
            "sentiment_score": 0.5
        }