import re
from typing import Dict
import os

EMAIL_REGEX = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
PHONE_REGEX = r'\+?91[\-\s]?\d{5}[\-\s]?\d{5}\b|\b\d{5}[\-\s]?\d{5}\b|\b\d{10}\b'
AADHAAR_REGEX = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'

# Heuristic name patterns with lookahead to prevent Dr vs doctor collision
NAME_PATTERNS = [
    (r'(?i)Dr\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', "Dr. [REDACTED NAME]"),
    (r'(?i)doctor\s+(?!Dr\b)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', "doctor [REDACTED NAME]"),
    (r'(?i)my name is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', "[REDACTED NAME]"),
    (r'(?i)i am\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', "[REDACTED NAME]"),
]

# Real Microsoft Presidio Analyzer loader with resource limit safety
analyzer = None
anonymizer = None
PRESIDIO_AVAILABLE = False

if not os.getenv("RENDER") and os.getenv("DISABLE_AI_MODELS") != "true":
    try:
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine
        analyzer = AnalyzerEngine()
        anonymizer = AnonymizerEngine()
        PRESIDIO_AVAILABLE = True
        print("Microsoft Presidio PII engines loaded successfully.")
    except Exception as e:
        print(f"Presidio loading skipped or failed: {e}. Using regex-based PII filter.")


def detect_pii(text: str) -> Dict:
    pii_types = []
    masked_content = text

    # Try Presidio first
    if PRESIDIO_AVAILABLE and analyzer is not None and anonymizer is not None:
        try:
            results = analyzer.analyze(text=text, language="en")
            if results:
                anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
                masked_content = anonymized_result.text
                for res in results:
                    pii_types.append(res.entity_type)
        except Exception as e:
            print(f"Presidio execution failed: {e}. Falling back to regex.")

    # Fallback/Supplemental regex patterns (guarantees Aadhaar and phone number masking)
    if re.search(EMAIL_REGEX, text):
        if "EMAIL" not in pii_types:
            pii_types.append("EMAIL")
        masked_content = re.sub(EMAIL_REGEX, "[REDACTED EMAIL]", masked_content)

    if re.search(AADHAAR_REGEX, text):
        if "AADHAAR" not in pii_types:
            pii_types.append("AADHAAR")
        masked_content = re.sub(AADHAAR_REGEX, "[REDACTED AADHAAR]", masked_content)

    if re.search(PHONE_REGEX, text):
        if "PHONE" not in pii_types:
            pii_types.append("PHONE")
        masked_content = re.sub(PHONE_REGEX, "[REDACTED PHONE]", masked_content)

    # Heuristic names patterns
    has_name = False
    for pattern, replacement in NAME_PATTERNS:
        match = re.search(pattern, masked_content)
        if match:
            full_match = match.group(0)
            name_part = match.group(1)
            if name_part.lower() not in ["nauseous", "vomiting", "sick", "better", "having", "taking"]:
                has_name = True
                masked_full = full_match.replace(name_part, "[REDACTED NAME]")
                masked_content = masked_content.replace(full_match, masked_full)
                
    if has_name and "NAME" not in pii_types:
        pii_types.append("NAME")

    # Standardize types
    pii_types_clean = []
    for t in pii_types:
        if t == "PERSON":
            pii_types_clean.append("NAME")
        elif t in ["PHONE_NUMBER", "PHONE"]:
            pii_types_clean.append("PHONE")
        elif t in ["EMAIL_ADDRESS", "EMAIL"]:
            pii_types_clean.append("EMAIL")
        else:
            pii_types_clean.append(t)

    return {
        "has_pii": len(pii_types_clean) > 0,
        "pii_types": list(set(pii_types_clean)),
        "masked_content": masked_content
    }