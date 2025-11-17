"""Tests for MCP tools registration and prefixing."""

import pytest
from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_tools_are_registered_with_prefix():
    """Test that tools are registered with the configured prefix."""
    from mcp_server_atlassian.tools import register_tools
    from mcp_server_atlassian.config import AtlassianConfig

    # Reset global state for test
    import mcp_server_atlassian.tools as tools_module

    tools_module._tools_registered = False

    # Create mock server
    mock_server = MagicMock()
    mock_tool_decorator = MagicMock()
    mock_server.tool.return_value = mock_tool_decorator

    # Create config with custom prefix
    config = AtlassianConfig(url="https://test.atlassian.net", tool_prefix="custom")

    # Register tools
    await register_tools(mock_server, config)

    # Verify tools were registered with prefix
    calls = mock_server.tool.call_args_list
    assert len(calls) == 2

    # Check that tools were registered with custom prefix
    registered_names = [call.kwargs.get("name") for call in calls]
    assert "custom_health_check" in registered_names
    assert "custom_setup_atlassian_credentials" in registered_names


@pytest.mark.asyncio
async def test_tools_registration_is_idempotent():
    """Test that tools registration only happens once."""
    from mcp_server_atlassian.tools import register_tools
    from mcp_server_atlassian.config import AtlassianConfig

    # Reset global state for test
    import mcp_server_atlassian.tools as tools_module

    tools_module._tools_registered = False

    # Create mock server
    mock_server = MagicMock()
    mock_tool_decorator = MagicMock()
    mock_server.tool.return_value = mock_tool_decorator

    config = AtlassianConfig(url="https://test.atlassian.net")

    # Register tools twice
    await register_tools(mock_server, config)
    await register_tools(mock_server, config)

    # Should only be called once (2 tools registered once each)
    assert mock_server.tool.call_count == 2


@pytest.mark.asyncio
async def test_default_prefix_is_applied():
    """Test that default 'atl' prefix is applied."""
    from mcp_server_atlassian.tools import register_tools
    from mcp_server_atlassian.config import AtlassianConfig

    # Reset global state for test
    import mcp_server_atlassian.tools as tools_module

    tools_module._tools_registered = False

    # Create mock server
    mock_server = MagicMock()
    mock_tool_decorator = MagicMock()
    mock_server.tool.return_value = mock_tool_decorator

    # Create config with default prefix
    config = AtlassianConfig(url="https://test.atlassian.net")  # default tool_prefix="atl"

    # Register tools
    await register_tools(mock_server, config)

    # Verify tools were registered with default prefix
    calls = mock_server.tool.call_args_list
    registered_names = [call.kwargs.get("name") for call in calls]
    assert "atl_health_check" in registered_names
    assert "atl_setup_atlassian_credentials" in registered_names


def test_mcp_tool_decorator():
    """Test the mcp_tool decorator functionality."""
    from mcp_server_atlassian.tools import mcp_tool

    @mcp_tool("test_tool")
    async def sample_tool():
        return {"result": "test"}

    # Check that decorator adds metadata
    assert hasattr(sample_tool, "_mcp_tool_name")
    assert hasattr(sample_tool, "_mcp_tool_func")
    assert sample_tool._mcp_tool_name == "test_tool"
    assert sample_tool._mcp_tool_func == sample_tool


def test_mcp_tool_decorator_with_default_name():
    """Test the mcp_tool decorator with default function name."""
    from mcp_server_atlassian.tools import mcp_tool

    @mcp_tool()
    async def another_sample_tool():
        return {"result": "test"}

    # Check that decorator uses function name as default
    assert another_sample_tool._mcp_tool_name == "another_sample_tool"
