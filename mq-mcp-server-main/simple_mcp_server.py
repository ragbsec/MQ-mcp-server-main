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

server = Server("ibm-mq-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="dspmq",
            description="List available queue managers and their status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
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
    headers = {"Content-Type": "application/json", "ibm-mq-rest-csrf-token": "token"}
    url = URL_BASE + "qmgr/"
    auth = httpx.BasicAuth(username=USER_NAME, password=PASSWORD)
    
    async with httpx.AsyncClient(verify=False, auth=auth) as client:
        try:
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
    headers = {"Content-Type": "application/json", "ibm-mq-rest-csrf-token": "a"}
    data = json.dumps({"type": "runCommand", "parameters": {"command": mqsc_command}})
    url = URL_BASE + f"action/qmgr/{qmgr_name}/mqsc"
    auth = httpx.BasicAuth(username=USER_NAME, password=PASSWORD)
    
    async with httpx.AsyncClient(verify=False, auth=auth) as client:
        try:
            response = await client.post(url, data=data, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            result = "\n---\n"
            for cmd in data['commandResponse']:
                result += cmd['text'][0] + "\n---\n"
            return result
        except Exception as e:
            return f"Error: {str(e)}"

async def main():
    import sys
    print("Starting simple MCP server...", file=sys.stderr)
    try:
        from mcp.server.stdio import stdio_server
        print("Stdio server imported successfully", file=sys.stderr)
        async with stdio_server() as (read_stream, write_stream):
            print("Stdio streams created", file=sys.stderr)
            await server.run(read_stream, write_stream, server.create_initialization_options())
    except Exception as e:
        print(f"Error in main: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())