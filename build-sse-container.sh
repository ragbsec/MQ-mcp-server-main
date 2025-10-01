#!/bin/bash
set -e

echo "=== Building Raghi SSE Server Container ==="

# Build the SSE server image
echo "Building raghi-sse-server image..."
podman build -f Dockerfile.sse -t raghi-sse-server .

echo "=== SSE Server Container Built Successfully ==="
echo "Run: podman run -d --name sse-server -p 8000:8000 --network=host raghi-sse-server"