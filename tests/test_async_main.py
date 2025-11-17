"""Test async main functionality."""

import inspect
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
async def test_start_server_function_exists():
    """Test that start_server function exists and can be called."""
    from mcp_server_atlassian.cli import start_server

    # The function exists and is callable
    assert callable(start_server)
    assert inspect.iscoroutinefunction(start_server)


@pytest.mark.asyncio
async def test_start_server_uses_safe_config():
    """Test that start_server gets configuration safely."""
    from mcp_server_atlassian.cli import start_server
    from mcp_server_atlassian.config import AtlassianConfig
    from mcp_server_atlassian.result import Result
    from unittest.mock import AsyncMock

    mock_config = AtlassianConfig(url="https://test.atlassian.net")
    mock_result = Result.ok(mock_config)

    with (
        patch("mcp_server_atlassian.cli.AtlassianConfig.from_environment_safe", return_value=mock_result),
        patch("mcp_server_atlassian.mcp_log.configure") as mock_configure,
        patch("mcp_server_atlassian.server.AtlassianMCPServer") as mock_server_class,
    ):
        mock_server = MagicMock()
        mock_server.start = AsyncMock()
        mock_server.stop = AsyncMock()
        mock_server.mcp_server.run_async = AsyncMock()
        mock_server_class.return_value = mock_server

        await start_server()

        # Verify logging was configured
        mock_configure.assert_called_once_with(level="INFO")
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
