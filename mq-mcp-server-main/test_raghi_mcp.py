#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('.')

# Import functions from raghi-mcp-server
import importlib.util
spec = importlib.util.spec_from_file_location("raghi_mcp_server", "raghi-mcp-server.py")
raghi_mcp_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(raghi_mcp_server)

dspmq = raghi_mcp_server.dspmq
list_queues = raghi_mcp_server.list_queues
get_queue_depth = raghi_mcp_server.get_queue_depth
list_channels = raghi_mcp_server.list_channels

async def test_raghi_mcp():
    print("=== Testing Raghi's Comprehensive MQ MCP Server ===\n")
    
    # Test 1: List queue managers
    print("1. Testing dspmq:")
    result = await dspmq()
    print(result)
    
    # Test 2: List queues
    print("2. Testing list_queues:")
    result = await list_queues("QM1")
    print(result)
    
    # Test 3: Get queue depth
    print("3. Testing get_queue_depth:")
    result = await get_queue_depth("QM1", "TEST.QUEUE")
    print(result)
    
    # Test 4: List channels
    print("4. Testing list_channels:")
    result = await list_channels("QM1")
    print(result[:500] + "..." if len(result) > 500 else result)
    
    print("=== Raghi MCP Server Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_raghi_mcp())