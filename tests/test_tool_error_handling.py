"""Test tool error handling."""

import os
import pytest
from mcp_server_atlassian.server import AtlassianMCPServer


@pytest.mark.asyncio
async def test_get_auth_manager_handles_missing_config():
    """Test that _get_auth_manager handles missing config gracefully."""
    # Ensure ATLASSIAN_URL is not set
    original_url = os.environ.get("ATLASSIAN_URL")
    if "ATLASSIAN_URL" in os.environ:
        del os.environ["ATLASSIAN_URL"]

    try:
        server = AtlassianMCPServer()

        # Should raise ValueError with helpful message, not crash
        with pytest.raises(ValueError) as exc_info:
            await server._get_auth_manager()

        assert "Configuration error" in str(exc_info.value)
        assert "ATLASSIAN_URL" in str(exc_info.value)

    finally:
        # Restore original value
        if original_url:
            os.environ["ATLASSIAN_URL"] = original_url
