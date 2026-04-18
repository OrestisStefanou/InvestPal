import asyncio
from fastmcp import Client
from datetime import datetime, timedelta

# HTTP server
client = Client("http://127.0.0.1:9000/mcp")


async def main():
    async with client:
        # Basic server interaction
        await client.ping()

        result = await client.call_tool(
            name="getSkill",
            arguments={
                "skill_name": "analyze_stock_valuation",
                #"limit": 1,
            }
        )
        print(result.structured_content)


asyncio.run(main())