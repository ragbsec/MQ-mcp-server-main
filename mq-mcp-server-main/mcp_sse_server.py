#!/usr/bin/env python3
import asyncio
import json
import httpx
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from mcp.server import Server
from mcp.types import Tool, TextContent

# MQ Configuration
URL_BASE = "https://localhost:9443/ibmmq/rest/v2/admin/"
USER_NAME = "admin"
PASSWORD = "passw0rd"

app = FastAPI()
server = Server("ibm-mq-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="dspmq",
            description="List available queue managers and their status",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="runmqsc",
            description="Run MQSC command against a queue manager",
            inputSchema={
                "type": "object",
                "properties": {
                    "qmgr_name": {"type": "string", "description": "Queue manager name"},
                    "mqsc_command": {"type": "string", "description": "MQSC command to execute"}
                },
                "required": ["qmgr_name", "mqsc_command"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "dspmq":
        result = await dspmq()
        return [TextContent(type="text", text=result)]
    elif name == "runmqsc":
        qmgr_name = arguments.get("qmgr_name")
        mqsc_command = arguments.get("mqsc_command")
        result = await runmqsc(qmgr_name, mqsc_command)
        return [TextContent(type="text", text=result)]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def dspmq():
    try:
        headers = {"Content-Type": "application/json", "ibm-mq-rest-csrf-token": "token"}
        url = URL_BASE + "qmgr/"
        auth = httpx.BasicAuth(username=USER_NAME, password=PASSWORD)
        
        async with httpx.AsyncClient(verify=False, auth=auth) as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            result = "\n---\n"
            for qmgr in data['qmgr']:
                result += f"name = {qmgr['name']}, running = {qmgr['state']}\n---\n"
            return result
    except Exception as e:
        return f"Error: {str(e)}"

async def runmqsc(qmgr_name: str, mqsc_command: str):
    try:
        headers = {"Content-Type": "application/json", "ibm-mq-rest-csrf-token": "a"}
        data = json.dumps({"type": "runCommand", "parameters": {"command": mqsc_command}})
        url = URL_BASE + f"action/qmgr/{qmgr_name}/mqsc"
        auth = httpx.BasicAuth(username=USER_NAME, password=PASSWORD)
        
        async with httpx.AsyncClient(verify=False, auth=auth) as client:
            response = await client.post(url, data=data, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            result = "\n---\n"
            for cmd in data['commandResponse']:
                result += cmd['text'][0] + "\n---\n"
            return result
    except Exception as e:
        return f"Error: {str(e)}"

async def mcp_message_handler(message: dict):
    """Handle MCP messages and return responses"""
    if message.get("method") == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"experimental": {}, "tools": {"listChanged": False}},
                "serverInfo": {"name": "ibm-mq-server", "version": "1.0.0"}
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

async def sse_stream():
    """SSE stream for MCP communication"""
    yield "data: " + json.dumps({"type": "connection", "status": "connected"}) + "\n\n"
    
    # Keep connection alive
    while True:
        await asyncio.sleep(30)
        yield "data: " + json.dumps({"type": "ping", "timestamp": asyncio.get_event_loop().time()}) + "\n\n"

@app.get("/sse")
async def mcp_sse():
    """SSE endpoint for MCP communication"""
    return StreamingResponse(
        sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

@app.get("/mcp/sse")
async def mcp_sse_alt():
    """Alternative SSE endpoint for MCP communication"""
    return StreamingResponse(
        sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

@app.post("/mcp/message")
async def mcp_message(message: dict):
    """Handle MCP messages via POST"""
    response = await mcp_message_handler(message)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)