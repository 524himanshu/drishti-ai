from typing import Dict

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


def extract_entities(text: str) -> Dict:
    text_lower = text.lower()

    drugs_found = [drug for drug in DRUG_KEYWORDS if drug in text_lower]
    symptoms_found = [sym for sym in SYMPTOM_KEYWORDS if sym in text_lower]

    entities = []

    for drug in drugs_found:
        entities.append({
            "text": drug,
            "label": "DRUG"
        })

    for symptom in symptoms_found:
        entities.append({
            "text": symptom,
            "label": "SYMPTOM"
        })

    return {
        "ner_entities": entities,
        "drugs": list(set(drugs_found)),
        "symptoms": list(set(symptoms_found)),
        "entity_count": len(entities)
    }