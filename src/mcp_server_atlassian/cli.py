"""CLI interface for MCP Server Atlassian."""

import asyncio
import typer
from typing_extensions import Annotated

from . import __version__
from .config import AtlassianConfig

app = typer.Typer(
    name="mcp-server-atlassian",
    help="MCP Server for Atlassian services (Jira, Confluence)",
    add_completion=False,
    no_args_is_help=False,
)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        typer.echo(f"MCP Server Atlassian {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool, typer.Option("--version", callback=version_callback, help="Show version and exit")
    ] = False,
    log_level: Annotated[str, typer.Option("--log-level", help="Set logging level")] = "INFO",
    log_file: Annotated[str, typer.Option("--log-file", help="Log to file")] = "",
    log_json: Annotated[bool, typer.Option("--log-json", help="Use JSON log format")] = False,
) -> None:
    """MCP Server for Atlassian services."""
    if ctx.invoked_subcommand is None:
        # No subcommand, start the server
        asyncio.run(start_server(log_level, log_file, log_json))


async def start_server(log_level: str = "INFO", log_file: str = "", log_json: bool = False) -> None:
    """Start the MCP server."""
    from .server import AtlassianMCPServer
    from .config import AtlassianConfig
    from .mcp_log import get_logger, add_file_handler, configure
    import os

    # Validate log level
    valid_levels = {"TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if log_level.upper() not in valid_levels:
        raise ValueError(f"Invalid log level: {log_level}")

    # Convert log file to absolute path
    if log_file:
        log_file = os.path.abspath(log_file)

    # Get configuration safely BEFORE any logging setup
    config_result = AtlassianConfig.from_environment_safe()

    # Always create and start the MCP server, even if configuration fails
    # Configuration errors will be handled within the MCP protocol
    server = AtlassianMCPServer()

    if config_result.is_ok():
        server.config = config_result.unwrap()
    else:
        # Set a minimal config to allow server to start
        # The error will be reported when tools are called
        server.config = None
        # Store the configuration error for later reporting
        server._config_error = config_result.error or "Unknown configuration error"  # type: ignore

    await server.start()

    # IMMEDIATELY configure logging to override FastMCP's setup
    configure(level=log_level)
    if log_file:
        add_file_handler(log_file, log_level, log_json)

    # Now get logger and start logging
    logger = get_logger(__name__)
    logger.info("Starting MCP Server Atlassian")
    logger.debug(f"Configuration: log_level={log_level}, log_file={log_file or 'stdout'}, log_json={log_json}")

    if server.config:
        logger.debug(f"Configuration loaded: url={server.config.url}, tool_prefix={server.config.tool_prefix}")
    else:
        config_error = getattr(server, "_config_error", "Unknown error")
        logger.warning(f"Configuration failed: {config_error}")
        # Also send configuration error to MCP client via context logging
        # This will be visible in the client's logs
        try:
            # We need to get a context from the server to send client-visible logs
            # This will be sent once the server starts processing requests
            server._pending_config_warning = f"Atlassian MCP Server configuration warning: {config_error}. Please set the ATLASSIAN_URL environment variable."  # type: ignore
        except Exception:
            # If context logging fails, continue anyway
            pass

    logger.info("MCP server started successfully, entering STDIO mode")

    try:
        # Run the FastMCP server in STDIO mode
        await server.mcp_server.run_async(transport="stdio")
    except Exception as e:
        logger.error(f"Server runtime error: {str(e)}")
        raise
    finally:
        # Clean shutdown
        logger.info("Shutting down MCP server")
        await server.stop()


def get_config() -> AtlassianConfig:
    """Get configuration from environment variables."""
    return AtlassianConfig.from_environment()


if __name__ == "__main__":
    app()
