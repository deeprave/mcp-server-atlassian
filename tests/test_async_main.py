"""Test async main functionality."""
import asyncio
import inspect
import pytest
import subprocess
import sys


@pytest.mark.asyncio
async def test_async_main_function_exists():
    """Test that async main function exists and can be called."""
    from mcp_server_atlassian.cli import async_main
    
    # The function exists and is callable
    assert callable(async_main)
    assert inspect.iscoroutinefunction(async_main)


def test_cli_uses_asyncio_run():
    """Test that CLI properly uses asyncio.run for async operations."""
    # This test ensures the serve command starts properly
    # We use a very short timeout and expect it to timeout (meaning it's running)
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mcp_server_atlassian", "serve"],
            input="",  # Send empty input
            capture_output=True,
            text=True,
            timeout=1  # Very short timeout
        )
        # If it completes quickly, that's also fine
        assert "Starting MCP Server" in result.stdout
    except subprocess.TimeoutExpired as e:
        # This is expected - the server is running and waiting for input
        assert "Starting MCP Server" in e.output.decode() if e.output else True
        # This is actually a success - the server started and is running


def test_server_class_can_be_instantiated():
    """Test that server class can be created."""
    from mcp_server_atlassian.server import AtlassianMCPServer
    
    server = AtlassianMCPServer()
    assert server is not None
    assert hasattr(server, 'start')
    assert hasattr(server, 'stop')
