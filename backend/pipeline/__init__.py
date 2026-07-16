from pipeline.ner import extract_entities
from pipeline.sentiment import analyze_sentiment
from pipeline.adverse import detect_adverse_event
from pipeline.pii import detect_pii

def run_pipeline(text: str) -> dict:
    # Stage 1: Entity extraction
    entities = extract_entities(text)

    # Stage 2: Sentiment
    sentiment_result = analyze_sentiment(text)

    # Stage 3: Adverse event detection
    adverse_result = detect_adverse_event(
        text=text,
        sentiment=sentiment_result["sentiment"],
        sentiment_score=sentiment_result["sentiment_score"],
        drugs=entities["drugs"],
        symptoms=entities["symptoms"]
    )

    # Stage 4: PII detection
    pii_result = detect_pii(text)

    return {
        "entities": entities,
        "sentiment": sentiment_result["sentiment"],
        "sentiment_score": sentiment_result["sentiment_score"],
        "is_adverse_event": adverse_result["is_adverse_event"],
        "adverse_confidence": adverse_result["adverse_confidence"],
        "shap_explanation": adverse_result["shap_explanation"],
        "has_pii": pii_result["has_pii"],
        "pii_types": pii_result["pii_types"],
        "masked_content": pii_result["masked_content"]
    }