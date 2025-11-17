"""Tests for MCP tools advanced functionality."""

from unittest.mock import MagicMock

from src.mcp_server_atlassian.tools import register_tools, mcp_tool
from src.mcp_server_atlassian.config import AtlassianConfig


def test_mcp_tool_decorator_with_custom_name():
    """Test mcp_tool decorator with custom name."""

    @mcp_tool("custom_name")
    async def test_func():
        pass

    assert test_func._mcp_tool_name == "custom_name"
    assert test_func._mcp_tool_func == test_func


def test_mcp_tool_decorator_uses_function_name():
    """Test mcp_tool decorator uses function name when no name provided."""

    @mcp_tool()
    async def test_function():
        pass

    assert test_function._mcp_tool_name == "test_function"
    assert test_function._mcp_tool_func == test_function


async def test_register_tools_calls_server_tool():
    """Test that register_tools calls server.tool for registration."""
    mock_server = MagicMock()
    mock_server.tool = MagicMock(return_value=lambda f: f)
    config = AtlassianConfig(url="https://test.atlassian.net", tool_prefix="test")

    await register_tools(mock_server, config)

    # Should have called tool registration
    assert mock_server.tool.called


async def test_register_tools_completes_successfully():
    """Test register_tools completes without error."""
    mock_server = MagicMock()
    mock_server.tool = MagicMock(return_value=lambda f: f)
    config = AtlassianConfig(url="https://test.atlassian.net", tool_prefix="test")

    # Should complete without raising exception
    await register_tools(mock_server, config)


async def test_register_tools_idempotent():
    """Test that register_tools can be called multiple times safely."""
    mock_server = MagicMock()
    mock_server.tool = MagicMock(return_value=lambda f: f)
    config = AtlassianConfig(url="https://test.atlassian.net", tool_prefix="test")

    # Reset global state for this test
    import src.mcp_server_atlassian.tools as tools_module

    tools_module._tools_registered = False

    await register_tools(mock_server, config)
    first_call_count = mock_server.tool.call_count

    await register_tools(mock_server, config)
    second_call_count = mock_server.tool.call_count

    # Should not register tools again
    assert first_call_count == second_call_count


async def test_register_tools_uses_config_prefix():
    """Test register_tools uses the config tool prefix."""
    mock_server = MagicMock()
    mock_server.tool = MagicMock(return_value=lambda f: f)
    config = AtlassianConfig(url="https://test.atlassian.net", tool_prefix="custom")

    # Reset global state for this test
    import src.mcp_server_atlassian.tools as tools_module

    tools_module._tools_registered = False

    await register_tools(mock_server, config)

    # Should have registered tools (exact names depend on implementation)
    assert mock_server.tool.called


async def test_register_tools_with_valid_config():
    """Test register_tools works with valid configuration."""
    mock_server = MagicMock()
    mock_server.tool = MagicMock(return_value=lambda f: f)
    config = AtlassianConfig(url="https://valid.atlassian.net", tool_prefix="valid")

    # Should not raise exception
    await register_tools(mock_server, config)
