#!/usr/bin/env python3
"""
Test script for IBM MQ MCP Server
"""
import asyncio
from mqmcpserver import dspmq, runmqsc

async def main():
    print("=== IBM MQ MCP Server Test ===\n")
    
    # Test 1: List queue managers
    print("1. Listing queue managers:")
    result = await dspmq()
    print(result)
    
    # Test 2: Display queue manager details
    print("2. Queue manager details:")
    result = await runmqsc('QM1', 'DISPLAY QMGR QMNAME CMDLEVEL VERSION')
    print(result)
    
    # Test 3: Display TEST.QUEUE
    print("3. TEST.QUEUE details:")
    result = await runmqsc('QM1', 'DISPLAY QUEUE(TEST.QUEUE)')
    print(result)
    
    # Test 4: Display channels
    print("4. Application channels:")
    result = await runmqsc('QM1', 'DISPLAY CHANNEL(DEV.APP.SVRCONN)')
    print(result)
    
    print("=== MCP Server Test Complete ===")

if __name__ == "__main__":
    asyncio.run(main())