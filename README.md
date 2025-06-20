# Commvault MCP Server

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
[![License](https://img.shields.io/badge/License-Apache_2.0-red.svg)](https://opensource.org/licenses/Apache-2.0)


A [Model Context Protocol (MCP)](https://modelcontextprotocol.org/) server for interacting with **Commvault** software. This server provides a standardized interface for AI agents to access job details, security posture and SLA status of the commcell.


## Features

- Fetch job history (Active / All / Last 24 hours)
- Retrieve Security Posture and Score
- Retrieve Service Level Agreement (SLA) Status
- More coming soon...


## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd commvault-mcp-server
```

### 2. Run the Setup Script

```bash
uv run setup.py
```

### 2. Run the MCP Server

```bash
uv run src/server.py
```

## Prerequisites

Before running the Commvault MCP Server, ensure the following requirements are met:

### 1. Python Environment

* Python 3.11 or higher
* [`uv`](https://github.com/astral-sh/uv) package manager (used for dependency management and running the server)

### 2. Authentication & Security Configuration

The following values will be collected during the setup process:

* **Commvault Access Credentials:**
  You need a valid `access_token` and `refresh_token` to authenticate with the Commvault API.
  Learn how to generate these tokens here: [Creating an Access Token – Commvault Docs](https://documentation.commvault.com/11.38/expert/creating_access_token.html)
  
* **Secret Key:**
  This secret must be included by the **MCP Client** in the `Authorization` header of all tool requests.
  It acts as a security layer for tool access in remote server. You can set your own. 


## Configuring Clients

<details>
<summary>Remote MCP Server (Streamable HTTP / SSE)</summary>

```json
{
  "mcpServers": {
    "Commvault": {
      "command": "npx",
      "args": ["mcp-remote", "HOST:PORT/mcp", "--header", "Authorization: <secret stored in server keyring>"]
    }
  }
}

```
</details>

<details>
<summary>Remote MCP Server (Client on Windows)</summary>

```json
{
  "mcpServers": {
    "Commvault": {
      "command": "cmd",
      "args": ["/c", "npx", "mcp-remote", "HOST:PORT/mcp", "--header", "Authorization: <secret stored in server keyring>"]
    }
  }
}

```
</details>

<details>
<summary>Remote MCP Server (HTTP)</summary>

```json
{
  "mcpServers": {
    "Commvault": {
      "command": "npx",
      "args": ["mcp-remote", "HOST:PORT/mcp", "--header", "Authorization: <secret stored in server keyring>", "--allow-http"]
    }
  }
}

```
</details>

<details>
<summary>Local MCP Server (STDIO)</summary>

```json
{
  "mcpServers": {
    "Commvault": {
      "command": "C:\\YOUR\\PATH\\TO\\commvault-mcp-server\\.venv\\bin\\python",
      "args": [
        "C:\\YOUR\\PATH\\TO\\commvault-mcp-server\\src\\server.py"
      ]
    }
  }
}


```
</details>

## Contributing

- We're continuing to add more functionality to this MCP server. If you'd like to leave feedback, file a bug or provide a feature request, please open an issue on this repository.
- Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the Apache License. See the [LICENSE](./LICENSE) file for details.

