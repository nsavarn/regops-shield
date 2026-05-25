# mcp_server.py
# RegOps Shield — Model Context Protocol Server
# Lightweight MCP Server exposing search_policies to Gemini 2.0 Flash
# This implements Option B: a tiny MCP wrapper for MongoDB Atlas

import os
import json
from dotenv import load_dotenv
from memory.mongo_utils import MongoUtils

load_dotenv()

# ─────────────────────────────────────────────────────────────
# MCP Tool Definitions (MCP Protocol v1.0.0 compatible)
# ─────────────────────────────────────────────────────────────

def list_tools():
    """Return list of MCP tools for tool listing."""
    return {
        "tools": [
            {
                "name": "search_policies",
                "description": "Search regulatory policies from MongoDB Atlas. Returns relevant policy documents with category, jurisdiction, and risk thresholds.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Keywords describing the compliance risk or claim type to search for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of policies to retrieve (default: 5)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "vector_search_policies",
                "description": "Semantic policy search using Google text-embedding-004 + Atlas Vector Search (768 dims). Falls back to keyword search if index missing.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language query for semantic matching"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of policies to retrieve (default: 5)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "health_check",
                "description": "Check if MongoDB Atlas connection is alive and ready.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    }


class MCPServer:
    """Lightweight MCP server exposing MongoDB Atlas as a tool provider.
    
    This implements the Model Context Protocol (MCP) server pattern:
    - Tool listing via list_tools()
    - Tool execution via call_tool()
    - Supports search_policies + vector_search_policies tools
    - Fully compatible with MongoDB Atlas MCP terminology
    - Used internally by SupervisorAgent for native tool calling
    - Also callable standalone for debugging and testing
    """
    
    def __init__(self):
        self.mongo = MongoUtils()
    
    def call_tool(self, name: str, arguments: dict) -> dict:
        """Execute an MCP tool by name with arguments.
        
        Args:
            name: Tool name (search_policies, vector_search_policies, health_check)
            arguments: Dict of tool arguments
            
        Returns:
            dict: Tool execution result
        """
        if name == "search_policies":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 5)
            results = self.mongo.search_policies(query, limit=limit, use_vector=False)
            return {
                "content": [{"type": "text", "text": json.dumps(results, indent=2)}]
            }
        
        elif name == "vector_search_policies":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 5)
            results = self.mongo.vector_search_policies(query, limit=limit)
            return {
                "content": [{"type": "text", "text": json.dumps(results, indent=2)}]
            }
        
        elif name == "health_check":
            healthy = self.mongo.health_check()
            return {
                "content": [{"type": "text", "text": json.dumps({"healthy": healthy})}]
            }
        
        else:
            return {
                "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
                "isError": True
            }


# ─────────────────────────────────────────────────────────────
# CLI Entry Point (for testing)
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("RegOps Shield — MCP Server")
    print("=" * 60)
    
    # List available tools
    tools = list_tools()
    print("\nAvailable MCP Tools:")
    for tool in tools["tools"]:
        print(f"  - {tool['name']}: {tool['description'][:60]}...")
    
    # Test vector search
    print("\nTesting vector_search_policies tool...")
    server = MCPServer()
    result = server.call_tool("vector_search_policies", {
        "query": "high amount international provider review",
        "limit": 3
    })
    print(result["content"][0]["text"])
    
    print("\nMCP Server test complete.")
