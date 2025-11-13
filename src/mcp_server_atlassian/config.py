"""Configuration management for MCP Server Atlassian."""

import os
from dataclasses import dataclass, field
from typing import List
from urllib.parse import urlparse
import httpx


@dataclass
class AtlassianConfig:
    """Configuration for Atlassian API integration."""

    url: str
    timeout: int = 30  # Read timeout in seconds
    verify_ssl: bool = True
    backoff_and_retry: bool = True
    max_backoff_seconds: int = 1800
    max_backoff_retries: int = 1000
    retry_status_codes: List[int] = field(default_factory=lambda: [413, 429, 503])

    @property
    def http_timeout(self) -> httpx.Timeout:
        """Get httpx.Timeout configuration for robust connection handling.

        Uses the configured timeout for read operations, with fixed values
        for connection establishment, write operations, and connection pool.
        """
        return httpx.Timeout(
            connect=10.0,  # Connection establishment timeout (fixed)
            read=self.timeout,  # Read timeout (configurable)
            write=10.0,  # Write timeout (fixed)
            pool=5.0,  # Pool timeout (fixed)
        )

    def _create_http_client(self) -> httpx.AsyncClient:
        """Create configured HTTP client."""
        return httpx.AsyncClient(timeout=self.http_timeout, verify=self.verify_ssl)

    cloud: bool = True
    tool_prefix: str = "atl"

    @classmethod
    def from_environment(cls) -> "AtlassianConfig":
        """Load configuration from environment variables."""
        url = os.getenv("ATLASSIAN_URL")
        if not url:
            raise ValueError("ATLASSIAN_URL environment variable is required")

        tool_prefix = os.getenv("MCP_TOOL_PREFIX", "atl")

        return cls(url=url, tool_prefix=tool_prefix)

    def validate_url(self) -> bool:
        """Validate URL format."""
        if not self.url:
            return False

        try:
            parsed = urlparse(self.url)
            # Must be HTTPS
            if parsed.scheme != "https":
                return False
            # Must have a hostname
            if not parsed.hostname:
                return False
            return True
        except Exception:
            return False

    @property
    def is_cloud(self) -> bool:
        """Detect if this is an Atlassian Cloud instance."""
        if not self.url:
            return False

        try:
            parsed = urlparse(self.url)
            if parsed.hostname and "atlassian.net" in parsed.hostname:
                return True
            return False
        except Exception:
            return False

    async def test_connectivity(self) -> bool:
        """Test connectivity to the Atlassian instance."""
        if not self.url:
            return False

        try:
            async with self._create_http_client() as client:
                response = await client.get(self.url)
                return response.status_code < 500
        except Exception:
            return False

    async def test_atlassian_api(self) -> bool:
        """Test if this is a valid Atlassian instance by checking the API."""
        if not self.url:
            return False

        try:
            # Try to access the serverInfo endpoint
            api_url = f"{self.url.rstrip('/')}/rest/api/3/serverInfo"
            async with self._create_http_client() as client:
                response = await client.get(api_url)
                return response.status_code == 200
        except Exception:
            return False

    def is_configured(self) -> bool:
        """Check if configuration is complete."""
        return bool(self.url and self.url.strip())

    def get_setup_guidance(self) -> str:
        """Get guidance message for setting up configuration."""
        return (
            "Please set the ATLASSIAN_URL environment variable to your Atlassian instance URL.\n"
            "Example: export ATLASSIAN_URL=https://your-company.atlassian.net\n"
            "You can also set MCP_TOOL_PREFIX to customize the tool prefix (default: atl)."
        )
