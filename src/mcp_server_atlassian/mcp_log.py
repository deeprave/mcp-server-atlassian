"""Reusable MCP logging module with FastMCP integration."""

import logging
from dataclasses import dataclass
from typing import Any, Optional

try:
    from fastmcp.utilities.logging import get_logger as fastmcp_get_logger
    from fastmcp.utilities.logging import configure_logging

    _FASTMCP_AVAILABLE = True
except ImportError:
    # Fallback if FastMCP not available
    fastmcp_get_logger = logging.getLogger

    def configure_logging(*args: Any, **kwargs: Any) -> None:  # type: ignore
        """Fallback configure_logging function."""
        pass

    _FASTMCP_AVAILABLE = False


# Custom TRACE level (below DEBUG=10)
TRACE_LEVEL = 5

# Track if TRACE level has been initialized
_trace_initialized = False


@dataclass
class MCPLogConfig:
    """Configuration for MCP logging."""

    level: str = "INFO"
    file_path: Optional[str] = None
    json_format: bool = False


def _sanitize_log_message(message: Any) -> Any:
    """Sanitize log message to prevent log injection."""
    if isinstance(message, str):
        return message.replace("\n", "\\n").replace("\r", "\\r")
    return message


def _initialize_trace_level() -> None:
    """Initialize TRACE level in logging module."""
    global _trace_initialized
    if _trace_initialized:
        return

    logging.addLevelName(TRACE_LEVEL, "TRACE")

    def trace(self: logging.Logger, message: Any, *args: Any, **kwargs: Any) -> None:
        """Log message at TRACE level."""
        if self.isEnabledFor(TRACE_LEVEL):
            sanitized_message = _sanitize_log_message(message)
            self._log(TRACE_LEVEL, sanitized_message, args, **kwargs)

    logging.Logger.trace = trace  # type: ignore
    _trace_initialized = True


def _add_trace_method(logger: logging.Logger) -> None:
    """Add trace method to logger instance if not present."""
    if not hasattr(logger, "trace"):

        def trace(message: Any, *args: Any, **kwargs: Any) -> None:
            """Log message at TRACE level."""
            if logger.isEnabledFor(TRACE_LEVEL):
                sanitized_message = _sanitize_log_message(message)
                logger._log(TRACE_LEVEL, sanitized_message, args, **kwargs)

        logger.trace = trace  # type: ignore


def _get_log_level(level_name: str) -> int:
    """Convert level name to logging level constant."""
    level_upper = level_name.upper()
    if level_upper == "TRACE":
        return TRACE_LEVEL
    return getattr(logging, level_upper, logging.INFO)


def configure(level: str = "INFO", file_path: Optional[str] = None, json_format: bool = False) -> None:
    """Configure MCP logging system."""
    _initialize_trace_level()
    _add_trace_to_context()  # Add trace method to FastMCP Context

    # Configure file logging first if requested - this ensures our logs get captured
    if file_path:
        add_file_handler(file_path, level, json_format)

    if _FASTMCP_AVAILABLE and configure_logging is not None:
        # Use FastMCP's configure_logging
        configure_logging(level=level.upper())  # type: ignore
    else:
        # Fallback configuration
        log_level = _get_log_level(level)
        if not file_path:  # Only use basicConfig if no file handler
            logging.basicConfig(level=log_level)


def add_file_handler(
    file_path: str, level: str = "INFO", json_format: bool = False, date_format: str = "%Y-%m-%d %H:%M:%S"
) -> None:
    """Add file handler to our application loggers only, not FastMCP loggers."""
    import logging

    # Create file handler
    file_handler = logging.FileHandler(file_path, mode="a")
    file_handler.setLevel(_get_log_level(level))

    # Create formatter with redaction support
    if json_format:
        formatter = _create_structured_json_formatter(date_format)
    else:
        formatter = _create_redacted_formatter(date_format)

    file_handler.setFormatter(formatter)

    # Strategy: Add handler to both our direct loggers and FastMCP-prefixed versions
    # This prevents duplication while ensuring our logs reach the file

    # Our application logger patterns (both direct and FastMCP-prefixed)
    app_logger_patterns = ["mcp_server_atlassian", "fastmcp.mcp_server_atlassian"]

    for pattern in app_logger_patterns:
        app_logger = logging.getLogger(pattern)
        app_logger.addHandler(file_handler)
        app_logger.setLevel(_get_log_level(level))
        app_logger.propagate = False  # Don't propagate to avoid duplication

        # Also configure any existing child loggers
        for name in list(logging.Logger.manager.loggerDict.keys()):
            if name.startswith(f"{pattern}."):
                child_logger = logging.getLogger(name)
                child_logger.setLevel(_get_log_level(level))
                # Child loggers will propagate to their parent which has our handler


def _create_redacted_formatter(date_format: str) -> logging.Formatter:
    """Create standard log formatter with optional PII redaction."""

    class RedactedFormatter(logging.Formatter):
        def __init__(self) -> None:
            super().__init__(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt=date_format)
            # Try to import optional redaction filter
            self._redaction_func = None
            try:
                from .mcp_log_filter import get_redaction_function

                self._redaction_func = get_redaction_function()
            except ImportError:
                # Redaction filter not available, skip filtering
                pass

        def format(self, record: logging.LogRecord) -> str:
            # Format the message normally first
            formatted = super().format(record)

            # Apply redaction if available
            if self._redaction_func:
                formatted = self._redaction_func(formatted)

            return formatted

    return RedactedFormatter()


def _create_structured_json_formatter(date_format: str) -> logging.Formatter:
    """Create structured JSON formatter with optional redaction."""

    class StructuredJSONFormatter(logging.Formatter):
        def __init__(self) -> None:
            super().__init__()
            # Try to import optional redaction filter
            self._redaction_func = None
            try:
                from .mcp_log_filter import get_redaction_function

                self._redaction_func = get_redaction_function()
            except ImportError:
                # Redaction filter not available, skip filtering
                pass

        def format(self, record: logging.LogRecord) -> str:
            # For now, use basic JSON until structlog is properly integrated
            import json
            from datetime import datetime

            message = record.getMessage()
            if self._redaction_func:
                message = self._redaction_func(message)

            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).strftime(date_format),
                "name": record.name,
                "level": record.levelname,
                "message": message,
                "module": record.module,
                "funcName": record.funcName,
                "lineno": record.lineno,
            }

            if record.exc_info:
                log_entry["exception"] = self.formatException(record.exc_info)

            return json.dumps(log_entry)

    return StructuredJSONFormatter()


def remove_file_handler(file_path: str) -> None:
    """Remove file handler from logging system."""
    import logging

    root_logger = logging.getLogger()
    handlers_to_remove = []

    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler) and handler.baseFilename == file_path:
            handlers_to_remove.append(handler)

    for handler in handlers_to_remove:
        root_logger.removeHandler(handler)
        handler.close()


def get_logger(name: str) -> logging.Logger:
    """Get logger instance with TRACE level support via FastMCP."""
    _initialize_trace_level()

    # Get logger from FastMCP (or fallback to standard logging)
    logger = fastmcp_get_logger(name)

    # Ensure trace method is available on this logger instance
    _add_trace_method(logger)

    return logger


# Initialize TRACE level on module import
_initialize_trace_level()


def _add_trace_to_context() -> None:
    """Add trace method to FastMCP Context class if available."""
    try:
        from fastmcp.server.context import Context

        if not hasattr(Context, "trace"):

            async def trace(
                self: Any,
                message: str,
                logger_name: str | None = None,
                extra: dict[str, Any] | None = None,
            ) -> None:
                """Send a TRACE-level message to the connected MCP Client.

                Since MCP protocol doesn't support 'trace' level, this maps to 'debug'.
                Messages sent to Clients are also logged to the fastmcp.server.context.to_client logger.
                """
                sanitized_message = _sanitize_log_message(message)
                await self.log(
                    level="debug",  # Map TRACE to DEBUG since MCP doesn't have TRACE
                    message=f"[TRACE] {sanitized_message}",  # Prefix to distinguish from regular debug
                    logger_name=logger_name,
                    extra=extra,
                )

            Context.trace = trace  # type: ignore

    except ImportError:
        # FastMCP not available, skip context patching
        pass
