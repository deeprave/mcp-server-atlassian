"""Test configuration functionality."""

import os
import pytest
from unittest.mock import patch, AsyncMock


def test_configuration_class_can_be_created():
    """Test that the configuration class can be created."""
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")
    assert config is not None
    assert config.url == "https://test.atlassian.net"


def test_configuration_has_default_values():
    """Test that configuration has sensible default values."""
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")
    assert config.timeout == 30
    assert config.verify_ssl is True
    assert config.backoff_and_retry is True
    assert config.max_backoff_seconds == 1800
    assert config.max_backoff_retries == 1000
    assert config.retry_status_codes == [413, 429, 503]
    assert config.cloud is True
    assert config.tool_prefix == "atl"


def test_configuration_from_environment():
    """Test that configuration can be loaded from environment variables."""
    from mcp_server_atlassian.config import AtlassianConfig

    with patch.dict(os.environ, {"ATLASSIAN_URL": "https://company.atlassian.net", "MCP_TOOL_PREFIX": "custom"}):
        config = AtlassianConfig.from_environment()
        assert config.url == "https://company.atlassian.net"
        assert config.tool_prefix == "custom"


def test_configuration_from_environment_missing_url():
    """Test that missing ATLASSIAN_URL raises appropriate error."""
    from mcp_server_atlassian.config import AtlassianConfig

    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="ATLASSIAN_URL"):
            AtlassianConfig.from_environment()


def test_url_validation_valid_urls():
    """Test that valid URLs pass validation."""
    from mcp_server_atlassian.config import AtlassianConfig

    valid_urls = ["https://company.atlassian.net", "https://test.atlassian.net", "https://my-company.atlassian.net"]

    for url in valid_urls:
        config = AtlassianConfig(url=url)
        assert config.validate_url() is True


def test_url_validation_invalid_urls():
    """Test that invalid URLs fail validation."""
    from mcp_server_atlassian.config import AtlassianConfig

    invalid_urls = [
        "http://company.atlassian.net",  # Not HTTPS
        "not-a-url",  # Invalid format
        "",  # Empty
    ]

    for url in invalid_urls:
        config = AtlassianConfig(url=url)
        assert config.validate_url() is False


def test_url_validation_accepts_custom_domains():
    """Test that custom domains are accepted for on-premise installations."""
    from mcp_server_atlassian.config import AtlassianConfig

    valid_custom_urls = [
        "https://jira.company.com",
        "https://atlassian.internal.corp",
        "https://tickets.example.org",
    ]

    for url in valid_custom_urls:
        config = AtlassianConfig(url=url)
        assert config.validate_url() is True


def test_cloud_detection():
    """Test that cloud instances are detected correctly."""
    from mcp_server_atlassian.config import AtlassianConfig

    # Cloud instances
    cloud_config = AtlassianConfig(url="https://company.atlassian.net")
    assert cloud_config.is_cloud is True

    # Server instances (hypothetical)
    server_config = AtlassianConfig(url="https://jira.company.com")
    assert server_config.is_cloud is False


@pytest.mark.asyncio
async def test_connectivity_test_reachable():
    """Test connectivity to reachable URL."""
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value.status_code = 200
        result = await config.test_connectivity()
        assert result is True


@pytest.mark.asyncio
async def test_connectivity_test_unreachable():
    """Test connectivity to unreachable URL."""
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://nonexistent.atlassian.net")

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = Exception("Connection failed")
        result = await config.test_connectivity()
        assert result is False


@pytest.mark.asyncio
async def test_atlassian_api_detection():
    """Test detection of valid Atlassian instance via API."""
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")

    with patch("httpx.AsyncClient.get") as mock_get:
        # Mock successful serverInfo response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "baseUrl": "https://test.atlassian.net",
            "version": "1001.0.0-SNAPSHOT",
            "deploymentType": "Cloud",
        }
        mock_get.return_value = mock_response

        result = await config.test_atlassian_api()
        assert result is True


@pytest.mark.asyncio
async def test_atlassian_api_detection_invalid():
    """Test detection fails for non-Atlassian sites."""
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://google.com")

    with patch("httpx.AsyncClient.get") as mock_get:
        # Mock 404 response (API endpoint doesn't exist)
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = await config.test_atlassian_api()
        assert result is False


def test_missing_configuration_detection():
    """Test detection of missing configuration."""
    from mcp_server_atlassian.config import AtlassianConfig

    # Test with empty URL
    config = AtlassianConfig(url="")
    assert config.is_configured() is False

    # Test with valid URL
    config = AtlassianConfig(url="https://test.atlassian.net")
    assert config.is_configured() is True


def test_configuration_guidance_message():
    """Test that helpful guidance is provided for missing configuration."""
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="")
    guidance = config.get_setup_guidance()

    assert "ATLASSIAN_URL" in guidance
    assert "environment variable" in guidance
    assert "https://" in guidance


def test_http_timeout_configuration():
    """Test that HTTP timeout configuration is properly structured."""
    from mcp_server_atlassian.config import AtlassianConfig
    import httpx

    config = AtlassianConfig(url="https://test.atlassian.net", timeout=25)
    timeout_config = config.http_timeout

    assert isinstance(timeout_config, httpx.Timeout)
    assert timeout_config.connect == 10.0  # Connection timeout
    assert timeout_config.read == 25  # Read timeout matches config
    assert timeout_config.write == 10.0  # Write timeout
    assert timeout_config.pool == 5.0  # Pool timeout
