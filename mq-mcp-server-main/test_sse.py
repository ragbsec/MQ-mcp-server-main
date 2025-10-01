#!/usr/bin/env python3
import asyncio
import httpx
import json

async def test_sse_endpoints():
    """Test the SSE MCP server endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    async with httpx.AsyncClient() as client:
        print("=== Testing SSE MCP Server ===\n")
        
        # Test 1: Initialize
        print("1. Testing initialize:")
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"}
            }
        }
        response = await client.post(f"{base_url}/message", json=init_message)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
        
        # Test 2: List tools
        print("2. Testing tools/list:")
        tools_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        response = await client.post(f"{base_url}/message", json=tools_message)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
        
        # Test 3: Call dspmq tool
        print("3. Testing dspmq tool:")
        dspmq_message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "dspmq",
                "arguments": {}
            }
        }
        response = await client.post(f"{base_url}/message", json=dspmq_message)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
        
        # Test 4: Call runmqsc tool
        print("4. Testing runmqsc tool:")
        runmqsc_message = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "runmqsc",
                "arguments": {
                    "qmgr_name": "QM1",
                    "mqsc_command": "DISPLAY QMGR QMNAME"
                }
            }
        }
        response = await client.post(f"{base_url}/message", json=runmqsc_message)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

async def test_sse_stream():
    """Test the SSE stream endpoint"""
    print("5. Testing SSE stream (first event):")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            async with client.stream("GET", "http://127.0.0.1:8000/sse") as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        print(f"SSE Event: {line}")
                        print("SSE connection working!")
                        break
    except httpx.ReadTimeout:
        print("SSE connection established, timeout waiting for next event (expected)")
    except Exception as e:
        print(f"SSE test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_sse_endpoints())
    asyncio.run(test_sse_stream())