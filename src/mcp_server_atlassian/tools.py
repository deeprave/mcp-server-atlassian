"""MCP Tools registration and management."""

import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable, TypeVar

from .config import AtlassianConfig
from .auth import AtlassianAuthManager
from .result import Result


# Global registration state
_tools_registered = False
_registration_lock = asyncio.Lock()

# Type for decorated functions
F = TypeVar("F", bound=Callable[..., Awaitable[Dict[str, Any]]])


def mcp_tool(name: Optional[str] = None) -> Callable[[F], F]:
    """Decorator for MCP tools with automatic prefixing.

    Args:
        name: Optional custom name for the tool (will still be prefixed)
    """

    def decorator(func: F) -> F:
        # Store original function info for registration
        func._mcp_tool_name = name or func.__name__  # type: ignore
        func._mcp_tool_func = func  # type: ignore
        return func

    return decorator


async def register_tools(mcp_server: Any, config: AtlassianConfig) -> None:
    """Register all MCP tools with the server.

    Args:
        mcp_server: FastMCP server instance
        config: Atlassian configuration with tool_prefix
    """
    global _tools_registered

    async with _registration_lock:
        if _tools_registered:
            return

        # Register all tools with prefix
        await _register_health_tools(mcp_server, config)
        await _register_auth_tools(mcp_server, config)

        _tools_registered = True


async def _register_health_tools(mcp_server: Any, config: AtlassianConfig) -> None:
    """Register health-related tools."""
    from .mcp_log import get_logger

    try:

        @mcp_tool("health_check")
        async def health_check() -> Dict[str, Any]:
            """Check server health including configuration and connectivity."""
            from datetime import datetime

            try:
                health_status = {
                    "server": "running",
                    "configuration": "unknown",
                    "connectivity": "unknown",
                    "timestamp": datetime.utcnow().isoformat(),
                }

                # Check configuration
                atlassian_server = getattr(mcp_server, "_atlassian_server", None)
                if atlassian_server and atlassian_server.config:
                    health_status["configuration"] = "valid"

                    # Test connectivity if config is valid
                    try:
                        await atlassian_server.config.test_connectivity()
                        health_status["connectivity"] = "ok"
                    except Exception:
                        health_status["connectivity"] = "failed"
                else:
                    health_status["configuration"] = "missing"

                return Result.ok(health_status).to_json()

            except Exception as e:
                return Result.failure(f"Health check failed: {str(e)}", "health_check_error", e).to_json()

        # Register with prefix
        tool_name = f"{config.tool_prefix}_{health_check._mcp_tool_name}"  # type: ignore
        mcp_server.tool(name=tool_name)(health_check._mcp_tool_func)  # type: ignore
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Failed to register health tools: {e}")
        raise


async def _register_auth_tools(mcp_server: Any, config: AtlassianConfig) -> None:
    """Register authentication-related tools."""
    from .mcp_log import get_logger

    try:

        @mcp_tool("setup_atlassian_credentials")
        async def setup_atlassian_credentials(token: str) -> Dict[str, Any]:
            """Configure Atlassian API token for authentication.

            Args:
                token: API token for Atlassian authentication
            """
            try:
                # Send any pending configuration warnings to the client first
                await _send_pending_warnings(mcp_server)

                # Check if we have a valid configuration
                atlassian_server = getattr(mcp_server, "_atlassian_server", None)
                if atlassian_server and not atlassian_server.config:
                    config_error = getattr(atlassian_server, "_config_error", "Configuration not available")
                    return Result.failure(
                        f"Server configuration error: {config_error}. "
                        "Please set the ATLASSIAN_URL environment variable to your Atlassian instance URL "
                        "(e.g., https://your-company.atlassian.net)",
                        "config_error",
                    ).to_json()

                # Get auth manager - this will be passed from server context
                auth_manager = AtlassianAuthManager(config)
                result = await auth_manager.setup_credentials(token=token)
                return Result.ok(result).to_json()

            except ValueError as e:
                return Result.failure(f"Setup failed: {str(e)}", "setup_error", e).to_json()
            except Exception as e:
                return Result.failure(f"Unexpected error during setup: {str(e)}", "unknown_error", e).to_json()

        # Register with prefix
        tool_name = f"{config.tool_prefix}_{setup_atlassian_credentials._mcp_tool_name}"  # type: ignore
        mcp_server.tool(name=tool_name)(setup_atlassian_credentials._mcp_tool_func)  # type: ignore
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Failed to register auth tools: {e}")
        raise


async def _send_pending_warnings(mcp_server: Any) -> None:
    """Send any pending configuration warnings to the MCP client."""
    try:
        atlassian_server = getattr(mcp_server, "_atlassian_server", None)
        if atlassian_server and hasattr(atlassian_server, "_pending_config_warning"):
            # Clear the warning so it's only sent once
            delattr(atlassian_server, "_pending_config_warning")

            # Try to get current context and send warning
            # Note: This is a best-effort attempt - if no context is available, we skip
            try:
                # FastMCP context access is not available in this context
                # The warning will be shown in the tool response instead
                pass
            except Exception:
                # If context logging fails, continue silently
                pass
    except Exception:
        # If anything fails, continue silently - this is just a nice-to-have
        pass
