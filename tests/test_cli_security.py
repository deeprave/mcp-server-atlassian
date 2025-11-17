"""Tests for CLI security fixes."""

import pytest
from mcp_server_atlassian.cli import start_server


@pytest.mark.asyncio
async def test_invalid_log_level_raises_error():
    """Test that invalid log levels are rejected."""
    with pytest.raises(ValueError, match="Invalid log level: INVALID"):
        await start_server(log_level="INVALID")


@pytest.mark.asyncio
async def test_path_traversal_protection():
    """Test that path traversal attacks are prevented."""
    # Try to write outside current directory
    malicious_path = "../../../etc/passwd"

    with pytest.raises(ValueError, match="Log file must be within current directory"):
        await start_server(log_file=malicious_path)


def test_log_message_sanitization():
    """Test that log messages are sanitized to prevent injection."""
    from mcp_server_atlassian.mcp_log import _sanitize_log_message

    # Test newline sanitization
    malicious_message = "Normal message\nFAKE LOG ENTRY: Admin logged in"
    sanitized = _sanitize_log_message(malicious_message)
    assert "\n" not in sanitized
    assert "\\n" in sanitized

    # Test carriage return sanitization
    malicious_message = "Normal message\rFAKE LOG ENTRY: Admin logged in"
    sanitized = _sanitize_log_message(malicious_message)
    assert "\r" not in sanitized
    assert "\\r" in sanitized

    # Test non-string messages pass through
    non_string_message = 12345
    sanitized = _sanitize_log_message(non_string_message)
    assert sanitized == 12345
