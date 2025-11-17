"""MCP Server implementation for Atlassian services."""

from typing import List, Optional, Any
from fastmcp import FastMCP

from .config import AtlassianConfig
from .auth import AtlassianAuthManager
from .tools import register_tools


class AtlassianMCPServer:
    """MCP Server for Atlassian services."""

    def __init__(self) -> None:
        """Initialize the server."""
        self._running = False
        self.mcp_server = FastMCP("Atlassian MCP Server")
        self.config: Optional[AtlassianConfig] = None
        self.auth_manager: Optional[AtlassianAuthManager] = None

    async def start(self) -> None:
        """Start the MCP server."""
        # Register tools with configuration (or default config if None)
        if self.config:
            await register_tools(self.mcp_server, self.config)
        else:
            # Use default config for tool registration when config is missing
            from .config import AtlassianConfig

            default_config = AtlassianConfig(url="https://example.atlassian.net")
            await register_tools(self.mcp_server, default_config)

        # Store reference to this server instance for error checking
        self.mcp_server._atlassian_server = self  # type: ignore

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

    async def _get_auth_manager(self) -> AtlassianAuthManager:
        """Get authenticated auth manager or raise helpful exception."""
        if not self.config:
            config_result = AtlassianConfig.from_environment_safe()
            if config_result.is_failure():
                raise ValueError(f"Configuration error: {config_result.error}")
            self.config = config_result.unwrap()

        if not self.auth_manager:
            self.auth_manager = AtlassianAuthManager(self.config)

        return self.auth_manager
