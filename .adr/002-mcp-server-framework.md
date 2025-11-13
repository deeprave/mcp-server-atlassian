# ADR-002: MCP Server Framework

**Date:** 2025-11-11
**Status:** Decided
**Deciders:** Development Team

## Context

Need to choose an MCP (Model Context Protocol) server framework for implementing Atlassian API integration. The framework must support:

- Async operations for API calls
- Clean tool registration and management
- Good developer experience
- Active maintenance and community support

## Decision

Use FastMCP framework for implementing the MCP server.

## Rationale

**FastMCP Advantages:**
- **Async Support**: Native async/await support for API operations
- **FastAPI-style**: Familiar decorator patterns and development experience
- **Active Development**: Well-maintained with regular updates
- **Clean Architecture**: Clear separation of concerns and tool organization
- **Type Safety**: Good TypeScript/Python type support
- **Documentation**: Comprehensive documentation and examples

**Alternatives Considered:**
- Raw MCP protocol implementation: Too much boilerplate
- Other MCP frameworks: Less mature or lacking async support

## Implementation

- Use FastMCP's `@tool` decorator for tool registration
- Leverage async capabilities for Atlassian API calls
- Follow FastMCP patterns for error handling and responses
- Use FastMCP's built-in STDIO transport for agent communication

## Examples

```python
from fastmcp import FastMCP

app = FastMCP("Atlassian MCP Server")

@app.tool()
async def get_jira_issue(issue_key: str) -> dict:
    # Async API call implementation
    pass
```

## Consequences

**Positive:**
- Rapid development with familiar patterns
- Built-in async support for API operations
- Good error handling and validation
- Active community and maintenance

**Negative:**
- Framework dependency (vs raw protocol)
- Learning curve for FastMCP-specific patterns

## Status

Implemented and serving as the foundation for all MCP tool implementations.
