from typing import Annotated

from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan
from fastmcp.dependencies import (
    Depends,
    CurrentContext,
)
from pymongo import AsyncMongoClient

from config import settings
from services.user_context import (
    MongoDBUserContextService,
    UserContextService,
)
from models.user_context import (
    UserContext,
    UserPortfolioHolding
)


@lifespan
async def db_lifespan(server):
    db_client = AsyncMongoClient(settings.MONGO_URI)
    yield {"db_client": db_client}
    await db_client.close()


def get_user_context_service(ctx = Depends(CurrentContext)) -> UserContextService:
    db_client = ctx.lifespan_context["db_client"]
    return MongoDBUserContextService(mongo_client=db_client)


mcp_app = FastMCP("InvestPal MCP Server", lifespan=db_lifespan)

@mcp_app.tool(
    name="updateUserContext",
    description="Update the user context(for the given user_id) including user profile and portfolio holdings. Note: The provided context will completely replace the existing one, so the entire updated object must be provided.",
)
async def update_user_context(
    user_id: Annotated[str, "The id of the user to update the context for"],
    user_profile: Annotated[dict, "General information about the user. Must provide the complete user profile as it will replace the existing one."],
    user_portfolio: Annotated[list[UserPortfolioHolding], "List of portfolio holdings. Must provide the complete portfolio as it will replace the existing one."],
    user_context_service: UserContextService = Depends(get_user_context_service),
):
    pass


if __name__ == "__main__":
    mcp_app.run(transport="http", host="127.0.0.1", port=9000)