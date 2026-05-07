from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from typing import Dict

print("Loading PII analyzer...")

configuration = {
    "nlp_engine_name": "spacy",
    "models": [
        {
            "lang_code": "en",
            "model_name": "en_core_web_sm"
        }
    ],
}

provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()

analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

print("PII analyzer loaded.")

INDIAN_PII_ENTITIES = [
    "PERSON",
    "PHONE_NUMBER",
    "EMAIL_ADDRESS",
    "LOCATION",
    "DATE_TIME",
    "MEDICAL_LICENSE"
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
        return {
            "has_pii": False,
            "pii_types": []
        }