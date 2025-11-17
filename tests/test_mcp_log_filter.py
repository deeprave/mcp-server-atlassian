"""Tests for MCP log filtering and redaction functionality."""

from src.mcp_server_atlassian.mcp_log_filter import redact_sensitive_data, get_redaction_function


class TestRedactSensitiveData:
    """Test cases for sensitive data redaction."""

    def test_email_redaction(self):
        """Test email address redaction."""
        text = "User john.doe@example.com logged in"
        result = redact_sensitive_data(text)
        assert result == "User [EMAIL] logged in"

    def test_phone_redaction(self):
        """Test phone number redaction."""
        text = "Contact: 555-123-4567 or 555.987.6543"
        result = redact_sensitive_data(text)
        assert result == "Contact: [PHONE] or [PHONE]"

    def test_credit_card_redaction(self):
        """Test credit card number redaction."""
        text = "Card: 1234-5678-9012-3456 and 1234567890123456"
        result = redact_sensitive_data(text)
        assert result == "Card: [CARD] and [CARD]"

    def test_api_key_redaction(self):
        """Test API key redaction."""
        text = "API key: abc123def456ghi789jkl012mno345pqr"
        result = redact_sensitive_data(text)
        assert result == "API key: [API_KEY]"

    def test_multiple_patterns(self):
        """Test multiple sensitive patterns in one text."""
        text = "User test@example.com called 555-123-4567 with key abc123def456ghi789jkl012mno345pqr"
        result = redact_sensitive_data(text)
        assert result == "User [EMAIL] called [PHONE] with key [API_KEY]"

    def test_no_sensitive_data(self):
        """Test text with no sensitive data remains unchanged."""
        text = "Normal log message with no sensitive information"
        result = redact_sensitive_data(text)
        assert result == text

    def test_empty_string(self):
        """Test empty string handling."""
        result = redact_sensitive_data("")
        assert result == ""


class TestGetRedactionFunction:
    """Test cases for redaction function retrieval."""

    def test_returns_redaction_function(self):
        """Test that get_redaction_function returns the redaction function."""
        func = get_redaction_function()
        assert func is not None
        assert callable(func)
        assert func == redact_sensitive_data

    def test_returned_function_works(self):
        """Test that the returned function actually redacts data."""
        func = get_redaction_function()
        result = func("Email: test@example.com")
        assert result == "Email: [EMAIL]"
