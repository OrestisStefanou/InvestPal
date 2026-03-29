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
            name="updateUserContext",
            arguments={
                "user_id": "orestis_user_id",
                "user_profile": {
                    "name": "Orestis",
                    "age": 28
                },
                "user_portfolio": [],
            }
        )
        print(result.structured_content)


asyncio.run(main())