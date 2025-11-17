"""Main entry point for MCP Server Atlassian."""

from .cli import app


def main() -> None:
    """Main CLI entry point."""
    # Use Typer CLI app which handles --help, --version, and server startup
    app()


if __name__ == "__main__":
    main()
