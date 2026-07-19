import asyncio
from datetime import datetime, timedelta

from fastmcp import Client

# HTTP server
client = Client("http://127.0.0.1:9000/mcp")


async def main():
    async with client:
        # Basic server interaction
        await client.ping()

        result = await client.call_tool(
            name="createUserProfileNote",
            arguments={
                "note": "user is a 28 year old male",
                # "limit": 1,
            },
        )
        print(result.structured_content)


asyncio.run(main())
