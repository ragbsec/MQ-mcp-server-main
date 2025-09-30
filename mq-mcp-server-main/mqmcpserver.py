#
# Copyright (c) 2025 IBM Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import httpx
import json

from typing import Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mqmcpserver")

# Change this to point to your mqweb server
URL_BASE = "https://localhost:9443/ibmmq/rest/v2/admin/"

# Change these to a suitable user in your mqweb server
USER_NAME = "admin"
PASSWORD = "passw0rd"

@mcp.tool()
async def dspmq() -> str:
    """List available queue managers and whether they are running or not
    """
    headers = {
        "Content-Type": "application/json",
        "ibm-mq-rest-csrf-token": "token"
    }    
    
    url = URL_BASE + "qmgr/"

    auth = httpx.BasicAuth(username=USER_NAME, password=PASSWORD)
    async with httpx.AsyncClient(verify=False,auth=auth) as client:
        try:            
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return prettify_dspmq(response.content)
        except Exception as err:
            print(err)
            return "Something went wrong!"
                        
# Put the output of for each queue manager on its own line, separated by ---                        
def prettify_dspmq(payload: str) -> str:
    jsonOutput = json.loads(payload.decode("utf-8"))
    prettifiedOutput="\n---\n"
    for x in jsonOutput['qmgr']:
      prettifiedOutput += "name = " + x['name'] + ", running = " + x['state'] + "\n---\n"
    
    return prettifiedOutput
    
@mcp.tool()
async def runmqsc(qmgr_name: str, mqsc_command: str) -> str:
    """Run an MQSC command against a specific queue manager

    Args:
        qmgr_name: A queue manager name   
        mqsc_command: An MQSC command to run on the queue manager   
    """
    headers = {
        "Content-Type": "application/json",
        "ibm-mq-rest-csrf-token": "a"
    }
    
    data = "{\"type\":\"runCommand\",\"parameters\":{\"command\":\"" + mqsc_command + "\"}}"
    
    url = URL_BASE + "action/qmgr/" + qmgr_name + "/mqsc"

    auth = httpx.BasicAuth(username=USER_NAME, password=PASSWORD)
    async with httpx.AsyncClient(verify=False,auth=auth) as client:
        try:            
            response = await client.post(url, data=data, headers=headers, timeout=30.0)
            response.raise_for_status()
            return prettify_runmqsc(response.content)
        except Exception as err:
            print(err)
            return "Something went wrong!"
            
# Put the output of each MQSC command on its own line, separated by ---
# For the moment this will not work against z/OS queue managers which use a slightly different format.
def prettify_runmqsc(payload: str) -> str:
    jsonOutput = json.loads(payload.decode("utf-8"))
    prettifiedOutput="\n---\n"
    for x in jsonOutput['commandResponse']:
      prettifiedOutput += x['text'][0] + "\n---\n"
    
    return prettifiedOutput    

if __name__ == "__main__":
    import sys
    import asyncio
    
    print("Starting IBM MQ MCP Server...", file=sys.stderr)
    
    # Test MQ connection first
    async def test_connection():
        try:
            result = await dspmq()
            print(f"MQ Connection test: {result[:50]}...", file=sys.stderr)
            return True
        except Exception as e:
            print(f"MQ Connection failed: {e}", file=sys.stderr)
            return False
    
    # Test connection before starting server
    if asyncio.run(test_connection()):
        print("MQ connection successful, starting MCP server...", file=sys.stderr)
        try:
            mcp.run()
        except Exception as e:
            print(f"Error starting MCP server: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("MQ connection failed, exiting...", file=sys.stderr)
        sys.exit(1)
