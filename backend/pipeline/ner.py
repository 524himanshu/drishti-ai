from typing import Dict
import os

DRUG_KEYWORDS = [
    "metformin",
    "ozempic",
    "semaglutide",
    "insulin",
    "lisinopril",
    "atorvastatin",
    "omeprazole",
    "amoxicillin",
    "ibuprofen",
    "aspirin",
    "wegovy",
    "mounjaro",
    "tirzepatide",
    "jardiance",
    "farxiga"
]

SYMPTOM_KEYWORDS = [
    "nausea",
    "vomiting",
    "dizziness",
    "fatigue",
    "headache",
    "rash",
    "pain",
    "swelling",
    "fever",
    "chills",
    "diarrhea",
    "constipation",
    "insomnia",
    "anxiety",
    "depression",
    "shortness of breath",
    "chest pain"
]

# Real SpaCy NER loader with resource limit safety
nlp = None
SPACY_AVAILABLE = False

if not os.getenv("RENDER") and os.getenv("DISABLE_AI_MODELS") != "true":
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
        print("SpaCy clinical/general NER loaded successfully.")
    except Exception as e:
        print(f"SpaCy loading skipped or failed: {e}. Using rule-based NER.")


def extract_entities(text: str) -> Dict:
    text_lower = text.lower()
    drugs_found = set(drug for drug in DRUG_KEYWORDS if drug in text_lower)
    symptoms_found = set(sym for sym in SYMPTOM_KEYWORDS if sym in text_lower)

    entities = []

    if SPACY_AVAILABLE and nlp is not None:
        try:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PRODUCT"] and ent.text.lower() not in SYMPTOM_KEYWORDS:
                    drugs_found.add(ent.text.lower())
                    entities.append({
                        "text": ent.text,
                        "label": "DRUG (SpaCy)"
                    })
                elif ent.label_ in ["DISEASE", "CONDITION"] or ent.text.lower() in SYMPTOM_KEYWORDS:
                    symptoms_found.add(ent.text.lower())
                    entities.append({
                        "text": ent.text,
                        "label": "SYMPTOM (SpaCy)"
                    })
        except Exception as e:
            print(f"SpaCy execution failed: {e}. Falling back to rule-based NER.")

    # Always ensure keywords are captured as fallback
    for drug in drugs_found:
        if not any(e["text"].lower() == drug for e in entities):
            entities.append({
                "text": drug,
                "label": "DRUG"
            })

    for symptom in symptoms_found:
        if not any(e["text"].lower() == symptom for e in entities):
            entities.append({
                "text": symptom,
                "label": "SYMPTOM"
            })

    return {
        "ner_entities": entities,
        "drugs": list(drugs_found),
        "symptoms": list(symptoms_found),
        "entity_count": len(entities)
    }