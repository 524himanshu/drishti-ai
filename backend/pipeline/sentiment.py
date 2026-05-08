from typing import Dict

NEGATIVE_WORDS = [
    "pain",
    "nausea",
    "vomiting",
    "dizziness",
    "rash",
    "fatigue",
    "headache",
    "swelling",
    "fever",
    "diarrhea",
    "hospital",
    "reaction",
    "adverse",
    "side effect",
    "shortness of breath"
]

POSITIVE_WORDS = [
    "better",
    "improved",
    "helped",
    "effective",
    "working"
]


def analyze_sentiment(text: str) -> Dict:
    text_lower = text.lower()

    neg_score = sum(1 for word in NEGATIVE_WORDS if word in text_lower)
    pos_score = sum(1 for word in POSITIVE_WORDS if word in text_lower)

    if neg_score > pos_score:
        return {
            "sentiment": "negative",
            "sentiment_score": 0.85
        }

    elif pos_score > neg_score:
        return {
            "sentiment": "positive",
            "sentiment_score": 0.8
        }

    return {
        "sentiment": "neutral",
        "sentiment_score": 0.5
    }