#!/bin/bash

echo "=== Testing SSE MCP Server with curl ==="

# Test 1: Initialize
echo "1. Testing initialize:"
curl -X POST http://127.0.0.1:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-06-18",
      "capabilities": {},
      "clientInfo": {"name": "test-client", "version": "1.0"}
    }
  }'
echo -e "\n"

# Test 2: List tools
echo "2. Testing tools/list:"
curl -X POST http://127.0.0.1:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }'
echo -e "\n"

# Test 3: Call dspmq tool
echo "3. Testing dspmq tool:"
curl -X POST http://127.0.0.1:8000/mcp/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "dspmq",
      "arguments": {}
    }
  }'
echo -e "\n"

# Test 4: SSE stream (first few events)
echo "4. Testing SSE stream (first 5 seconds):"
timeout 5 curl -N http://127.0.0.1:8000/mcp/sse || echo "SSE test completed"
echo -e "\n"