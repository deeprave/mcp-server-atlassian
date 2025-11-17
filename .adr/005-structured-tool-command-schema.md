# ADR-005: Structured Tool Command Schema

**Date:** 2025-11-17
**Status:** Decided
**Deciders:** Development Team

## Context

As we expand beyond basic tools (health check, authentication) to comprehensive Atlassian API functionality, we need a consistent, structured approach to tool parameters. Current tools use ad-hoc parameter patterns that don't scale:

- No consistent way to specify target product (Jira vs Confluence vs cross-product)
- No standard approach for field selection in responses
- No unified parameter structure for complex operations
- AI agents have no clear schema expectations for tool usage

## Decision

Implement a standardized 5-parameter structure for all Atlassian MCP tools:

```python
async def atl_tool_name(
    product: Literal["atlassian", "jira", "confluence"] = "atlassian",
    subject: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    response_fields: Optional[List[str]] = None,
    ctx: Context
) -> Dict[str, Any]:
```

## Rationale

**Consistency**: All tools follow the same parameter pattern, making them predictable for AI agents.

**Product Targeting**: Explicit `product` parameter clarifies which Atlassian product the operation targets.

**Flexibility**: `subject` and `parameters` provide tool-specific customization without breaking the schema.

**Field Selection**: `response_fields` allows AI agents to request only needed data, improving performance.

**Context Integration**: All tools receive MCP `Context` for logging, progress reporting, and resource access.

**FastMCP Compatibility**: Uses flat parameter structure that FastMCP can automatically convert to JSON Schema.

## Implementation Details

### Parameter Definitions

- **`product`**: Target Atlassian product with enum validation
  - `"atlassian"`: Cross-product or instance-level operations
  - `"jira"`: Jira-specific operations  
  - `"confluence"`: Confluence-specific operations

- **`subject`**: Primary target entity (username, project key, search query, etc.)
  - Tool-specific meaning documented in tool description
  - Optional with sensible defaults (e.g., current user)

- **`parameters`**: Additional tool-specific options
  - Flexible dictionary for complex tool requirements
  - Optional with empty dict default

- **`response_fields`**: Requested response fields
  - Array of field names to include in response
  - Optional - returns all fields if not specified
  - Improves performance by reducing payload size

- **`ctx`**: MCP Context (automatically injected by FastMCP)
  - Provides logging, progress reporting, resource access
  - Not visible in tool schema - handled by framework

### Tool Naming and Command Derivation

- Tool names follow existing ADR-001 convention: `atl_{command}`
- Command is derived from tool name (remove redundancy)
- Example: `atl_user_info` → command is implicitly "user_info"

### Response Format

Continue using Result pattern from ADR-003:

```python
return Result.ok(response_data).to_json()
return Result.failure("Error message", "error_type").to_json()
```

### Schema Advertisement

FastMCP automatically generates JSON Schema from Python type hints:

```json
{
  "type": "object",
  "properties": {
    "product": {
      "type": "string", 
      "enum": ["atlassian", "jira", "confluence"],
      "default": "atlassian"
    },
    "subject": {"type": "string"},
    "parameters": {"type": "object"},
    "response_fields": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
```

## Examples

### User Information Tool
```python
@mcp_tool("user_info")
async def atl_user_info(
    product: Literal["atlassian", "jira", "confluence"] = "atlassian",
    subject: Optional[str] = None,  # username
    parameters: Optional[Dict[str, Any]] = None,
    response_fields: Optional[List[str]] = None,  # ["id", "name", "email"]
    ctx: Context
) -> Dict[str, Any]:
    """Get information about an Atlassian user.
    
    Args:
        product: Target product (always "atlassian" for user info)
        subject: Username (optional, defaults to current user)
        parameters: Additional options (unused for this tool)
        response_fields: Specific fields to return ["id", "name", "email", "avatar"]
        ctx: MCP context for logging and operations
    
    Returns:
        Result JSON with user information
    """
```

### Search Tool
```python
@mcp_tool("search_users")
async def atl_search_users(
    product: Literal["atlassian", "jira", "confluence"] = "atlassian",
    subject: Optional[str] = None,  # search query
    parameters: Optional[Dict[str, Any]] = None,  # {"limit": 10, "active_only": True}
    response_fields: Optional[List[str]] = None,  # ["id", "name", "email"]
    ctx: Context
) -> Dict[str, Any]:
    """Search for users across Atlassian products."""
```

## Migration Strategy

1. **Phase 1**: Update existing tools (`atl_health_check`, `atl_setup_atlassian_credentials`)
2. **Phase 2**: Implement new core tools with structured schema
3. **Phase 3**: Expand to product-specific tools (Jira, Confluence)

## Benefits

**For AI Agents:**
- Predictable tool interface across all Atlassian operations
- Clear schema documentation via FastMCP's automatic generation
- Field selection capability for optimized responses

**For Developers:**
- Consistent parameter validation and error handling
- Unified logging and context access
- Scalable pattern for new tool development

**For Users:**
- Better performance through field selection
- Consistent error messages and debugging information
- Cross-product operation clarity

## Consequences

**Positive:**
- Unified, predictable tool interface
- Better AI agent integration
- Scalable architecture for complex operations
- Automatic JSON Schema generation

**Negative:**
- Breaking changes to existing tools (acceptable - early development)
- Slightly more verbose tool signatures
- Learning curve for new parameter structure

## Compatibility

- **FastMCP**: Full compatibility with automatic schema generation
- **MCP Protocol**: Supports all parameter types (strings, arrays, objects)
- **Result Pattern**: Continues using ADR-003 error handling
- **Tool Naming**: Follows ADR-001 naming conventions

## Status

Approved for implementation across all Atlassian MCP tools.
