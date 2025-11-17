"""Test error context for MCP error reporting."""

from mcp_server_atlassian.error_context import ErrorContext


def test_error_context_report_config_error():
    """Test that ErrorContext can report configuration errors."""
    ctx = ErrorContext()

    # Should be able to report config error without raising exception
    result = ctx.report_config_error("ATLASSIAN_URL is not set")

    assert result is not None
    assert "ATLASSIAN_URL is not set" in str(result)


def test_error_context_report_runtime_error():
    """Test that ErrorContext can report runtime errors."""
    ctx = ErrorContext()

    # Should be able to report runtime error without raising exception
    result = ctx.report_runtime_error("Connection failed")

    assert result is not None
    assert "Connection failed" in str(result)
