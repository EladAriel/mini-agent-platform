"""
PII anonymization using Microsoft Presidio.
Replaces personal data with labeled placeholders before LLM invocation and persistence.
No external services — uses local spaCy NER model.

Public API
----------
anonymize_text(text) — call on user task input and on LLM/tool outputs before persistence
"""

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# ── Entity types to detect and replace ───────────────────────────────────────
_PII_ENTITIES = [
    "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION",
    "US_SSN", "US_ITIN", "CREDIT_CARD", "IP_ADDRESS", "IBAN_CODE",
    "US_PASSPORT", "US_DRIVER_LICENSE", "NRP", "DATE_TIME",
    "URL", "MEDICAL_LICENSE", "US_BANK_NUMBER",
]

# ── Module-level singletons (initialized once at import, like guardrail.py's regex) ──
# Failure here (e.g. missing spaCy model) surfaces at startup, not mid-request.
_analyzer = AnalyzerEngine()
_anonymizer = AnonymizerEngine()

# Replace each entity with a labeled placeholder; catch-all for unrecognized types
_OPERATORS: dict = {
    entity: OperatorConfig("replace", {"new_value": f"<{entity}>"})
    for entity in _PII_ENTITIES
}
_OPERATORS["DEFAULT"] = OperatorConfig("replace", {"new_value": "<REDACTED>"})


def anonymize_text(text: str) -> str:
    """
    Detect and replace PII entities in text using Presidio.
    Returns anonymized string; returns original if empty or no PII found.

    Example:
        anonymize_text("Contact John Smith at john@example.com or 555-123-4567.")
        # → "Contact <PERSON> at <EMAIL_ADDRESS> or <PHONE_NUMBER>."

        anonymize_text("")
        # → ""

        anonymize_text("The weather is nice today.")
        # → "The weather is nice today."
    """
    if not text:
        return text
    results = _analyzer.analyze(text=text, language="en", entities=_PII_ENTITIES)
    if not results:
        return text
    return _anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators=_OPERATORS,
    ).text
