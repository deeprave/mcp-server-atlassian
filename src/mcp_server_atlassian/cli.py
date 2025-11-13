"""CLI interface for MCP Server Atlassian."""

import typer
from typing_extensions import Annotated

from . import __version__
from .config import AtlassianConfig

app = typer.Typer(
    name="mcp-server-atlassian", help="MCP Server for Atlassian services (Jira, Confluence)", add_completion=False
)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        typer.echo(f"MCP Server Atlassian {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool, typer.Option("--version", callback=version_callback, help="Show version and exit")
    ] = False,
) -> None:
    """MCP Server for Atlassian services."""


def get_config() -> AtlassianConfig:
    """Get configuration from environment variables."""
    return AtlassianConfig.from_environment()


if __name__ == "__main__":
    app()
