from presidio_analyzer import AnalyzerEngine
from typing import Dict, List

print("Loading PII analyzer...")
analyzer = AnalyzerEngine()
print("PII analyzer loaded.")

# Indian-specific PII patterns to check
INDIAN_PII_ENTITIES = [
    "PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS",
    "LOCATION", "DATE_TIME", "MEDICAL_LICENSE"
]

def detect_pii(text: str) -> Dict:
    try:
        results = analyzer.analyze(
            text=text,
            entities=INDIAN_PII_ENTITIES,
            language="en"
        )

        has_pii = len(results) > 0
        pii_types = list(set([r.entity_type for r in results]))

        return {
            "has_pii": has_pii,
            "pii_types": pii_types
        }
    except Exception as e:
        print(f"PII detection error: {e}")
        return {"has_pii": False, "pii_types": []}