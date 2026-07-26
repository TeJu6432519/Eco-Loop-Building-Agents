import asyncio
from fastmcp import Client

async def test_server():
    # Connect to the local running server using stdio transport
    async with Client("mcp/mcp_server.py") as client:
        print("Connected to MCP Server successfully!\n")

        # Test Tool 1: Get building thresholds
        thresholds = await client.call_tool("get_building_target_thresholds", {})
        print("Tool Output (Thresholds):", thresholds)

        # Test Tool 2: Check simulation logs
        logs = await client.call_tool("check_simulation_logs", {})
        print("Tool Output (Logs):", logs)

if __name__ == "__main__":
    asyncio.run(test_server())