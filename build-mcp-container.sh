#!/bin/bash
set -e

echo "=== Building Raghi MCP Server Container ==="

# Build the MCP server image
echo "Building raghi-mcp-server image..."
podman build -f Dockerfile.mcp -t raghi-mcp-server .

echo "=== MCP Server Container Built Successfully ==="
echo "Use mcp-docker.json configuration to connect to the containerized MCP server"