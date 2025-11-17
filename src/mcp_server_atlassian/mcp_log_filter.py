"""Optional log filtering and redaction for MCP logging."""

import re
from typing import Optional, Callable


def redact_sensitive_data(text: str) -> str:
    """Apply basic redaction patterns for sensitive data.

    This function provides basic PII redaction patterns.
    For production use, consider using dedicated packages like logredactor.

    Args:
        text: The log message text to redact

    Returns:
        Text with sensitive data redacted
    """
    # Email addresses
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]", text)

    # Phone numbers (basic patterns)
    text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE]", text)

    # Credit card numbers (basic pattern)
    text = re.sub(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[CARD]", text)

    # API keys (common patterns)
    text = re.sub(r"\b[A-Za-z0-9]{32,}\b", "[API_KEY]", text)

    return text


def get_redaction_function() -> Optional[Callable[[str], str]]:
    """Get the redaction function if filtering is enabled.

    Returns:
        Redaction function or None if filtering should be skipped
    """
    # This could be extended to check configuration or environment variables
    # For now, always return the basic redaction function
    return redact_sensitive_data
