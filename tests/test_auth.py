"""Tests for authentication functionality."""

import pytest
from unittest.mock import patch, MagicMock


def test_auth_manager_can_be_created():
    """Test that authentication manager can be created."""
    from mcp_server_atlassian.auth import AtlassianAuthManager
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")
    auth_manager = AtlassianAuthManager(config)

    assert auth_manager is not None
    assert auth_manager.config == config


@pytest.mark.asyncio
async def test_keychain_token_storage():
    """Test storing and retrieving API token from keychain."""
    from mcp_server_atlassian.auth import AtlassianAuthManager
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")
    auth_manager = AtlassianAuthManager(config)

    test_token = "ATATT3xFfGF0test_token_123"

    # Mock keyring operations
    stored_data = None

    def mock_set_password(service, account, password):
        nonlocal stored_data
        stored_data = (service, account, password)

    def mock_get_password(service, account):
        if stored_data and stored_data[0] == service and stored_data[1] == account:
            return stored_data[2]
        return None

    with (
        patch("keyring.set_password", side_effect=mock_set_password),
        patch("keyring.get_password", side_effect=mock_get_password),
    ):
        # Store token
        await auth_manager.store_token(test_token)

        # Verify storage used URL as account key
        assert stored_data[0] == "mcp-server-atlassian"
        assert stored_data[1] == "https://test.atlassian.net"
        assert stored_data[2] == test_token

        # Retrieve token
        retrieved = await auth_manager.get_keychain_token()
        assert retrieved == test_token


@pytest.mark.asyncio
async def test_environment_token_fallback():
    """Test fallback to environment variables when keychain unavailable."""
    from mcp_server_atlassian.auth import AtlassianAuthManager
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")
    auth_manager = AtlassianAuthManager(config)

    test_token = "ATATT3xFfGF0env_token_456"

    with (
        patch("keyring.get_password", return_value=None),
        patch.dict("os.environ", {"ATLASSIAN_API_TOKEN": test_token}),
    ):
        # Should get token from environment
        env_token = await auth_manager.get_environment_token()
        assert env_token == test_token


@pytest.mark.asyncio
async def test_api_token_authentication():
    """Test creating authenticated client with API token."""
    from mcp_server_atlassian.auth import AtlassianAuthManager
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")
    auth_manager = AtlassianAuthManager(config)

    test_token = "ATATT3xFfGF0test_token"

    with patch("mcp_server_atlassian.auth.Jira") as mock_jira:
        mock_client = MagicMock()
        mock_jira.return_value = mock_client

        client = await auth_manager.create_authenticated_client(test_token)

        mock_jira.assert_called_once_with(url="https://test.atlassian.net", token=test_token, cloud=True)
        assert client == mock_client


@pytest.mark.asyncio
async def test_credential_validation_success():
    """Test successful credential validation."""
    from mcp_server_atlassian.auth import AtlassianAuthManager
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")
    auth_manager = AtlassianAuthManager(config)

    test_token = "ATATT3xFfGF0valid_token"

    with patch("mcp_server_atlassian.auth.Jira") as mock_jira:
        mock_client = MagicMock()
        mock_client.myself.return_value = {"accountId": "test123"}
        mock_jira.return_value = mock_client

        result = await auth_manager.test_credentials(test_token)
        assert result.is_ok()
        assert result.value is True


@pytest.mark.asyncio
async def test_credential_validation_failure():
    """Test credential validation failure."""
    from mcp_server_atlassian.auth import AtlassianAuthManager
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")
    auth_manager = AtlassianAuthManager(config)

    test_token = "ATATT3xFfGF0invalid_token"

    with patch("mcp_server_atlassian.auth.Jira") as mock_jira:
        mock_client = MagicMock()
        mock_client.myself.side_effect = Exception("401 Unauthorized")
        mock_jira.return_value = mock_client

        result = await auth_manager.test_credentials(test_token)
        assert result.is_failure()
        assert result.error_type == "auth_error"
        assert "authentication failed" in result.error


@pytest.mark.asyncio
async def test_require_authentication_success():
    """Test successful authentication requirement."""
    from mcp_server_atlassian.auth import AtlassianAuthManager
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")
    auth_manager = AtlassianAuthManager(config)

    test_token = "ATATT3xFfGF0valid_token"

    with patch.object(auth_manager, "get_keychain_token", return_value=test_token):
        result = await auth_manager.require_authentication()
        assert result == test_token


@pytest.mark.asyncio
async def test_require_authentication_failure():
    """Test authentication requirement failure raises exception."""
    from mcp_server_atlassian.auth import AtlassianAuthManager, CredentialsRequiredException
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")
    auth_manager = AtlassianAuthManager(config)

    with (
        patch.object(auth_manager, "get_keychain_token", return_value=None),
        patch.object(auth_manager, "get_environment_token", return_value=None),
    ):
        with pytest.raises(CredentialsRequiredException) as exc_info:
            await auth_manager.require_authentication()

        assert exc_info.value.url == "https://test.atlassian.net"
        assert "message" in exc_info.value.user_instructions
        assert "steps" in exc_info.value.user_instructions


@pytest.mark.asyncio
async def test_setup_credentials_success():
    """Test successful credential setup."""
    from mcp_server_atlassian.auth import AtlassianAuthManager
    from mcp_server_atlassian.config import AtlassianConfig
    from mcp_server_atlassian.result import Result

    config = AtlassianConfig(url="https://test.atlassian.net")
    auth_manager = AtlassianAuthManager(config)

    test_token = "ATATT3xFfGF0valid_token"

    with (
        patch.object(auth_manager, "test_credentials", return_value=Result.ok(True)),
        patch.object(auth_manager, "store_token") as mock_store,
    ):
        result = await auth_manager.setup_credentials(token=test_token)

        assert "API token validated and stored" in result
        mock_store.assert_called_once_with(test_token)


@pytest.mark.asyncio
async def test_setup_credentials_invalid():
    """Test setup with invalid credentials."""
    from mcp_server_atlassian.auth import AtlassianAuthManager
    from mcp_server_atlassian.config import AtlassianConfig
    from mcp_server_atlassian.result import Result

    config = AtlassianConfig(url="https://test.atlassian.net")
    auth_manager = AtlassianAuthManager(config)

    test_token = "ATATT3xFfGF0invalid_token"

    with patch.object(auth_manager, "test_credentials", return_value=Result.failure("Invalid token", "auth_error")):
        with pytest.raises(ValueError, match="Token validation failed"):
            await auth_manager.setup_credentials(token=test_token)


@pytest.mark.asyncio
async def test_setup_credentials_empty_token():
    """Test setup with empty token."""
    from mcp_server_atlassian.auth import AtlassianAuthManager
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")
    auth_manager = AtlassianAuthManager(config)

    with pytest.raises(ValueError, match="API token must be provided"):
        await auth_manager.setup_credentials(token="")


@pytest.mark.asyncio
async def test_keychain_token_none():
    """Test when keychain returns None."""
    from mcp_server_atlassian.auth import AtlassianAuthManager
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")
    auth_manager = AtlassianAuthManager(config)

    with patch("keyring.get_password", return_value=None):
        result = await auth_manager.get_keychain_token()
        assert result is None


@pytest.mark.asyncio
async def test_credential_validation_network_error():
    """Test credential validation with network error."""
    from mcp_server_atlassian.auth import AtlassianAuthManager
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")
    auth_manager = AtlassianAuthManager(config)

    test_token = "ATATT3xFfGF0valid_token"

    with patch("mcp_server_atlassian.auth.Jira") as mock_jira:
        mock_client = MagicMock()
        mock_client.myself.side_effect = ConnectionError("Connection timeout")
        mock_jira.return_value = mock_client

        result = await auth_manager.test_credentials(test_token)
        assert result.is_failure()
        assert result.error_type == "network_error"
        assert "Connection timeout" in result.error


@pytest.mark.asyncio
async def test_credential_validation_permission_error():
    """Test credential validation with permission error."""
    from mcp_server_atlassian.auth import AtlassianAuthManager
    from mcp_server_atlassian.config import AtlassianConfig

    config = AtlassianConfig(url="https://test.atlassian.net")
    auth_manager = AtlassianAuthManager(config)

    test_token = "ATATT3xFfGF0valid_token"

    with patch("mcp_server_atlassian.auth.Jira") as mock_jira:
        mock_client = MagicMock()
        mock_client.myself.side_effect = Exception("403 Forbidden")
        mock_jira.return_value = mock_client

        result = await auth_manager.test_credentials(test_token)
        assert result.is_failure()
        assert result.error_type == "permission_error"
        assert "Access forbidden" in result.error


@pytest.mark.asyncio
async def test_result_json_serialization_success():
    """Test Result JSON serialization for successful results."""
    from mcp_server_atlassian.result import Result

    result = Result.ok({"status": "authenticated"})
    json_data = result.to_json()

    assert json_data == {"success": True, "value": {"status": "authenticated"}}


@pytest.mark.asyncio
async def test_result_json_serialization_failure():
    """Test Result JSON serialization for failure results with exception."""
    from mcp_server_atlassian.result import Result

    original_exception = ValueError("Invalid token format")
    result = Result.failure("Token error", "credential_error", original_exception)
    json_data = result.to_json()

    expected = {
        "success": False,
        "error": "Token error",
        "error_type": "credential_error",
        "exception_type": "ValueError",
        "exception_message": "Invalid token format",
    }
    assert json_data == expected


@pytest.mark.asyncio
async def test_result_json_serialization_failure_no_exception():
    """Test Result JSON serialization for failure results without exception."""
    from mcp_server_atlassian.result import Result

    result = Result.failure("Generic error", "unknown_error")
    json_data = result.to_json()

    expected = {
        "success": False,
        "error": "Generic error",
        "error_type": "unknown_error",
    }
    assert json_data == expected
