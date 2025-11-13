"""Main entry point for MCP Server Atlassian."""

import asyncio
from .cli import get_config
from .server import AtlassianMCPServer


async def async_main() -> None:
    """Async main function for server operations."""
    # Get configuration from CLI
    config = get_config()

    # Create and configure server
    server = AtlassianMCPServer()
    server.config = config
    await server.start()

    # Run the FastMCP server in STDIO mode
    await server.mcp_server.run_async(transport="stdio")

    # Clean shutdown
    await server.stop()


def main() -> None:
    """Main CLI entry point."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
