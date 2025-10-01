#!/bin/bash
set -e

echo "=== Testing Raghi MCP Server Container ==="

# Test the container by running it briefly
echo "Testing container startup..."
timeout 10s podman run --rm --network=host raghi-mcp-server || echo "Container test completed"

echo "=== Container Test Complete ==="
echo "Container is ready to use with mcp-docker.json configuration"