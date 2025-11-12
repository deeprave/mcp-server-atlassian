"""Test server functionality."""
import pytest


def test_fastmcp_server_can_be_created():
    """Test that FastMCP server can be created."""
    from mcp_server_atlassian.server import AtlassianMCPServer
    
    server = AtlassianMCPServer()
    # Should have FastMCP server instance
    assert hasattr(server, 'mcp_server')
    assert server.mcp_server is not None


@pytest.mark.asyncio
async def test_server_can_start_and_stop():
    """Test that server can start and stop."""
    from mcp_server_atlassian.server import AtlassianMCPServer
    
    server = AtlassianMCPServer()
    
    # Should start without error
    await server.start()
    assert server.is_running
    
    # Should stop without error
    await server.stop()
    assert not server.is_running


@pytest.mark.asyncio
async def test_server_has_health_check_tool():
    """Test that server has a health check tool registered."""
    from mcp_server_atlassian.server import AtlassianMCPServer
    
    server = AtlassianMCPServer()
    # Should have tools registered
    tools = await server.get_tools()
    assert len(tools) > 0
    
    # Should have health check tool
    # Tools are returned as strings (tool names)
    assert any("health" in tool.lower() for tool in tools)
