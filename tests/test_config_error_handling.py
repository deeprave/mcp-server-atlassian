"""Test configuration error handling."""

import os
from mcp_server_atlassian.config import AtlassianConfig


def test_config_from_environment_missing_url_returns_validation_result():
    """Test that missing ATLASSIAN_URL returns validation result instead of raising."""
    # Ensure ATLASSIAN_URL is not set
    original_url = os.environ.get("ATLASSIAN_URL")
    if "ATLASSIAN_URL" in os.environ:
        del os.environ["ATLASSIAN_URL"]

    try:
        # Should return validation result, not raise exception
        result = AtlassianConfig.from_environment_safe()

        assert result is not None
        assert hasattr(result, "success")
        assert result.success is False
        assert "ATLASSIAN_URL" in result.error

    finally:
        # Restore original value
        if original_url:
            os.environ["ATLASSIAN_URL"] = original_url


def test_config_from_environment_with_valid_url_succeeds():
    """Test that valid ATLASSIAN_URL creates successful config."""
    # Set valid URL
    original_url = os.environ.get("ATLASSIAN_URL")
    os.environ["ATLASSIAN_URL"] = "https://test.atlassian.net"

    try:
        result = AtlassianConfig.from_environment_safe()

        assert result is not None
        assert hasattr(result, "success")
        assert result.success is True
        assert result.value.url == "https://test.atlassian.net"

    finally:
        # Restore original value
        if original_url:
            os.environ["ATLASSIAN_URL"] = original_url
        elif "ATLASSIAN_URL" in os.environ:
            del os.environ["ATLASSIAN_URL"]
