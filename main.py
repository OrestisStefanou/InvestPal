import logging
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import AsyncMongoClient

from apps.rest_api import (
    session,
    user_context,
    chat,
    agent_reminders,
)
from config import settings


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.mongodb_client = AsyncMongoClient(settings.MONGO_URI)
    yield
    # Shutdown
    await app.state.mongodb_client.close()


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Try to get request body for better debugging of 500s
    try:
        body = await request.body()
        body_str = body.decode('utf-8', errors='replace')[:1000]
    except:
        body_str = "Could not read body"

    logger.exception(
        "Unhandled exception occurred while processing request: %s %s\nRequest Body: %s", 
        request.method, 
        request.url, 
        body_str
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


app.include_router(session.router)
app.include_router(user_context.router)
app.include_router(chat.router)
app.include_router(agent_reminders.router)
