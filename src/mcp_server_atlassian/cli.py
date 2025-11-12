"""CLI interface for MCP Server Atlassian."""
import asyncio
import typer
from typing_extensions import Annotated

from . import __version__

app = typer.Typer(
    name="mcp-server-atlassian",
    help="MCP Server for Atlassian services (Jira, Confluence)",
    add_completion=False
)


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        typer.echo(f"MCP Server Atlassian {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[bool, typer.Option(
        "--version", 
        callback=version_callback,
        help="Show version and exit"
    )] = False,
):
    """MCP Server for Atlassian services."""
    pass


async def async_main():
    """Async main function for server operations."""
    from .server import AtlassianMCPServer
    
    # Create and start the MCP server
    server = AtlassianMCPServer()
    await server.start()
    
    # Run the FastMCP server in STDIO mode (async version)
    await server.mcp_server.run_async(transport="stdio")
    
    # Clean shutdown
    await server.stop()
    return "Server completed"


@app.command()
def serve():
    """Start the MCP server."""
    typer.echo("Starting MCP Server...")
    # Use asyncio.run to execute async main
    result = asyncio.run(async_main())
    typer.echo(f"Server result: {result}")


if __name__ == "__main__":
    app()
