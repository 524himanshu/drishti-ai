from typing import Dict, List
import re

# Patterns strongly associated with adverse drug reactions
ADVERSE_PATTERNS = [
    r"\b(side effect|adverse|reaction|hospitali[sz]ed|ER|emergency)\b",
    r"\b(couldn't breathe|chest pain|heart attack|stroke|seizure)\b",
    r"\b(severe|serious|dangerous|life.threatening|fatal)\b",
    r"\b(stopped taking|had to stop|discontinued|quit taking)\b",
    r"\b(allergic|allergy|anaphylaxis|swelling|hives)\b",
    r"\b(overdose|too much|wrong dose|missed dose)\b",
]

NEGATION_PATTERNS = [
    r"\bno\s+side\s+effects?\b",
    r"\bwithout\s+(any\s+)?side\s+effects?\b",
    r"\b(works?|working)\s+(great|well|fine|perfectly)\b",
    r"\blove\s+(this|it|my)\b",
]

def detect_adverse_event(
    text: str,
    sentiment: str,
    sentiment_score: float,
    drugs: List[str],
    symptoms: List[str]
) -> Dict:
    text_lower = text.lower()
    confidence = 0.0
    reasons = []

    # Check negation first — if post says "no side effects", not adverse
    for pattern in NEGATION_PATTERNS:
        if re.search(pattern, text_lower):
            return {
                "is_adverse_event": False,
                "adverse_confidence": 0.05,
                "shap_explanation": {"reasons": ["negation detected"]}
            }

    # Signal 1: Negative sentiment with drugs mentioned
    if sentiment == "negative" and drugs:
        confidence += 0.35
        reasons.append(f"negative sentiment with drug mention: {drugs}")

    # Signal 2: Adverse pattern matches
    pattern_matches = []
    for pattern in ADVERSE_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            confidence += 0.2
            pattern_matches.append(match.group())

    if pattern_matches:
        reasons.append(f"adverse patterns found: {pattern_matches}")

    # Signal 3: Symptoms + drugs co-occurring
    if symptoms and drugs:
        confidence += 0.2
        reasons.append(f"symptom-drug co-occurrence: {symptoms} + {drugs}")

    # Signal 4: High negative sentiment score
    if sentiment == "negative" and sentiment_score > 0.85:
        confidence += 0.1
        reasons.append(f"high negative confidence: {sentiment_score}")

    confidence = min(round(confidence, 4), 1.0)
    is_adverse = confidence >= 0.4

    return {
        "is_adverse_event": is_adverse,
        "adverse_confidence": confidence,
        "shap_explanation": {
            "reasons": reasons,
            "pattern_matches": pattern_matches,
            "drugs_involved": drugs,
            "symptoms_involved": symptoms
        }
    }