#!/usr/bin/env python3
import asyncio
import json
import httpx
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# MQ Configuration
URL_BASE = "https://localhost:9443/ibmmq/rest/v2/admin/"
USER_NAME = "admin"
PASSWORD = "passw0rd"

app = FastAPI()

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

async def handle_mcp_message(message: dict):
    """Handle MCP protocol messages"""
    method = message.get("method")
    msg_id = message.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "ibm-mq-server", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": [
                    {
                        "name": "dspmq",
                        "description": "List queue managers",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "runmqsc",
                        "description": "Run MQSC command",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "qmgr_name": {"type": "string"},
                                "mqsc_command": {"type": "string"}
                            },
                            "required": ["qmgr_name", "mqsc_command"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = message.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if name == "dspmq":
            result = await dspmq()
        elif name == "runmqsc":
            result = await runmqsc(arguments.get("qmgr_name"), arguments.get("mqsc_command"))
        else:
            result = f"Unknown tool: {name}"
            
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"content": [{"type": "text", "text": result}]}
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": "Method not found"}
        }

async def sse_generator():
    """Generate SSE events"""
    # Send initial connection event
    yield f"data: {json.dumps({'type': 'connection', 'status': 'connected'})}\n\n"
    
    # Keep connection alive with periodic pings
    while True:
        await asyncio.sleep(30)
        yield f"data: {json.dumps({'type': 'ping', 'timestamp': asyncio.get_event_loop().time()})}\n\n"

@app.get("/")
async def root():
    return {"message": "IBM MQ MCP Server", "endpoints": ["/sse", "/message"]}

@app.get("/sse")
async def sse_endpoint():
    """Standard SSE endpoint"""
    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.post("/message")
async def message_endpoint(message: dict):
    """Handle MCP messages"""
    response = await handle_mcp_message(message)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)