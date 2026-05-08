import re
from typing import Dict

EMAIL_REGEX = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
PHONE_REGEX = r'\b\d{10}\b'


def detect_pii(text: str) -> Dict:
    pii_types = []

    if re.search(EMAIL_REGEX, text):
        pii_types.append("EMAIL")

    if re.search(PHONE_REGEX, text):
        pii_types.append("PHONE")

    return {
        "has_pii": len(pii_types) > 0,
        "pii_types": pii_types
    }