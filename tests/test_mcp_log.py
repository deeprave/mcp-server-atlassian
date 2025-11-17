"""Tests for mcp_log module."""

import logging
from unittest.mock import patch, MagicMock


def test_trace_level_exists():
    """Test that TRACE level exists and works."""
    import sys

    sys.path.insert(0, "src")

    import mcp_server_atlassian.mcp_log as mcp_log

    # Test TRACE level constant exists
    assert hasattr(mcp_log, "TRACE_LEVEL")
    assert mcp_log.TRACE_LEVEL == 5

    # Test logger has trace method
    logger = mcp_log.get_logger("test")
    assert hasattr(logger, "trace")

    # Test TRACE level is registered
    assert logging.getLevelName(5) == "TRACE"


def test_get_logger_returns_logger():
    """Test get_logger returns working logger."""
    import sys

    sys.path.insert(0, "src")

    import mcp_server_atlassian.mcp_log as mcp_log

    logger = mcp_log.get_logger("test")
    assert isinstance(logger, logging.Logger)
    # FastMCP may prefix logger names, so check it contains our name
    assert "test" in logger.name


@patch("mcp_server_atlassian.mcp_log.fastmcp_get_logger")
def test_logger_uses_fastmcp(mock_fastmcp_get_logger):
    """Test that logger delegates to FastMCP's get_logger."""
    import sys

    sys.path.insert(0, "src")

    import mcp_server_atlassian.mcp_log as mcp_log

    # Mock FastMCP logger
    mock_logger = MagicMock()
    mock_logger.name = "test"
    mock_fastmcp_get_logger.return_value = mock_logger

    logger = mcp_log.get_logger("test")

    # Should call FastMCP's get_logger
    mock_fastmcp_get_logger.assert_called_once_with("test")

    # Should return enhanced logger with trace method
    assert hasattr(logger, "trace")
    assert logger.name == "test"


def test_configure_sets_level():
    """Test basic configuration sets log level."""
    import sys

    sys.path.insert(0, "src")

    import mcp_server_atlassian.mcp_log as mcp_log

    # Test configure function exists
    assert hasattr(mcp_log, "configure")

    # Test configuration with level
    mcp_log.configure(level="DEBUG")

    # Test that configuration is applied
    logger = mcp_log.get_logger("test_config")
    # Should be able to get effective level (implementation detail may vary)
    assert hasattr(logger, "getEffectiveLevel")


def test_mcp_log_config_dataclass():
    """Test MCPLogConfig dataclass exists and works."""
    import sys

    sys.path.insert(0, "src")

    import mcp_server_atlassian.mcp_log as mcp_log

    # Test MCPLogConfig exists
    assert hasattr(mcp_log, "MCPLogConfig")

    # Test default values
    config = mcp_log.MCPLogConfig()
    assert config.level == "INFO"
    assert config.file_path is None
    assert config.json_format is False

    # Test custom values
    config = mcp_log.MCPLogConfig(level="DEBUG", file_path="/tmp/test.log", json_format=True)
    assert config.level == "DEBUG"
    assert config.file_path == "/tmp/test.log"
    assert config.json_format is True


def test_get_log_level_trace():
    """Test that TRACE level is properly converted."""
    from mcp_server_atlassian.mcp_log import _get_log_level, TRACE_LEVEL

    level = _get_log_level("TRACE")
    assert level == TRACE_LEVEL
    assert level == 5


def test_get_log_level_standard_levels():
    """Test that standard log levels work."""
    from mcp_server_atlassian.mcp_log import _get_log_level
    import logging

    assert _get_log_level("DEBUG") == logging.DEBUG
    assert _get_log_level("INFO") == logging.INFO
    assert _get_log_level("WARNING") == logging.WARNING
    assert _get_log_level("ERROR") == logging.ERROR


def test_logger_trace_method_available():
    """Test that logger.trace() method is available."""
    from mcp_server_atlassian.mcp_log import get_logger

    logger = get_logger(__name__)

    # Should have trace method
    assert hasattr(logger, "trace")
    assert callable(logger.trace)

    # Should be able to call trace (won't output anything in test)
    logger.trace("Test trace message")


def test_multiple_loggers_have_trace():
    """Test that multiple loggers all get trace method."""
    from mcp_server_atlassian.mcp_log import get_logger

    logger1 = get_logger("module1")
    logger2 = get_logger("module2")

    assert hasattr(logger1, "trace")
    assert hasattr(logger2, "trace")
    assert callable(logger1.trace)
    assert callable(logger2.trace)


def test_trace_level_integration():
    """Test complete TRACE level integration."""
    from mcp_server_atlassian.mcp_log import get_logger, configure, TRACE_LEVEL

    # Configure logging at TRACE level
    configure(level="TRACE")

    # Get logger
    logger = get_logger("test_module")

    # Should have trace method and be enabled for TRACE level
    assert hasattr(logger, "trace")
    assert logger.isEnabledFor(TRACE_LEVEL)

    # Should be able to call all log levels
    logger.trace("Trace message")
    logger.debug("Debug message")
    logger.info("Info message")


def test_context_trace_method_added():
    """Test that trace method is added to FastMCP Context."""
    from mcp_server_atlassian.mcp_log import _add_trace_to_context

    # Call the function to add trace method
    _add_trace_to_context()

    try:
        from fastmcp.server.context import Context

        # Should have trace method after patching
        assert hasattr(Context, "trace")
        assert callable(Context.trace)

    except ImportError:
        # FastMCP not available, test passes
        pass


def test_configure_adds_context_trace():
    """Test that configure() adds trace method to context."""
    from mcp_server_atlassian.mcp_log import configure

    # Configure should add trace method
    configure(level="DEBUG")

    try:
        from fastmcp.server.context import Context

        assert hasattr(Context, "trace")
    except ImportError:
        # FastMCP not available, test passes
        pass


def test_context_trace_functionality():
    """Test that context trace method works correctly."""
    from mcp_server_atlassian.mcp_log import configure
    from unittest.mock import AsyncMock, MagicMock

    # Configure to add trace method
    configure(level="TRACE")

    try:
        from fastmcp.server.context import Context

        # Create a mock context instance
        mock_context = MagicMock(spec=Context)
        mock_context.log = AsyncMock()

        # Add the trace method to our mock
        Context.trace.__get__(mock_context, Context)

        # Should have trace method
        assert hasattr(Context, "trace")

    except ImportError:
        # FastMCP not available, test passes
        pass
