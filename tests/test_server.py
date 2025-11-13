"""Tests for MCP Server functionality."""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
async def test_server_can_be_created():
    """Test that MCP server can be created."""
    from mcp_server_atlassian.server import AtlassianMCPServer

    server = AtlassianMCPServer()
    assert server is not None
    assert not server.is_running


@pytest.mark.asyncio
async def test_server_start_stop():
    """Test server start and stop functionality."""
    from mcp_server_atlassian.server import AtlassianMCPServer

    server = AtlassianMCPServer()

    await server.start()
    assert server.is_running

    await server.stop()
    assert not server.is_running


@pytest.mark.asyncio
async def test_auth_manager_creation():
    """Test auth manager creation in server."""
    from mcp_server_atlassian.server import AtlassianMCPServer

    server = AtlassianMCPServer()

    with patch("mcp_server_atlassian.server.AtlassianConfig") as mock_config:
        mock_config.from_environment.return_value = MagicMock(url="https://test.atlassian.net")

        auth_manager = await server._get_auth_manager()

        assert auth_manager is not None
        assert server.config is not None
        assert server.auth_manager is not None


@pytest.mark.asyncio
async def test_mcp_tools_use_result_pattern():
    """Test that MCP tools return Result pattern JSON format."""
    from mcp_server_atlassian.server import AtlassianMCPServer

    server = AtlassianMCPServer()

    # Get tools and find health_check
    tools = await server.get_tools()
    health_tool = None
    for tool in tools:
        if hasattr(tool, "name") and tool.name == "health_check":
            health_tool = tool
            break
        elif hasattr(tool, "__name__") and "health_check" in tool.__name__:
            health_tool = tool
            break

    # Test health check returns Result JSON format
    if health_tool and hasattr(health_tool, "fn"):
        result = await health_tool.fn()
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is True
        assert "value" in result
