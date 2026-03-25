import asyncio
import os
import sys
import logging
from typing import Type
from pydantic import BaseModel, Field
from pymongo import AsyncMongoClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Add current directory to path if needed
sys.path.append(os.getcwd())

from config import settings
from dependencies import (
    get_mcp_client,
    get_etf_expert_agent,
    get_crypto_expert_agent,
    get_stock_analyst_expert_agent,
    get_market_analyst_expert_agent,
    get_portfolio_manager_agent,
)
from services.user_context import MongoDBUserContextService
from services.agent_service import InvestmentManagerMultiAgentService
from models.session import Message, MessageRole

# Define a response format for the test
class TestResponse(BaseModel):
    response: str = Field(description="The response from the agent")


async def test_investment_manager_actual_behavior():
    print("Setting up actual test for InvestmentManagerMultiAgentService...")

    # 1. Initialize MongoDB Client and Service
    print(f"Connecting to MongoDB at {settings.MONGO_URI}...")
    mongo_client = AsyncMongoClient(settings.MONGO_URI)
    user_context_service = MongoDBUserContextService(mongo_client=mongo_client)

    try:
        # 2. Get Real MCP Client
        print("Initializing MCP client...")
        mcp_client = get_mcp_client()

        # 3. Instantiate the service with REAL dependencies
        service = InvestmentManagerMultiAgentService(
            #mcp_client=mcp_client,
            user_context_service=user_context_service,
            etf_expert_agent=await get_etf_expert_agent(mcp_client=mcp_client),
            crypto_expert_agent=await get_crypto_expert_agent(mcp_client=mcp_client),
            stock_analyst_expert_agent=await get_stock_analyst_expert_agent(mcp_client=mcp_client),
            market_analyst_expert_agent=await get_market_analyst_expert_agent(mcp_client=mcp_client),
            portfolio_manager_agent=await get_portfolio_manager_agent(mcp_client=mcp_client),
        )

        # 4. Prepare test data
        user_id = "test_user_actual"
        conversation = [
            Message(role=MessageRole.USER, content="What are the latest market news?")
        ]

        response = await service.generate_response(
            user_id=user_id,
            conversation=conversation,
            response_format=TestResponse
        )

        print("\n--- ACTUAL AGENT RESPONSE ---")
        print(response)
        print("-----------------------------")

    except Exception as e:
        print(f"\nCaught an error during execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nClosing MongoDB client...")
        await mongo_client.close()

if __name__ == "__main__":
    if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY and not settings.GOOGLE_API_KEY:
        print("ERROR: No API keys found in settings. Please check your .env file.")
        sys.exit(1)
        
    asyncio.run(test_investment_manager_actual_behavior())
