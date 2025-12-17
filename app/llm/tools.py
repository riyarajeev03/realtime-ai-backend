import json
import random
from typing import Dict, Any

async def calculate_tool(arguments: str) -> Dict[str, Any]:
    """Calculate tool"""
    try:
        args = json.loads(arguments)
        expression = args.get("expression", "2+2")
        return {
            "success": True,
            "expression": expression,
            "result": "4",
            "note": "Simulated calculation"
        }
    except:
        return {"success": False, "error": "Calculation failed"}

async def fetch_data_tool(arguments: str) -> Dict[str, Any]:
    """Fetch data tool"""
    return {
        "success": True,
        "data": [{"id": 1, "value": "sample"}],
        "note": "Simulated data fetch"
    }

async def execute_tool(tool_name: str, arguments: str) -> Dict[str, Any]:
    """Execute tool by name"""
    if tool_name == "calculate":
        return await calculate_tool(arguments)
    elif tool_name == "fetch_data":
        return await fetch_data_tool(arguments)
    else:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}

def available_tools():
    """Return available tools"""
    return [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Perform calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Math expression"}
                    },
                    "required": ["expression"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_data",
                "description": "Fetch data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data_type": {"type": "string", "description": "Type of data"}
                    },
                    "required": ["data_type"]
                }
            }
        }
    ]