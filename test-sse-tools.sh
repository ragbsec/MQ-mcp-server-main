#!/bin/bash
set -e

echo "=== Testing SSE Server Tools ==="

BASE_URL="http://localhost:8000"

# Test health endpoint
echo "Testing health endpoint..."
curl -s "$BASE_URL/health" | jq .

# Test tools list
echo -e "\nTesting tools list..."
curl -s -X POST "$BASE_URL/mcp/message" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }' | jq .

# Test dspmq tool
echo -e "\nTesting dspmq tool..."
curl -s -X POST "$BASE_URL/mcp/message" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "dspmq",
      "arguments": {}
    }
  }' | jq .

echo -e "\n=== SSE Server Test Complete ==="