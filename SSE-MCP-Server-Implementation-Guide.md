# SSE MCP Server Implementation Guide

## Overview
This guide documents the complete implementation of an SSE (Server-Sent Events) MCP (Model Context Protocol) server for IBM MQ operations, including container networking, testing, and troubleshooting.

## Project Structure
```
PythonProject/
├── raghi-sse-server.py              # Main SSE MCP server
├── Dockerfile.sse                   # SSE server container
├── sse-config-mcp.json             # MCP client configuration
├── test-sse-client.html            # HTML SSE test client
├── test-sse-postman.json           # Basic Postman collection
├── test-sse-postman-complete.json  # Complete Postman collection
├── Dockerfile.mq-messaging         # Custom IBM MQ container
├── mqwebuser.xml                   # MQ web user configuration
├── mq-config.mqsc                  # MQSC configuration
└── server.xml                      # Liberty server configuration
```

## 1. SSE MCP Server Implementation

### Core Server (`raghi-sse-server.py`)
- **Framework**: FastAPI with MCP integration
- **Protocol**: Server-Sent Events for real-time communication
- **Tools**: 19 IBM MQ management tools
- **Endpoints**:
  - `/health` - Health check
  - `/mcp/sse` - SSE stream endpoint
  - `/mcp/message` - JSON-RPC message handler

### Key Features
- **Tool Categories**:
  - Basic: `dspmq`, `runmqsc`
  - Queue Management: `list_queues`, `create_queue`, `delete_queue`, `get_queue_depth`, `clear_queue`
  - Channel Management: `list_channels`, `start_channel`, `stop_channel`, `ping_channel`
  - Message Operations: `put_message`, `get_message`, `browse_messages`
  - Monitoring: `get_queue_stats`, `get_channel_status`, `list_connections`
  - Security: `refresh_security`, `display_auth`

### Container Configuration (`Dockerfile.sse`)
```dockerfile
FROM python:3.13-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi httpx "mcp[cli]" uvicorn
COPY raghi-sse-server.py .
EXPOSE 8000
CMD ["python", "raghi-sse-server.py"]
```

## 2. Container Networking Setup

### Network Creation
```bash
podman network create mq-network
```

### IBM MQ Container
```bash
podman run -d --name ibm-mq-server --network mq-network \
  -p 1414:1414 -p 9443:9443 -p 9157:9157 \
  -e LICENSE=accept -e MQ_QMGR_NAME=QM1 \
  -e MQ_APP_PASSWORD=passw0rd -e MQ_ADMIN_PASSWORD=passw0rd \
  -e MQ_ENABLE_EMBEDDED_WEB_SERVER=1 \
  ibm-mq-server
```

### SSE Server Container
```bash
podman run -d --name sse-server --network mq-network \
  -p 8000:8000 \
  -e MQ_URL="https://ibm-mq-server:9443/ibmmq/rest/v2/admin/" \
  raghi-sse-server
```

## 3. MCP Client Configuration

### SSE Configuration (`sse-config-mcp.json`)
```json
{
  "mcpServers": {
    "raghi-mq-sse-server": {
      "transport": {
        "type": "sse",
        "url": "http://localhost:8000/mcp/sse"
      }
    }
  }
}
```

## 4. Testing Implementation

### HTML SSE Client (`test-sse-client.html`)
- **Purpose**: Browser-based SSE connection testing
- **Features**:
  - Real-time SSE connection status
  - Tool listing functionality
  - Interactive tool execution
  - Message display area

### Postman Collections

#### Basic Collection (`test-sse-postman.json`)
- Health Check
- List Tools
- Test dspmq Tool
- SSE Stream endpoint

#### Complete Collection (`test-sse-postman-complete.json`)
**14 comprehensive tests covering:**
- **Basic Operations**: Health, Tools, dspmq
- **Queue Operations**: List, Create, Get Depth, Stats
- **Message Operations**: Put, Get, Browse
- **Advanced Operations**: Channels, MQSC, Connections
- **SSE Stream**: Real-time connection test

### Sample Postman Requests
```json
{
  "name": "List Queues",
  "request": {
    "method": "POST",
    "header": [{"key": "Content-Type", "value": "application/json"}],
    "body": {
      "mode": "raw",
      "raw": "{\n  \"jsonrpc\": \"2.0\",\n  \"id\": 3,\n  \"method\": \"tools/call\",\n  \"params\": {\n    \"name\": \"list_queues\",\n    \"arguments\": {\"qmgr_name\": \"QM1\"}\n  }\n}"
    },
    "url": {"raw": "http://localhost:8000/mcp/message"}
  }
}
```

## 5. Tool Implementation Details

### Working Tools (MQSC-based)
- **dspmq**: `GET /qmgr/` → Queue manager status
- **runmqsc**: `POST /action/qmgr/{qmgr}/mqsc` → MQSC command execution
- **list_queues**: `DISPLAY QUEUE(*) TYPE` → All queues with types
- **get_queue_depth**: `DISPLAY QUEUE({queue}) CURDEPTH` → Message count
- **browse_messages**: Shows queue depth + command guidance

### Message Operations (Command-based)
- **put_message**: Provides `amqsput` command guidance
- **get_message**: Shows queue depth + `amqsget` loop command for all messages
- **browse_messages**: Shows queue depth + `amqsbcg` command guidance

### Enhanced get_message Function
```python
async def get_message(qmgr_name: str, queue_name: str):
    depth_result = await runmqsc(qmgr_name, f"DISPLAY QUEUE({queue_name}) CURDEPTH")
    
    import re
    depth_match = re.search(r'CURDEPTH\((\d+)\)', depth_result)
    if depth_match:
        depth = int(depth_match.group(1))
        if depth == 0:
            return f"{depth_result}\n\nNo messages to retrieve."
        else:
            return f"{depth_result}\n\nTo get all {depth} messages, use: podman exec ibm-mq-server bash -c 'for i in {{1..{depth}}}; do /opt/mqm/samp/bin/amqsget {queue_name} {qmgr_name}; done'"
```

## 6. Troubleshooting & Solutions

### SSE Connection Issues
**Problem**: `TypeError: terminated: other side closed`
**Solution**: Added proper disconnection handling and reduced ping interval
```python
async def sse_stream():
    try:
        yield "data: " + json.dumps({"type": "connection", "status": "connected"}) + "\n\n"
        while True:
            if await request.is_disconnected():
                break
            await asyncio.sleep(5)
            yield "data: " + json.dumps({"type": "ping", "timestamp": asyncio.get_event_loop().time()}) + "\n\n"
    except Exception as e:
        yield "data: " + json.dumps({"type": "error", "message": str(e)}) + "\n\n"
```

### Container Networking Issues
**Problem**: SSE server couldn't connect to IBM MQ
**Solution**: Created shared network and used container names for communication
```bash
podman network create mq-network
# Use ibm-mq-server:9443 instead of localhost:9443
```

### REST API 404 Errors
**Problem**: `404 Not Found` for queue and message endpoints
**Solution**: IBM MQ REST API v2 doesn't support direct queue/message operations
- Used MQSC commands instead of REST endpoints
- Provided command-line tool guidance for message operations

### Postman Import Issues
**Problem**: "We don't recognize/support this format"
**Solution**: Added required Postman collection schema
```json
{
  "info": {
    "_postman_id": "12345678-1234-1234-1234-123456789012",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  }
}
```

## 7. Current Status & Results

### ✅ Working Features
- **SSE Connection**: Stable real-time communication
- **19 MQ Tools**: All tools accessible via SSE interface
- **Container Networking**: Proper inter-container communication
- **Queue Operations**: List, create, delete, depth checking
- **Message Counting**: Accurate message depth reporting
- **Command Guidance**: Proper amqsput/amqsget/amqsbcg commands
- **Postman Testing**: Complete test collection with 14 endpoints

### ✅ Test Results
- **Health Check**: `{"status":"healthy","server":"raghi-mq-sse-server"}`
- **Tool Count**: 19 tools available
- **Queue Listing**: Shows all system and application queues
- **Message Operations**: Correctly detects and handles multiple messages
- **SSE Streaming**: Stable connection with ping/pong

### 📋 Usage Examples
```bash
# Test message flow
for i in {1..10}; do 
  podman exec ibm-mq-server bash -c "echo 'Test message $i' | /opt/mqm/samp/bin/amqsput TEST.QUEUE QM1"
done

# Get all messages
curl -s -X POST http://localhost:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "get_message", "arguments": {"qmgr_name": "QM1", "queue_name": "TEST.QUEUE"}}}'

# Result: Shows CURDEPTH(10) and command to get all 10 messages
```

## 8. Next Steps & Improvements

### Potential Enhancements
1. **Direct Message Content**: Implement actual message retrieval via REST API v3 (requires complex Liberty configuration)
2. **Batch Operations**: Support for multiple queue operations
3. **Real-time Monitoring**: SSE-based queue depth monitoring
4. **Error Handling**: Enhanced error reporting and recovery
5. **Authentication**: Support for different MQ user credentials

### Alternative Approaches
- **WebSocket**: For bidirectional communication
- **gRPC**: For high-performance operations
- **Direct MQ Client**: Using PyMQ or similar libraries

## 9. Files Reference

### Key Configuration Files
- `raghi-sse-server.py` - Main server implementation
- `test-sse-postman-complete.json` - Complete test suite
- `sse-config-mcp.json` - MCP client configuration
- `test-sse-client.html` - Browser-based testing

### Container Commands
```bash
# Build and run SSE server
podman build -f Dockerfile.sse -t raghi-sse-server .
podman run -d --name sse-server --network mq-network -p 8000:8000 raghi-sse-server

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/mcp/sse
```

This implementation provides a complete, working SSE MCP server for IBM MQ operations with comprehensive testing capabilities and proper container networking.