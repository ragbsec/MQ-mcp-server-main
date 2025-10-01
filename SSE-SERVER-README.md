# Raghi SSE Server Container Setup

## Overview
This setup provides a containerized SSE (Server-Sent Events) server with all IBM MQ functionality from `raghi-mcp-server.py`. Users can make HTTP calls to interact with IBM MQ tools.

## Files Created
- `raghi-sse-server.py` - SSE server with all MQ functionality
- `Dockerfile.sse` - Container definition for SSE server
- `sse-config.json` - SSE client configuration
- `build-sse-container.sh` - Build script
- `test-sse-tools.sh` - Test script

## Quick Start

### 1. Build and Run Container
```bash
./build-sse-container.sh
podman run -d --name sse-server -p 8000:8000 raghi-sse-server
```

### 2. Test Server Health
```bash
curl http://localhost:8000/health
```

### 3. List Available Tools
```bash
curl -X POST http://localhost:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

### 4. Call MQ Tools
```bash
# List queue managers
curl -X POST http://localhost:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "dspmq",
      "arguments": {}
    }
  }'

# Run MQSC command
curl -X POST http://localhost:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "runmqsc",
      "arguments": {
        "qmgr_name": "QM1",
        "mqsc_command": "DISPLAY QUEUE(*)"
      }
    }
  }'
```

## Available Endpoints

### HTTP Endpoints
- `GET /health` - Health check
- `GET /sse` - SSE stream endpoint
- `POST /mcp/message` - MCP message handler

### Available MQ Tools
- **Basic**: dspmq, runmqsc
- **Queue Management**: list_queues, create_queue, delete_queue, get_queue_depth, clear_queue
- **Channel Management**: list_channels, start_channel, stop_channel, ping_channel
- **Message Operations**: put_message, get_message, browse_messages
- **Monitoring**: get_queue_stats, get_channel_status, list_connections
- **Security**: refresh_security, display_auth

## Container Details
- **Base Image**: Python 3.13-slim
- **Port**: 8000
- **Dependencies**: FastAPI, httpx, MCP, uvicorn
- **Network**: Connects to IBM MQ on localhost

## Prerequisites
- IBM MQ server running (use `start-mq-mcp.sh`)
- Podman installed
- IBM MQ accessible on localhost:9443

## Usage Examples

### Create Queue
```bash
curl -X POST http://localhost:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "create_queue",
      "arguments": {
        "qmgr_name": "QM1",
        "queue_name": "MY.TEST.QUEUE"
      }
    }
  }'
```

### Put Message
```bash
curl -X POST http://localhost:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "put_message",
      "arguments": {
        "qmgr_name": "QM1",
        "queue_name": "TEST.QUEUE",
        "message": "Hello from SSE server!"
      }
    }
  }'
```

## Container Management
```bash
# Start container
podman run -d --name sse-server -p 8000:8000 raghi-sse-server

# Stop container
podman stop sse-server

# View logs
podman logs sse-server

# Remove container
podman rm sse-server
```