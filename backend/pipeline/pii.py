import re
from typing import Dict

EMAIL_REGEX = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
PHONE_REGEX = r'(?:\+91[\-\s]?)?[6-9]\d{9}\b|\b\d{10}\b|\b\+91\s\d{5}[-\s]?\d{5}\b'
AADHAAR_REGEX = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'

# Heuristic name patterns
NAME_PATTERNS = [
    (r'(?i)my name is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', "[REDACTED NAME]"),
    (r'(?i)i am\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', "[REDACTED NAME]"),
    (r'(?i)Dr\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', "Dr. [REDACTED NAME]"),
    (r'(?i)doctor\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', "doctor [REDACTED NAME]"),
]

def detect_pii(text: str) -> Dict:
    pii_types = []
    masked_content = text

    # 1. Detect and mask Email
    if re.search(EMAIL_REGEX, text):
        pii_types.append("EMAIL")
        masked_content = re.sub(EMAIL_REGEX, "[REDACTED EMAIL]", masked_content)

    # 2. Detect and mask Aadhaar
    if re.search(AADHAAR_REGEX, text):
        pii_types.append("AADHAAR")
        masked_content = re.sub(AADHAAR_REGEX, "[REDACTED AADHAAR]", masked_content)

    # 3. Detect and mask Phone
    if re.search(PHONE_REGEX, text):
        pii_types.append("PHONE")
        masked_content = re.sub(PHONE_REGEX, "[REDACTED PHONE]", masked_content)

    # 4. Detect and mask Names using patterns
    has_name = False
    for pattern, replacement in NAME_PATTERNS:
        match = re.search(pattern, masked_content)
        if match:
            full_match = match.group(0)
            name_part = match.group(1)
            # Make sure we don't replace common words
            if name_part.lower() not in ["nauseous", "vomiting", "sick", "better", "having", "taking"]:
                has_name = True
                masked_full = full_match.replace(name_part, "[REDACTED NAME]")
                masked_content = masked_content.replace(full_match, masked_full)
                
    if has_name:
        pii_types.append("NAME")

    return {
        "has_pii": len(pii_types) > 0,
        "pii_types": list(set(pii_types)),
        "masked_content": masked_content
    }