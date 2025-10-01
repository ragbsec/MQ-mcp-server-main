#!/bin/bash
set -e

echo "=== Starting Raghi SSE Server ==="

# Stop existing container if running
podman stop sse-server 2>/dev/null || true
podman rm sse-server 2>/dev/null || true

# Start SSE server with host networking
echo "Starting SSE server container..."
podman run -d --name sse-server --network=host raghi-sse-server

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Test server
echo "Testing server health..."
curl -s http://localhost:8000/health || echo "Server not ready yet"

echo "=== SSE Server Started ==="
echo "Server available at: http://localhost:8000"
echo "Health check: http://localhost:8000/health"
echo "SSE endpoint: http://localhost:8000/sse"
echo "MCP endpoint: http://localhost:8000/mcp/message"