#!/bin/bash
set -e

echo "=== Cleaning up IBM MQ MCP Server ==="

# Stop and remove container
echo "Stopping IBM MQ container..."
podman stop ibm-mq-server 2>/dev/null || echo "Container already stopped"
podman rm ibm-mq-server 2>/dev/null || echo "Container already removed"

# Remove image
echo "Removing IBM MQ image..."
podman rmi ibm-mq-server 2>/dev/null || echo "Image already removed"

# Stop Podman machine
echo "Stopping Podman machine..."
podman machine stop 2>/dev/null || echo "Machine already stopped"

# Clean MCP server virtual environment
echo "Cleaning MCP server environment..."
cd mq-mcp-server-main 2>/dev/null && rm -rf .venv 2>/dev/null || echo "No MCP environment to clean"

echo "=== Cleanup Complete ==="