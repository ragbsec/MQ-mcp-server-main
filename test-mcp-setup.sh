#!/bin/bash
set -e

echo "=== Setting up and Testing MCP Server ==="

# Setup MCP server
echo "Setting up MCP server..."
cd mq-mcp-server-main
uv add "mcp[cli]" httpx

# Test MCP server
echo "Testing MCP server..."
uv run test_mcp.py

echo "=== MCP Server Setup Complete ==="
echo "MCP Server ready in: $(pwd)"