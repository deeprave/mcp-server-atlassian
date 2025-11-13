"""Test async main functionality."""

import inspect
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
async def test_async_main_function_exists():
    """Test that async main function exists and can be called."""
    from mcp_server_atlassian.__main__ import async_main

    # The function exists and is callable
    assert callable(async_main)
    assert inspect.iscoroutinefunction(async_main)


@pytest.mark.asyncio
async def test_async_main_uses_cli_config():
    """Test that async_main gets configuration from CLI."""
    from mcp_server_atlassian.__main__ import async_main
    from mcp_server_atlassian.config import AtlassianConfig
    from unittest.mock import AsyncMock

    mock_config = AtlassianConfig(url="https://test.atlassian.net")

    with (
        patch("mcp_server_atlassian.__main__.get_config", return_value=mock_config),
        patch("mcp_server_atlassian.__main__.AtlassianMCPServer") as mock_server_class,
    ):
        mock_server = MagicMock()
        mock_server.start = AsyncMock()
        mock_server.stop = AsyncMock()
        mock_server.mcp_server.run_async = AsyncMock()
        mock_server_class.return_value = mock_server

        await async_main()

        # Verify config was set on server
        assert mock_server.config == mock_config
        mock_server.start.assert_called_once()
        mock_server.stop.assert_called_once()


def test_server_class_can_be_instantiated():
    """Test that server class can be created."""
    from mcp_server_atlassian.server import AtlassianMCPServer

    server = AtlassianMCPServer()
    assert server is not None
    assert hasattr(server, "start")
    assert hasattr(server, "stop")
