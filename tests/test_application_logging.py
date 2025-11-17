"""Tests for application logging integration."""

import pytest


def test_server_uses_mcp_log():
    """Test that server.py uses mcp_log."""
    from mcp_server_atlassian.server import logger

    # Verify logger is from mcp_log
    assert hasattr(logger, "trace")
    assert logger.name.endswith("server")


def test_main_uses_mcp_log():
    """Test that main.py uses mcp_log."""
    from mcp_server_atlassian.main import logger

    # Verify logger is from mcp_log
    assert hasattr(logger, "trace")
    assert logger.name.endswith("main")


@pytest.mark.asyncio
async def test_server_logging_integration():
    """Test server logging integration."""
    from mcp_server_atlassian.server import AtlassianMCPServer
    from mcp_server_atlassian.config import AtlassianConfig

    server = AtlassianMCPServer()

    # Set a config to test logging
    server.config = AtlassianConfig(url="https://test.atlassian.net")

    # Should not raise exceptions
    await server.start()
    await server.stop()


def test_main_logging_integration():
    """Test main module logging integration."""
    from mcp_server_atlassian import main

    # Should be able to import without issues
    assert hasattr(main, "logger")
    assert hasattr(main.logger, "trace")
