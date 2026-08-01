import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.rest_api import (
    session,
    chat,
    agent_reminders,
    agent_workflows,
)
from config import settings
from repos.db import init_db
from repos.embeddings import get_embedder


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def _warm_up_embedder():
    """Load the embedding model off the startup path.

    Kicked off as a background task rather than awaited: the first embed
    otherwise pays the model load (and, on a cold cache, the download) while a
    user is waiting on it.
    """
    embedder = get_embedder()
    if embedder is None:
        return
    try:
        await asyncio.to_thread(embedder.warm_up)
    except Exception:
        logger.warning("Failed to warm up the embedding model", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(settings.TURSO_DB_PATH)
    warm_up_task = asyncio.create_task(_warm_up_embedder())
    try:
        yield
    finally:
        warm_up_task.cancel()


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
app.include_router(chat.router)
app.include_router(agent_reminders.router)
app.include_router(agent_workflows.router)
