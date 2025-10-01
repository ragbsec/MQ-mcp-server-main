# Raghi MCP Server Container Setup

## Overview
This setup containerizes the `raghi-mcp-server.py` using Podman, allowing you to run the MCP server in an isolated environment.

## Files Created
- `Dockerfile.mcp` - Container definition for the MCP server
- `mcp-docker.json` - MCP configuration to use the containerized server
- `build-mcp-container.sh` - Script to build the container
- `test-mcp-container.sh` - Script to test the container

## Quick Start

### 1. Build the Container
```bash
./build-mcp-container.sh
```

### 2. Use in MCP Configuration
Copy the `mcp-docker.json` configuration to your MCP client:

```json
{
  "mcpServers": {
    "raghi-mq-server": {
      "command": "podman",
      "args": [
        "run",
        "--rm",
        "-i",
        "--network=host",
        "raghi-mcp-server"
      ]
    }
  }
}
```

### 3. Manual Container Run (for testing)
```bash
# Interactive mode
podman run --rm -i --network=host raghi-mcp-server

# Background mode
podman run -d --name mcp-server --network=host raghi-mcp-server
```

## Container Features
- **Base Image**: Python 3.13-slim
- **Dependencies**: fastapi, httpx, mcp[cli], uvicorn
- **Network**: Uses host network to connect to IBM MQ
- **Port**: Exposes 8000 (for potential HTTP interface)

## Prerequisites
- IBM MQ server running (use `start-mq-mcp.sh`)
- Podman installed and running
- MCP client configured to use `mcp-docker.json`

## Available MQ Tools
The containerized server provides all IBM MQ management tools:
- Queue management (create, delete, list, clear)
- Channel operations (start, stop, ping)
- Message operations (put, get, browse)
- Monitoring and statistics
- Security management

## Troubleshooting
- Ensure IBM MQ is running before starting the MCP container
- Use `--network=host` to allow container access to localhost MQ
- Check container logs: `podman logs <container-id>`