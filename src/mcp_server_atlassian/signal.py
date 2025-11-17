"""Signal handling context manager for graceful MCP server shutdown."""

import signal
import sys
from typing import Optional, Any

from .mcp_log import get_logger

logger = get_logger(__name__)


class SignalHandler:
    """Context manager for graceful signal handling without stack traces."""

    def __init__(self) -> None:
        """Initialize signal handler."""
        self._original_handlers: dict[int, Any] = {}

    def __enter__(self) -> "SignalHandler":
        """Install signal handlers."""
        self._original_handlers[signal.SIGINT] = signal.signal(signal.SIGINT, self._handle_sigint)
        self._original_handlers[signal.SIGPIPE] = signal.signal(signal.SIGPIPE, self._handle_sigpipe)
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """Restore signal handlers and handle exit codes."""
        # Restore original signal handlers
        for sig, handler in self._original_handlers.items():
            signal.signal(sig, handler)

        # Handle signal-based exceptions
        if isinstance(exc_val, KeyboardInterrupt):
            logger.warning("MCP server interrupted by SIGINT")
            sys.exit(130)
        elif isinstance(exc_val, BrokenPipeError):
            sys.exit(141)

        # Other exceptions will propagate normally

    def _handle_sigint(self, signum: int, frame: Any) -> None:
        """Handle SIGINT by raising KeyboardInterrupt."""
        raise KeyboardInterrupt()

    def _handle_sigpipe(self, signum: int, frame: Any) -> None:
        """Handle SIGPIPE by raising BrokenPipeError."""
        raise BrokenPipeError()
