# ADR-003: Result Pattern for Error Handling

**Status:** Accepted
**Date:** 2025-11-13
**Context:** Phase 2 Authentication Framework - Error Handling Improvement

## Problem

Current boolean return patterns (`True`/`False`) mask critical error information:
- Authentication failures provide no diagnostic information
- Network issues are indistinguishable from credential problems
- Debugging authentication problems is impossible
- Users receive no actionable feedback

## Decision

Implement a Kotlin-like Result pattern throughout the MCP server:

```python
@dataclass
class Result[T]:
    success: bool
    value: Optional[T] = None
    error: Optional[str] = None
    error_type: Optional[str] = None

    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        return cls(success=True, value=value)

    @classmethod
    def failure(cls, error: str, error_type: str = "unknown") -> "Result[T]":
        return cls(success=False, error=error, error_type=error_type)
```

## Benefits

- **Rich Error Information**: Specific error messages and types
- **Better Debugging**: Clear distinction between error types + original exception preservation
- **User Feedback**: Actionable error messages for users
- **Consistent Pattern**: Uniform error handling across the system
- **Type Safety**: Generic type support for different return types
- **MCP Compatibility**: Direct JSON serialization for MCP tool responses
- **Exception Preservation**: Original exceptions stored for detailed debugging

## Implementation

1. Create `Result` class in `src/mcp_server_atlassian/result.py`
2. Update authentication methods to return `Result` types
3. Update error handling to provide specific error information
4. Include original exceptions for debugging
5. Add MCP-compatible JSON serialization
6. Maintain backward compatibility where needed

## Examples

```python
# Before
async def test_credentials(self, credentials: Dict[str, Any]) -> bool:
    try:
        # ... authentication logic
        return True
    except Exception:
        return False  # No error information

# After
async def test_credentials(self, credentials: Dict[str, Any]) -> Result[bool]:
    try:
        # ... authentication logic
        return Result.ok(True)
    except ValueError as e:
        return Result.failure(f"Invalid credentials: {e}", "credential_error", e)
    except ConnectionError as e:
        return Result.failure(f"Network error: {e}", "network_error", e)
    except Exception as e:
        return Result.failure(f"Authentication failed: {e}", "auth_error", e)

# MCP Tool Usage
result = await auth_manager.test_credentials(credentials)
return result.to_json()  # Direct MCP-compatible response
```

## MCP Integration

The Result pattern integrates seamlessly with MCP tool responses:

```python
# Success response
{"success": true, "value": {"authenticated": true}}

# Failure response with debugging info
{
  "success": false,
  "error": "Invalid credentials - authentication failed",
  "error_type": "auth_error",
  "exception_type": "HTTPError",
  "exception_message": "401 Client Error: Unauthorized"
}
```

## Migration Strategy

- Phase 1: Implement Result class
- Phase 2: Update authentication methods
- Phase 3: Update other critical methods
- Phase 4: Update MCP tool responses to use rich error information
