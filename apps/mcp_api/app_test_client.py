import asyncio

from fastmcp import Client

# HTTP server
client = Client("http://127.0.0.1:9000/mcp")


async def main():
    async with client:
        # Basic server interaction
        await client.ping()

        result = await client.call_tool(
            name="getUserConversationNotes",
            arguments={
                #"note": "user is a 28 year old male",
                # "limit": 1,
            },
        )
        print(result.structured_content)

        # Semantic search. Notes are embedded on write, so anything created
        # before the embeddings feature existed needs `make backfill_embeddings`
        # before it shows up here.
        result = await client.call_tool(
            name="searchUserConversationNotes",
            arguments={
                "query": "the client's view on pension allocation",
                "limit": 3,
                # "min_similarity": 0.7,
            },
        )
        print(result.structured_content)


asyncio.run(main())
