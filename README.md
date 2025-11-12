# MCP Server Atlassian

A Model Context Protocol (MCP) server providing comprehensive access to Atlassian Jira and Confluence Cloud APIs.

## Overview

This MCP server mirrors the full capability of Atlassian's Jira and Confluence Cloud APIs, enabling AI agents to interact with your Atlassian services through a locally hosted MCP interface.

## Features

- **Full Jira API Access**: Complete interface to Jira Cloud REST API
- **Full Confluence API Access**: Complete interface to Confluence Cloud REST API
- **Local MCP Server**: Runs locally for secure API access
- **Comprehensive Coverage**: Mirrors all available API endpoints and functionality

## Installation

### Using uvx (Recommended)

```bash
uvx --from git+https://github.com/deeprave/mcp-server-atlassian mcp-server-atlassian
```

### Using uv with Cloned Sources

1. Clone the repository:
```bash
git clone https://github.com/deeprave/mcp-server-atlassian.git
cd mcp-server-atlassian
```

2. Install using uv:
```bash
uv pip install -e .
```

3. Run the server:
```bash
uv run mcp-server-atlassian
```

## Configuration

Configure your Atlassian credentials and instance details through environment variables or configuration files (detailed configuration instructions to be added).

## Requirements

- Python 3.13+
- Valid Atlassian Cloud account
- API tokens for Jira and Confluence access

## Development

This project uses modern Python development practices:

- **Testing**: pytest with coverage reporting
- **Linting**: ruff for code formatting and linting
- **Type Checking**: mypy for static type analysis
- **Build System**: hatchling

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contributing

Contributions are welcome! Please ensure all tests pass and code follows the project's linting and formatting standards.
