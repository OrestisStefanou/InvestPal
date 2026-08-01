"""Embed conversation notes that have no vector, or one from another model.

Run this after changing `EMBEDDING_MODEL_NAME` (which is also when it matters
most: search filters on the model name, so notes carrying the old model's
vectors become invisible until they are re-embedded). It also picks up any note
whose embedding failed at write time, since note creation deliberately does not
fail when the model does.

    make backfill_embeddings
"""

import asyncio
import logging

from config import settings
from repos.db import init_db
from repos.embeddings import get_embedder
from repos.user_conversation_note_embeddings import (
    UserConversationNoteEmbeddingsTable,
)
from repos.user_conversation_notes import UserConversationNotesTable
from services.user_context import UserConversationNotesService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    init_db(settings.TURSO_DB_PATH)

    embedder = get_embedder()
    if embedder is None:
        raise SystemExit(
            "EMBEDDING_ENABLED is false, so there is nothing to backfill. "
            "Set it to true and re-run."
        )

    service = UserConversationNotesService(
        table=UserConversationNotesTable(db_path=settings.TURSO_DB_PATH),
        embeddings_table=UserConversationNoteEmbeddingsTable(
            db_path=settings.TURSO_DB_PATH, embedder=embedder
        ),
    )

    logger.info("Backfilling conversation note embeddings with %s", embedder.model_name)
    embedded = await service.backfill_embeddings()
    logger.info("Embedded %d note(s)", embedded)


if __name__ == "__main__":
    asyncio.run(main())
