# ADR-001: Tool Naming Convention

**Date:** 2025-11-11
**Status:** Decided
**Deciders:** Development Team

## Context

MCP servers provide tools to AI agents, but agents like Amazon Q don't automatically prefix tool names with the server name. This creates potential naming conflicts when multiple MCP servers are used together, and makes it unclear which server provides which tools.

## Decision

Use namespaced tool names with `atl_` prefix for all tools provided by this MCP server.

## Rationale

- **Disambiguation**: Clear identification of tools from this server vs others
- **Consistency**: All tools follow the same naming pattern
- **Flexibility**: Configurable prefix via `MCP_TOOL_PREFIX` environment variable
- **User Experience**: Agents can easily identify Atlassian-specific tools

## Implementation

- Custom tool decorator with configurable prefix
- Default prefix: `atl` (configurable via `MCP_TOOL_PREFIX` environment variable)
- Tool names follow pattern: `{prefix}_{service}.{action}`

## Examples

- `atl_jira.get_issue`
- `atl_confluence.get_page`
- `atl_jira.create_issue`

## Consequences

**Positive:**
- Clear tool identification and disambiguation
- Consistent naming across all tools
- Configurable for different deployment scenarios

**Negative:**
- Slightly longer tool names
- Additional configuration complexity

## Status

Implemented and active across all MCP tools.
