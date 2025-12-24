from fastapi import (
    Request,
    HTTPException,
)
from langchain_mcp_adapters.client import MultiServerMCPClient
from config import settings

def get_db_client(request: Request):
    if not hasattr(request.app.state, "mongodb_client"):
        raise HTTPException(status_code=500, detail="Database not initialized")
    return request.app.state.mongodb_client

def get_mcp_client():
    mcp_server_client = MultiServerMCPClient(
        {
            settings.MCP_SERVER_NAME: {
                "transport": "streamable_http",  # HTTP-based remote server
                "url": settings.MCP_SERVER_URL,
            }
        }
    )    
    return mcp_server_client
