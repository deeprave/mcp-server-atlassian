"""MCP Server implementation for Atlassian services."""
import asyncio
from typing import Optional, List
from fastmcp import FastMCP


class AtlassianMCPServer:
    """MCP Server for Atlassian services."""
    
    def __init__(self):
        """Initialize the server."""
        self._running = False
        self.mcp_server = FastMCP("Atlassian MCP Server")
        self._setup_tools()
    
    def _setup_tools(self):
        """Set up MCP tools."""
        # Add basic health check tool
        @self.mcp_server.tool()
        async def health_check() -> str:
            """Check server health."""
            return "Server is healthy"
    
    async def start(self) -> None:
        """Start the MCP server."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the MCP server."""
        self._running = False
    
    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running
    
    async def get_tools(self) -> List:
        """Get list of registered tools."""
        # Return tools from FastMCP server
        return await self.mcp_server.get_tools()
