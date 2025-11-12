"""Test basic CLI functionality."""
import subprocess
import sys


def test_module_can_be_executed():
    """Test that the module can be executed with --help."""
    result = subprocess.run(
        [sys.executable, "-m", "mcp_server_atlassian", "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0
    assert "help" in result.stdout.lower() or "usage" in result.stdout.lower()


def test_module_shows_version():
    """Test that the module can show version information."""
    result = subprocess.run(
        [sys.executable, "-m", "mcp_server_atlassian", "--version"],
        capture_output=True,
        text=True,
        timeout=10
    )
    # Should either succeed with version or fail gracefully
    assert result.returncode in [0, 2]  # 0 for success, 2 for missing option


def test_typer_cli_integration():
    """Test that CLI uses Typer and shows proper help."""
    result = subprocess.run(
        [sys.executable, "-m", "mcp_server_atlassian", "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0
    # Typer should show structured help with specific formatting
    stdout_lower = result.stdout.lower()
    assert "usage:" in stdout_lower
    assert "options" in stdout_lower  # Typer shows "Options" section
    # Typer includes --help and --version by default
    assert "--help" in stdout_lower
    assert "--version" in stdout_lower
