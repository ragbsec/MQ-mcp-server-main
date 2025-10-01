#!/usr/bin/env python3
import asyncio
import json
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from mcp.server import Server
from mcp.types import Tool, TextContent

# MQ Configuration
import os
URL_BASE = os.getenv("MQ_URL", "https://host.docker.internal:9443/ibmmq/rest/v2/admin/")
USER_NAME = os.getenv("MQ_USER", "admin")
PASSWORD = os.getenv("MQ_PASSWORD", "passw0rd")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

server = Server("raghi-mq-sse-server")

@server.list_tools()
async def list_tools():
    return [
        # Basic Tools
        Tool(name="dspmq", description="List queue managers and status", inputSchema={"type": "object", "properties": {}, "required": []}),
        Tool(name="runmqsc", description="Run MQSC command", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}, "mqsc_command": {"type": "string"}}, "required": ["qmgr_name", "mqsc_command"]}),
        
        # Queue Management
        Tool(name="list_queues", description="List all queues", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}}, "required": ["qmgr_name"]}),
        Tool(name="create_queue", description="Create queue", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}, "queue_name": {"type": "string"}, "queue_type": {"type": "string", "default": "local"}}, "required": ["qmgr_name", "queue_name"]}),
        Tool(name="delete_queue", description="Delete queue", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}, "queue_name": {"type": "string"}}, "required": ["qmgr_name", "queue_name"]}),
        Tool(name="get_queue_depth", description="Get queue depth", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}, "queue_name": {"type": "string"}}, "required": ["qmgr_name", "queue_name"]}),
        Tool(name="clear_queue", description="Clear queue messages", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}, "queue_name": {"type": "string"}}, "required": ["qmgr_name", "queue_name"]}),
        
        # Channel Management
        Tool(name="list_channels", description="List all channels", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}}, "required": ["qmgr_name"]}),
        Tool(name="start_channel", description="Start channel", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}, "channel_name": {"type": "string"}}, "required": ["qmgr_name", "channel_name"]}),
        Tool(name="stop_channel", description="Stop channel", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}, "channel_name": {"type": "string"}}, "required": ["qmgr_name", "channel_name"]}),
        Tool(name="ping_channel", description="Ping channel", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}, "channel_name": {"type": "string"}}, "required": ["qmgr_name", "channel_name"]}),
        
        # Message Operations
        Tool(name="put_message", description="Put message to queue", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}, "queue_name": {"type": "string"}, "message": {"type": "string"}}, "required": ["qmgr_name", "queue_name", "message"]}),
        Tool(name="get_message", description="Get message from queue", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}, "queue_name": {"type": "string"}}, "required": ["qmgr_name", "queue_name"]}),
        Tool(name="browse_messages", description="Browse queue messages", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}, "queue_name": {"type": "string"}}, "required": ["qmgr_name", "queue_name"]}),
        
        # Monitoring
        Tool(name="get_queue_stats", description="Get queue statistics", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}, "queue_name": {"type": "string"}}, "required": ["qmgr_name", "queue_name"]}),
        Tool(name="get_channel_status", description="Get channel status", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}, "channel_name": {"type": "string"}}, "required": ["qmgr_name", "channel_name"]}),
        Tool(name="list_connections", description="List active connections", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}}, "required": ["qmgr_name"]}),
        
        # Security
        Tool(name="refresh_security", description="Refresh security", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}}, "required": ["qmgr_name"]}),
        Tool(name="display_auth", description="Display authority records", inputSchema={"type": "object", "properties": {"qmgr_name": {"type": "string"}, "object_name": {"type": "string"}}, "required": ["qmgr_name", "object_name"]})
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    handlers = {
        "dspmq": dspmq,
        "runmqsc": lambda: runmqsc(arguments.get("qmgr_name"), arguments.get("mqsc_command")),
        "list_queues": lambda: list_queues(arguments.get("qmgr_name")),
        "create_queue": lambda: create_queue(arguments.get("qmgr_name"), arguments.get("queue_name"), arguments.get("queue_type", "local")),
        "delete_queue": lambda: delete_queue(arguments.get("qmgr_name"), arguments.get("queue_name")),
        "get_queue_depth": lambda: get_queue_depth(arguments.get("qmgr_name"), arguments.get("queue_name")),
        "clear_queue": lambda: clear_queue(arguments.get("qmgr_name"), arguments.get("queue_name")),
        "list_channels": lambda: list_channels(arguments.get("qmgr_name")),
        "start_channel": lambda: start_channel(arguments.get("qmgr_name"), arguments.get("channel_name")),
        "stop_channel": lambda: stop_channel(arguments.get("qmgr_name"), arguments.get("channel_name")),
        "ping_channel": lambda: ping_channel(arguments.get("qmgr_name"), arguments.get("channel_name")),
        "put_message": lambda: put_message(arguments.get("qmgr_name"), arguments.get("queue_name"), arguments.get("message")),
        "get_message": lambda: get_message(arguments.get("qmgr_name"), arguments.get("queue_name")),
        "browse_messages": lambda: browse_messages(arguments.get("qmgr_name"), arguments.get("queue_name")),
        "get_queue_stats": lambda: get_queue_stats(arguments.get("qmgr_name"), arguments.get("queue_name")),
        "get_channel_status": lambda: get_channel_status(arguments.get("qmgr_name"), arguments.get("channel_name")),
        "list_connections": lambda: list_connections(arguments.get("qmgr_name")),
        "refresh_security": lambda: refresh_security(arguments.get("qmgr_name")),
        "display_auth": lambda: display_auth(arguments.get("qmgr_name"), arguments.get("object_name"))
    }
    
    if name in handlers:
        result = await handlers[name]()
        return [TextContent(type="text", text=result)]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def mq_request(method: str, endpoint: str, data: dict = None, base_url: str = None):
    headers = {"Content-Type": "application/json", "ibm-mq-rest-csrf-token": "token"}
    auth = httpx.BasicAuth(username=USER_NAME, password=PASSWORD)
    url = (base_url or URL_BASE) + endpoint
    
    async with httpx.AsyncClient(verify=False, auth=auth) as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, timeout=30.0)
            elif method == "POST":
                response = await client.post(url, json=data, headers=headers, timeout=30.0)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json() if response.content else {"status": "success"}
        except Exception as e:
            return {"error": str(e)}

# MQ Functions (same as raghi-mcp-server.py)
async def dspmq():
    result = await mq_request("GET", "qmgr/")
    if "error" in result:
        return f"Error: {result['error']}"
    output = "\n---\n"
    for qmgr in result.get('qmgr', []):
        output += f"name = {qmgr['name']}, running = {qmgr['state']}\n---\n"
    return output

async def runmqsc(qmgr_name: str, mqsc_command: str):
    data = {"type": "runCommand", "parameters": {"command": mqsc_command}}
    result = await mq_request("POST", f"action/qmgr/{qmgr_name}/mqsc", data)
    if "error" in result:
        return f"Error: {result['error']}"
    output = "\n---\n"
    for cmd in result.get('commandResponse', []):
        output += cmd['text'][0] + "\n---\n"
    return output

async def list_queues(qmgr_name: str):
    return await runmqsc(qmgr_name, "DISPLAY QUEUE(*) TYPE")

async def create_queue(qmgr_name: str, queue_name: str, queue_type: str):
    return await runmqsc(qmgr_name, f"DEFINE QLOCAL({queue_name})")

async def delete_queue(qmgr_name: str, queue_name: str):
    return await runmqsc(qmgr_name, f"DELETE QLOCAL({queue_name})")

async def get_queue_depth(qmgr_name: str, queue_name: str):
    return await runmqsc(qmgr_name, f"DISPLAY QUEUE({queue_name}) CURDEPTH")

async def clear_queue(qmgr_name: str, queue_name: str):
    return await runmqsc(qmgr_name, f"CLEAR QLOCAL({queue_name})")

async def list_channels(qmgr_name: str):
    return await runmqsc(qmgr_name, "DISPLAY CHANNEL(*)")

async def start_channel(qmgr_name: str, channel_name: str):
    return await runmqsc(qmgr_name, f"START CHANNEL({channel_name})")

async def stop_channel(qmgr_name: str, channel_name: str):
    return await runmqsc(qmgr_name, f"STOP CHANNEL({channel_name})")

async def ping_channel(qmgr_name: str, channel_name: str):
    return await runmqsc(qmgr_name, f"PING CHANNEL({channel_name})")

async def put_message(qmgr_name: str, queue_name: str, message: str):
    return f"Note: Use amqsput command to put messages. Message '{message}' would be put to {queue_name} on {qmgr_name}"

async def get_message(qmgr_name: str, queue_name: str):
    # Try REST API v3 messaging first
    try:
        url = URL_BASE.replace('/v2/admin/', '/v3/messaging/')
        result = await mq_request("GET", f"qmgr/{qmgr_name}/queue/{queue_name}/message", base_url=url)
        if "error" not in result:
            return f"Message retrieved via REST API: {result}"
    except:
        pass
    
    # Fallback to queue depth check and command guidance
    depth_result = await runmqsc(qmgr_name, f"DISPLAY QUEUE({queue_name}) CURDEPTH")
    
    import re
    depth_match = re.search(r'CURDEPTH\((\d+)\)', depth_result)
    if depth_match:
        depth = int(depth_match.group(1))
        if depth == 0:
            return f"{depth_result}\n\nNo messages to retrieve."
        else:
            return f"{depth_result}\n\nTo get all {depth} messages, use: podman exec ibm-mq-server bash -c 'for i in {{1..{depth}}}; do /opt/mqm/samp/bin/amqsget {queue_name} {qmgr_name}; done'"
    
    return f"{depth_result}\n\nUse: podman exec ibm-mq-server /opt/mqm/samp/bin/amqsget {queue_name} {qmgr_name}"

async def browse_messages(qmgr_name: str, queue_name: str):
    # First get queue depth
    depth_result = await runmqsc(qmgr_name, f"DISPLAY QUEUE({queue_name}) CURDEPTH")
    
    # Try to browse actual message content using REST API
    try:
        result = await mq_request("GET", f"messaging/qmgr/{qmgr_name}/queue/{queue_name}/message")
        if "error" not in result:
            return f"Queue depth info:\n{depth_result}\n\nMessage content:\n{result}"
    except:
        pass
    
    return f"{depth_result}\n\nNote: To view message content, use: podman exec ibm-mq-server /opt/mqm/samp/bin/amqsbcg {queue_name} {qmgr_name}"

async def get_queue_stats(qmgr_name: str, queue_name: str):
    return await runmqsc(qmgr_name, f"DISPLAY QUEUE({queue_name}) ALL")

async def get_channel_status(qmgr_name: str, channel_name: str):
    return await runmqsc(qmgr_name, f"DISPLAY CHSTATUS({channel_name})")

async def list_connections(qmgr_name: str):
    return await runmqsc(qmgr_name, "DISPLAY CONN(*)")

async def refresh_security(qmgr_name: str):
    return await runmqsc(qmgr_name, "REFRESH SECURITY TYPE(CONNAUTH)")

async def display_auth(qmgr_name: str, object_name: str):
    return await runmqsc(qmgr_name, f"DISPLAY AUTHREC OBJNAME({object_name})")

# MCP Message Handler
async def mcp_message_handler(message: dict):
    if message.get("method") == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"experimental": {}, "tools": {"listChanged": False}},
                "serverInfo": {"name": "raghi-mq-sse-server", "version": "1.0.0"}
            }
        }
    elif message.get("method") == "tools/list":
        tools = await list_tools()
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {"tools": [tool.model_dump() for tool in tools]}
        }
    elif message.get("method") == "tools/call":
        params = message.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})
        result = await call_tool(name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {"content": [content.model_dump() for content in result]}
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "error": {"code": -32601, "message": "Method not found"}
        }

# SSE Endpoints
@app.api_route("/sse", methods=["GET", "POST", "OPTIONS"])
@app.api_route("/mcp/sse", methods=["GET", "POST", "OPTIONS"])
async def mcp_sse(request: Request):
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
    
    return StreamingResponse(
        sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/mcp/message")
async def mcp_message(message: dict):
    response = await mcp_message_handler(message)
    return response

@app.get("/health")
async def health():
    return {"status": "healthy", "server": "raghi-mq-sse-server"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)