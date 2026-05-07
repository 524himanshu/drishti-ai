import spacy
from typing import List, Dict

# Load the biomedical model once at module level
# Loading it per-request would be extremely slow
try:
    nlp = spacy.load("en_core_sci_sm")
except OSError:
    print("WARNING: en_core_sci_sm not found, falling back to en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Medical entity categories we care about
DRUG_KEYWORDS = [
    "metformin", "ozempic", "semaglutide", "insulin", "lisinopril",
    "atorvastatin", "omeprazole", "amoxicillin", "ibuprofen", "aspirin",
    "wegovy", "mounjaro", "tirzepatide", "jardiance", "farxiga"
]

SYMPTOM_KEYWORDS = [
    "nausea", "vomiting", "dizziness", "fatigue", "headache", "rash",
    "pain", "swelling", "fever", "chills", "diarrhea", "constipation",
    "insomnia", "anxiety", "depression", "shortness of breath", "chest pain"
]

def extract_entities(text: str) -> Dict:
    doc = nlp(text)

    entities = []

    # scispaCy entities
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char
        })

    # Keyword-based drug detection (catches brand names scispaCy might miss)
    text_lower = text.lower()
    drugs_found = [drug for drug in DRUG_KEYWORDS if drug in text_lower]
    symptoms_found = [sym for sym in SYMPTOM_KEYWORDS if sym in text_lower]

    return {
        "ner_entities": entities,
        "drugs": list(set(drugs_found)),
        "symptoms": list(set(symptoms_found)),
        "entity_count": len(entities)
    }