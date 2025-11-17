"""Error context for MCP error reporting."""

from typing import Dict, Any
from .result import Result


class ErrorContext:
    """Context for reporting errors via MCP without exiting."""

    def report_config_error(self, message: str) -> Dict[str, Any]:
        """Report configuration error via MCP error mechanism."""
        return Result.failure(error=f"Configuration Error: {message}", error_type="config_error").to_json()

    def report_runtime_error(self, message: str) -> Dict[str, Any]:
        """Report runtime error via MCP error mechanism."""
        return Result.failure(error=f"Runtime Error: {message}", error_type="runtime_error").to_json()
