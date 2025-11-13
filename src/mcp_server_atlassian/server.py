"""MCP Server implementation for Atlassian services."""

from typing import List, Optional, Any, Dict
from fastmcp import FastMCP

from .config import AtlassianConfig
from .auth import AtlassianAuthManager
from .result import Result


class AtlassianMCPServer:
    """MCP Server for Atlassian services."""

    def __init__(self) -> None:
        """Initialize the server."""
        self._running = False
        self.mcp_server = FastMCP("Atlassian MCP Server")
        self.config: Optional[AtlassianConfig] = None
        self.auth_manager: Optional[AtlassianAuthManager] = None
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Set up MCP tools."""

        @self.mcp_server.tool()
        async def health_check() -> Dict[str, Any]:
            """Check server health."""
            return Result.ok("Server is healthy").to_json()

        @self.mcp_server.tool()
        async def setup_atlassian_credentials(token: str) -> Dict[str, Any]:
            """Configure Atlassian API token for authentication.

            Args:
                token: API token for Atlassian authentication
            """
            try:
                # Use server's existing config - prevents URL injection
                auth_manager = await self._get_auth_manager()
                result = await auth_manager.setup_credentials(token=token)
                return Result.ok(result).to_json()

            except ValueError as e:
                return Result.failure(f"Setup failed: {str(e)}", "setup_error", e).to_json()
            except Exception as e:
                return Result.failure(f"Unexpected error during setup: {str(e)}", "unknown_error", e).to_json()

    async def _get_auth_manager(self) -> AtlassianAuthManager:
        """Get authenticated auth manager or raise helpful exception."""
        if not self.config:
            self.config = AtlassianConfig.from_environment()

        if not self.auth_manager:
            self.auth_manager = AtlassianAuthManager(self.config)

        return self.auth_manager

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

    async def get_tools(self) -> List[Any]:
        """Get list of registered tools."""
        return list((await self.mcp_server.get_tools()).values())
