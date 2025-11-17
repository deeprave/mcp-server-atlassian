"""Tests for MCP logging advanced functionality."""

import tempfile
import os
import logging
from unittest.mock import patch

from src.mcp_server_atlassian.mcp_log import (
    configure,
    add_file_handler,
    remove_file_handler,
    _get_log_level,
    _sanitize_log_message,
)


def test_configure_with_file_creates_handler():
    """Test that configure with file path creates file handler."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            configure(level="INFO", file_path=temp_file.name)
            # File should exist after configuration
            assert os.path.exists(temp_file.name)
        finally:
            os.unlink(temp_file.name)


def test_add_file_handler_creates_parent_directory():
    """Test that add_file_handler creates parent directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create directory structure first
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir, exist_ok=True)
        log_file = os.path.join(subdir, "test.log")

        add_file_handler(log_file, "INFO", False)

        # File should be created
        assert os.path.exists(log_file)


def test_add_file_handler_json_format():
    """Test add_file_handler with JSON format."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            add_file_handler(temp_file.name, "DEBUG", json_format=True)
            # File should exist
            assert os.path.exists(temp_file.name)
        finally:
            os.unlink(temp_file.name)


def test_remove_file_handler_nonexistent():
    """Test removing non-existent file handler succeeds."""
    # Should not raise exception
    remove_file_handler("/nonexistent/path.log")


def test_get_log_level_standard_levels():
    """Test _get_log_level with standard logging levels."""
    assert _get_log_level("DEBUG") == logging.DEBUG
    assert _get_log_level("INFO") == logging.INFO
    assert _get_log_level("WARNING") == logging.WARNING
    assert _get_log_level("ERROR") == logging.ERROR
    assert _get_log_level("CRITICAL") == logging.CRITICAL


def test_get_log_level_case_insensitive():
    """Test _get_log_level handles case variations."""
    assert _get_log_level("debug") == logging.DEBUG
    assert _get_log_level("Info") == logging.INFO
    assert _get_log_level("WARNING") == logging.WARNING


def test_get_log_level_trace():
    """Test _get_log_level with TRACE level."""
    trace_level = _get_log_level("TRACE")
    assert trace_level == 5


def test_get_log_level_invalid_defaults_to_info():
    """Test _get_log_level with invalid level returns INFO."""
    assert _get_log_level("INVALID") == logging.INFO


def test_sanitize_log_message_removes_newlines():
    """Test that _sanitize_log_message removes newline characters."""
    message = "Line 1\nLine 2\rLine 3\r\nLine 4"
    result = _sanitize_log_message(message)
    # Should replace newlines with spaces
    assert "\n" not in result
    assert "\r" not in result
    assert "Line 1" in result
    assert "Line 2" in result
    assert "Line 3" in result
    assert "Line 4" in result


def test_sanitize_log_message_empty_string():
    """Test sanitizing empty string."""
    result = _sanitize_log_message("")
    assert result == ""


def test_sanitize_log_message_no_newlines():
    """Test sanitizing message without newlines."""
    message = "Normal log message"
    result = _sanitize_log_message(message)
    assert result == message


@patch("src.mcp_server_atlassian.mcp_log._FASTMCP_AVAILABLE", True)
@patch("src.mcp_server_atlassian.mcp_log.configure_logging")
def test_configure_uses_fastmcp_when_available(mock_configure_logging):
    """Test configure uses FastMCP when available."""
    configure(level="DEBUG")
    mock_configure_logging.assert_called_once_with(level="DEBUG")


@patch("src.mcp_server_atlassian.mcp_log._FASTMCP_AVAILABLE", False)
@patch("logging.basicConfig")
def test_configure_uses_basic_config_when_fastmcp_unavailable(mock_basic_config):
    """Test configure uses basicConfig when FastMCP unavailable."""
    configure(level="INFO")
    mock_basic_config.assert_called_once_with(level=logging.INFO)
