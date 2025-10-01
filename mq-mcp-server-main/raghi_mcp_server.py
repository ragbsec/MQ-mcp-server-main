#!/usr/bin/env python3
import asyncio
import json
import sys
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

# MQ Configuration
URL_BASE = "https://localhost:9443/ibmmq/rest/v2/admin/"
USER_NAME = "admin"
PASSWORD = "passw0rd"

server = Server("raghi-mq-server")

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

async def mq_request(method: str, endpoint: str, data: dict = None):
    headers = {"Content-Type": "application/json", "ibm-mq-rest-csrf-token": "token"}
    auth = httpx.BasicAuth(username=USER_NAME, password=PASSWORD)
    url = URL_BASE + endpoint
    
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

# Basic Tools
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

# Queue Management
async def list_queues(qmgr_name: str):
    result = await mq_request("GET", f"qmgr/{qmgr_name}/queue")
    if "error" in result:
        return f"Error: {result['error']}"
    output = "\n---\n"
    for queue in result.get('queue', []):
        output += f"Queue: {queue['name']}, Type: {queue.get('type', 'N/A')}\n---\n"
    return output

async def create_queue(qmgr_name: str, queue_name: str, queue_type: str):
    return await runmqsc(qmgr_name, f"DEFINE QLOCAL({queue_name})")

async def delete_queue(qmgr_name: str, queue_name: str):
    return await runmqsc(qmgr_name, f"DELETE QLOCAL({queue_name})")

async def get_queue_depth(qmgr_name: str, queue_name: str):
    return await runmqsc(qmgr_name, f"DISPLAY QUEUE({queue_name}) CURDEPTH")

async def clear_queue(qmgr_name: str, queue_name: str):
    return await runmqsc(qmgr_name, f"CLEAR QLOCAL({queue_name})")

# Channel Management
async def list_channels(qmgr_name: str):
    return await runmqsc(qmgr_name, "DISPLAY CHANNEL(*)")

async def start_channel(qmgr_name: str, channel_name: str):
    return await runmqsc(qmgr_name, f"START CHANNEL({channel_name})")

async def stop_channel(qmgr_name: str, channel_name: str):
    return await runmqsc(qmgr_name, f"STOP CHANNEL({channel_name})")

async def ping_channel(qmgr_name: str, channel_name: str):
    return await runmqsc(qmgr_name, f"PING CHANNEL({channel_name})")

# Message Operations
async def put_message(qmgr_name: str, queue_name: str, message: str):
    data = {"type": "message", "message": {"applicationData": message}}
    result = await mq_request("POST", f"qmgr/{qmgr_name}/queue/{queue_name}/message", data)
    return f"Message put result: {result}"

async def get_message(qmgr_name: str, queue_name: str):
    result = await mq_request("DELETE", f"qmgr/{qmgr_name}/queue/{queue_name}/message")
    return f"Message get result: {result}"

async def browse_messages(qmgr_name: str, queue_name: str):
    result = await mq_request("GET", f"qmgr/{qmgr_name}/queue/{queue_name}/message")
    return f"Browse result: {result}"

# Monitoring
async def get_queue_stats(qmgr_name: str, queue_name: str):
    return await runmqsc(qmgr_name, f"DISPLAY QUEUE({queue_name}) ALL")

async def get_channel_status(qmgr_name: str, channel_name: str):
    return await runmqsc(qmgr_name, f"DISPLAY CHSTATUS({channel_name})")

async def list_connections(qmgr_name: str):
    return await runmqsc(qmgr_name, "DISPLAY CONN(*)")

# Security
async def refresh_security(qmgr_name: str):
    return await runmqsc(qmgr_name, "REFRESH SECURITY TYPE(CONNAUTH)")

async def display_auth(qmgr_name: str, object_name: str):
    return await runmqsc(qmgr_name, f"DISPLAY AUTHREC OBJNAME({object_name})")

async def main():
    print("Starting Raghi's comprehensive MQ MCP server...", file=sys.stderr)
    try:
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())