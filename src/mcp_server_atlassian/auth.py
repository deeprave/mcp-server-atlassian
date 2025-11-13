"""Authentication management for MCP Server Atlassian."""

import os
from typing import Optional
import keyring
from atlassian import Jira

from .config import AtlassianConfig
from .result import Result


class CredentialsRequiredException(Exception):
    """Raised when authentication is required but no valid token found."""

    def __init__(self, url: str):
        self.url = url
        self.user_instructions = {
            "message": "Tell the user: If you wish to authenticate with Atlassian, here's how:",
            "steps": [
                {
                    "step": 1,
                    "title": "Obtain an API Token",
                    "instructions": [
                        "Go to https://id.atlassian.com/manage-profile/security/api-tokens",
                        "Click 'Create API token'",
                        "Give it a label (e.g., 'MCP Server')",
                        "Copy the generated token",
                    ],
                },
                {
                    "step": 2,
                    "title": "Configure Authentication",
                    "options": [
                        {
                            "method": "Environment Variable (Manual)",
                            "instructions": [
                                f"Set ATLASSIAN_URL={url}",
                                "Set ATLASSIAN_API_TOKEN=your-token-here",
                                "Restart the MCP server",
                            ],
                        },
                        {
                            "method": "Interactive Setup (Secure Storage)",
                            "instructions": [
                                "Provide your API token when prompted",
                                "It will be stored securely in your system keychain",
                                "No need to restart - works immediately",
                            ],
                            "tool_call": "setup_atlassian_credentials(token='your-token')",
                        },
                    ],
                },
            ],
        }
        super().__init__(f"Authentication required for {url}")


class AtlassianAuthManager:
    """Manages token-based authentication for Atlassian services."""

    def __init__(self, config: AtlassianConfig):
        """Initialize authentication manager."""
        self.config = config

    async def store_token(self, token: str) -> None:
        """Store API token securely in keychain using URL as key."""
        keyring.set_password("mcp-server-atlassian", self.config.url, token)

    async def get_keychain_token(self) -> Optional[str]:
        """Retrieve API token from keychain using URL as key."""
        return keyring.get_password("mcp-server-atlassian", self.config.url)

    async def get_environment_token(self) -> Optional[str]:
        """Get API token from environment variables."""
        return os.getenv("ATLASSIAN_API_TOKEN")

    async def require_authentication(self) -> str:
        """Get valid API token or raise CredentialsRequiredException."""
        # Try keychain first
        token = await self.get_keychain_token()
        if token:
            return token

        # Try environment fallback
        env_token = await self.get_environment_token()
        if env_token:
            return env_token

        # No valid token found
        raise CredentialsRequiredException(self.config.url)

    async def create_jira_client(self, token: str) -> Jira:
        """Create authenticated Jira client with API token."""
        return Jira(url=self.config.url, token=token, cloud=self.config.is_cloud)

    async def create_authenticated_client(self, token: str) -> Jira:
        """Create authenticated Jira client."""
        return await self.create_jira_client(token=token)

    async def test_credentials(self, token: str) -> Result[bool]:
        """Test if API token is valid by making an API call."""
        try:
            client = await self.create_authenticated_client(token)
            client.myself()  # type: ignore[no-untyped-call]
            return Result.ok(True)
        except ValueError as e:
            # Invalid token format
            return Result.failure(f"Invalid token: {str(e)}", "credential_error", e)
        except ConnectionError as e:
            # Network connectivity issues
            return Result.failure(f"Network error: {str(e)}", "network_error", e)
        except PermissionError as e:
            # Authentication succeeded but insufficient permissions
            return Result.failure(f"Permission denied: {str(e)}", "permission_error", e)
        except Exception as e:
            # Other authentication or API errors
            error_msg = str(e)
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                return Result.failure("Invalid API token - authentication failed", "auth_error", e)
            elif "403" in error_msg or "forbidden" in error_msg.lower():
                return Result.failure("Access forbidden - check token permissions", "permission_error", e)
            elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                return Result.failure(f"Connection error: {error_msg}", "network_error", e)
            else:
                return Result.failure(f"Authentication test failed: {error_msg}", "unknown_error", e)

    async def setup_credentials(self, token: str) -> str:
        """Setup and validate API token, store in keychain."""
        if not token:
            raise ValueError("API token must be provided")

        # Test token
        result = await self.test_credentials(token)
        if result.is_failure():
            raise ValueError(f"Token validation failed: {result.error}")

        # Store in keychain
        await self.store_token(token)

        return f"API token validated and stored securely for {self.config.url}"
