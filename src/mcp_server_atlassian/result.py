"""Result pattern for rich error handling."""

from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Dict, Any

T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    """Kotlin-like Result pattern for rich error handling."""

    success: bool
    value: Optional[T] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    exception: Optional[Exception] = None

    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        """Create a successful result."""
        return cls(success=True, value=value)

    @classmethod
    def failure(cls, error: str, error_type: str = "unknown", exception: Optional[Exception] = None) -> "Result[T]":
        """Create a failure result with error information."""
        return cls(success=False, error=error, error_type=error_type, exception=exception)

    def is_ok(self) -> bool:
        """Check if result is successful."""
        return self.success

    def is_failure(self) -> bool:
        """Check if result is a failure."""
        return not self.success

    def unwrap(self) -> T:
        """Get the value, raising an exception if result is a failure."""
        if not self.success:
            raise ValueError(f"Cannot unwrap failed result: {self.error}")
        if self.value is None:
            raise ValueError("Cannot unwrap None value")
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Get the value or return default if result is a failure."""
        return self.value if self.success and self.value is not None else default

    def to_json(self) -> Dict[str, Any]:
        """Convert to MCP-compatible JSON format."""
        if self.success:
            return {"success": True, "value": self.value}
        else:
            result = {
                "success": False,
                "error": self.error,
                "error_type": self.error_type,
            }
            # Include exception details for debugging
            if self.exception:
                result["exception_type"] = type(self.exception).__name__
                result["exception_message"] = str(self.exception)
            return result
