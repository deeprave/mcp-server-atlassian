"""Test CLI integration and argument parsing."""

import sys
import pytest
from unittest.mock import patch
from typer.testing import CliRunner


def test_cli_app_help_command():
    """Test that CLI app --help works correctly."""
    from mcp_server_atlassian.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "MCP Server for Atlassian services" in result.output
    assert "--log-level" in result.output
    assert "--log-file" in result.output
    assert "--log-json" in result.output


def test_cli_app_version_command():
    """Test that CLI app --version works correctly."""
    from mcp_server_atlassian.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "MCP Server Atlassian" in result.output


def test_main_entry_point_with_help():
    """Test main entry point with --help argument."""
    from mcp_server_atlassian.main import main

    with patch.object(sys, "argv", ["mcp-server-atlassian", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_main_entry_point_with_version():
    """Test main entry point with --version argument."""
    from mcp_server_atlassian.main import main

    with patch.object(sys, "argv", ["mcp-server-atlassian", "--version"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_cli_logging_flags():
    """Test that logging flags are parsed correctly."""
    from mcp_server_atlassian.cli import app
    from unittest.mock import AsyncMock, patch

    runner = CliRunner()

    with patch("mcp_server_atlassian.cli.start_server", new_callable=AsyncMock) as mock_start:
        runner.invoke(app, ["--log-level", "DEBUG", "--log-file", "test.log", "--log-json"])

        # Should call start_server with correct parameters
        mock_start.assert_called_once_with("DEBUG", "test.log", True)


def test_cli_trace_log_level():
    """Test that TRACE log level is supported."""
    from mcp_server_atlassian.cli import app
    from unittest.mock import AsyncMock, patch

    runner = CliRunner()

    with patch("mcp_server_atlassian.cli.start_server", new_callable=AsyncMock) as mock_start:
        runner.invoke(app, ["--log-level", "TRACE"])

        # Should call start_server with TRACE level
        mock_start.assert_called_once_with("TRACE", "", False)
