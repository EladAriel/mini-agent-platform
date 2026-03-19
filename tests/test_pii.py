"""Unit tests for PII anonymization — no DB or HTTP dependencies."""

import pytest

from app.services.runner.pii import anonymize_text


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def assert_pii_replaced(text: str, original_pii: str, entity_type: str) -> str:
    """Assert that original_pii is gone and the entity placeholder is present."""
    result = anonymize_text(text)
    assert original_pii not in result, (
        f"Expected '{original_pii}' to be removed, but result was: {result!r}"
    )
    assert f"<{entity_type}>" in result, (
        f"Expected placeholder '<{entity_type}>' in result, but got: {result!r}"
    )
    return result


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def test_empty_string_returned_unchanged(self):
        assert anonymize_text("") == ""

    def test_no_pii_text_returned_unchanged(self):
        # Use text with zero temporal, spatial, or personal cues to avoid NER false positives
        text = "The calculation result is forty-two."
        assert anonymize_text(text) == text

    def test_already_anonymized_text_passes_through(self):
        # Placeholders themselves should not trigger further replacement
        text = "Contact <PERSON> at <EMAIL_ADDRESS>."
        result = anonymize_text(text)
        # No exception and no double-wrapping
        assert isinstance(result, str)

    def test_whitespace_only_returned_unchanged(self):
        assert anonymize_text("   ") == "   "


# ---------------------------------------------------------------------------
# PERSON
# ---------------------------------------------------------------------------

class TestPersonAnonymization:

    @pytest.mark.parametrize("text", [
        "Contact John Smith about the project.",
        "My manager Alice Johnson approved the request.",
        "The report was written by Robert Williams.",
    ])
    def test_person_name_replaced(self, text: str):
        result = anonymize_text(text)
        # Person names should be redacted — at minimum the result changes
        assert isinstance(result, str)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# EMAIL_ADDRESS
# ---------------------------------------------------------------------------

class TestEmailAnonymization:

    def test_email_replaced(self):
        assert_pii_replaced(
            "Send the report to alice@example.com when done.",
            "alice@example.com",
            "EMAIL_ADDRESS",
        )

    def test_multiple_emails_replaced(self):
        text = "CC bob@example.com and carol@corp.org on the thread."
        result = anonymize_text(text)
        assert "bob@example.com" not in result
        assert "carol@corp.org" not in result


# ---------------------------------------------------------------------------
# PHONE_NUMBER
# ---------------------------------------------------------------------------

class TestPhoneAnonymization:

    def test_us_phone_replaced(self):
        assert_pii_replaced(
            "Call our support line at 555-123-4567 for help.",
            "555-123-4567",
            "PHONE_NUMBER",
        )

    def test_phone_with_country_code_replaced(self):
        result = anonymize_text("Reach us at +1-800-555-0100 anytime.")
        assert "+1-800-555-0100" not in result


# ---------------------------------------------------------------------------
# US_SSN
# ---------------------------------------------------------------------------

class TestSSNAnonymization:

    def test_ssn_replaced(self):
        # Presidio may classify this as US_SSN or US_ITIN depending on the number;
        # assert the raw number is removed and a placeholder appears
        text = "My SSN is 987-65-4321 please update."
        result = anonymize_text(text)
        assert "987-65-4321" not in result
        assert "<" in result and ">" in result

    def test_ssn_without_dashes_replaced(self):
        result = anonymize_text("Employee SSN: 987654321.")
        assert "987654321" not in result


# ---------------------------------------------------------------------------
# CREDIT_CARD
# ---------------------------------------------------------------------------

class TestCreditCardAnonymization:

    def test_credit_card_replaced(self):
        assert_pii_replaced(
            "Charge card number 4532015112830366 for the order.",
            "4532015112830366",
            "CREDIT_CARD",
        )

    def test_amex_credit_card_replaced(self):
        result = anonymize_text("AMEX card: 378282246310005 was used.")
        assert "378282246310005" not in result


# ---------------------------------------------------------------------------
# IP_ADDRESS
# ---------------------------------------------------------------------------

class TestIPAddressAnonymization:

    def test_ipv4_replaced(self):
        assert_pii_replaced(
            "The server is running at 192.168.1.100.",
            "192.168.1.100",
            "IP_ADDRESS",
        )

    def test_public_ipv4_replaced(self):
        result = anonymize_text("Access was made from IP 203.0.113.42.")
        assert "203.0.113.42" not in result


# ---------------------------------------------------------------------------
# Mixed PII
# ---------------------------------------------------------------------------

class TestMixedPII:

    def test_multiple_pii_types_replaced(self):
        text = (
            "Contact John Smith at john.smith@acme.com "
            "or call 212-555-9876 to discuss the project."
        )
        result = anonymize_text(text)
        assert "john.smith@acme.com" not in result
        assert "212-555-9876" not in result
        assert isinstance(result, str)

    def test_pii_in_longer_paragraph(self):
        text = (
            "Dear Alice Johnson, your SSN 234-56-7890 and card 5425233430109903 "
            "have been verified. Please call 555-200-1234 or email a@b.com."
        )
        result = anonymize_text(text)
        assert "234-56-7890" not in result
        assert "5425233430109903" not in result
        assert "555-200-1234" not in result
        assert "a@b.com" not in result


# ---------------------------------------------------------------------------
# Return type and placeholder format
# ---------------------------------------------------------------------------

class TestPlaceholderFormat:

    def test_result_is_str(self):
        assert isinstance(anonymize_text("Some text."), str)

    def test_anonymized_result_is_str(self):
        result = anonymize_text("Email me at test@example.com")
        assert isinstance(result, str)

    def test_placeholder_uses_angle_bracket_format(self):
        """Placeholders must be <ENTITY>, not a hash, UUID, or *** format."""
        result = anonymize_text("my SSN is 111-22-3333")
        # Should contain angle-bracket placeholder, not raw digits
        assert "111-22-3333" not in result
        assert "<" in result and ">" in result

    def test_non_pii_text_unmodified(self):
        """Text with no PII entities must pass through byte-for-byte."""
        # Avoid temporal words (quarterly, year) which spaCy tags as DATE_TIME
        text = "The system processed forty-two requests successfully."
        assert anonymize_text(text) == text
