"""Main entry point for MCP Server Atlassian."""

from .cli import app
from .mcp_log import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Main CLI entry point."""
    logger.debug("Starting MCP Server Atlassian CLI")
    # Use Typer CLI app which handles --help, --version, and server startup
    app()


if __name__ == "__main__":
    main()
