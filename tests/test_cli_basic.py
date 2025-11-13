"""Test basic CLI functionality."""

import pytest
import typer
from unittest.mock import patch


def test_version_callback_shows_version():
    """Test version callback displays version and exits."""
    from mcp_server_atlassian.cli import version_callback
    from mcp_server_atlassian import __version__

    with patch("typer.echo") as mock_echo:
        with pytest.raises(typer.Exit):
            version_callback(True)

        mock_echo.assert_called_once_with(f"MCP Server Atlassian {__version__}")


def test_version_callback_no_action_when_false():
    """Test version callback does nothing when value is False."""
    from mcp_server_atlassian.cli import version_callback

    # Should not raise or call anything
    result = version_callback(False)
    assert result is None


def test_main_callback_function():
    """Test main callback function exists and is callable."""
    from mcp_server_atlassian.cli import main

    # Should not raise when called with default args
    result = main()
    assert result is None


def test_get_config_function():
    """Test get_config function returns AtlassianConfig."""
    from mcp_server_atlassian.cli import get_config
    from mcp_server_atlassian.config import AtlassianConfig

    with patch.object(AtlassianConfig, "from_environment") as mock_from_env:
        mock_config = AtlassianConfig(url="https://test.atlassian.net")
        mock_from_env.return_value = mock_config

        result = get_config()

        assert result == mock_config
        mock_from_env.assert_called_once()
