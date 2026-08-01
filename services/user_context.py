import asyncio
import datetime as dt
import logging

from models.user_context import (
    UserConversationNote,
    UserConversationNoteSearchResult,
    UserProfileNote,
)
from repos.user_conversation_notes import UserConversationNotesTable
from repos.user_profile_notes import UserProfileNotesTable
from services.embeddings import (
    EMBEDDING_BLOB_BYTES,
    FastEmbedEmbedder,
    to_vector_json,
)


logger = logging.getLogger(__name__)


class UserConversationNotesService:
    def __init__(
        self,
        table: UserConversationNotesTable,
        embedder: FastEmbedEmbedder | None = None,
    ):
        self.table = table
        self.embedder = embedder

    async def get_user_conversation_notes(
        self,
        limit: int | None = None,
    ) -> list[UserConversationNote]:
        """
        Get conversation notes ordered by most recent first.

        Args:
            limit: Maximum number of notes to return. If None, returns all notes.

        Returns:
            A list of UserConversationNote models ordered by date descending.
        """
        rows = await asyncio.to_thread(self.table.get_notes, limit)
        return [
            UserConversationNote(
                id=row.id,
                date=row.date,
                note=row.note,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def create_user_conversation_note(
        self,
        note: str,
        date: str | None = None,
    ) -> UserConversationNote:
        """
        Create a conversation note for the given date. A date can hold any
        number of notes.

        Args:
            note: The note to store for this date.
            date: The date string in YYYY-MM-DD format. Defaults to today.

        Raises:
            ValueError: If date is provided and is not in YYYY-MM-DD format.

        Returns:
            The created note.
        """
        if date is None:
            date = dt.date.today().isoformat()
        else:
            try:
                dt.datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD.")

        row = await asyncio.to_thread(self.table.create_note, date, note)
        await self._embed_note(row.id, row.note)
        return UserConversationNote(
            id=row.id,
            date=row.date,
            note=row.note,
            created_at=row.created_at,
        )

    async def _embed_note(self, note_id: str, note: str) -> None:
        """Attach an embedding to a note that has just been stored.

        Runs as a separate step rather than inside the note's transaction on
        purpose: losing a note because the embedding model failed would be far
        worse than the note being temporarily unsearchable. Anything skipped
        here is picked up by `backfill_embeddings`.
        """
        if self.embedder is None:
            return

        try:
            vectors = await asyncio.to_thread(self.embedder.embed_documents, [note])
            await asyncio.to_thread(
                self.table.upsert_embedding,
                note_id,
                to_vector_json(vectors[0]),
                self.embedder.model_name,
            )
        except Exception:
            logger.warning(
                "Failed to embed conversation note %s; it will be picked up by the "
                "next embeddings backfill",
                note_id,
                exc_info=True,
            )

    async def search_user_conversation_notes(
        self,
        query: str,
        limit: int = 5,
        min_similarity: float | None = None,
    ) -> list[UserConversationNoteSearchResult]:
        """
        Find conversation notes by meaning rather than by date.

        Args:
            query: Natural-language description of what to recall.
            limit: Maximum number of notes to return.
            min_similarity: Optional 0.0-1.0 floor. Left unset by default: the
                model packs same-domain short text into a narrow similarity
                band, so a fixed threshold tends to return either everything or
                nothing. Filtering happens here rather than in SQL because
                there is no vector index to short-circuit, so it saves no work
                in the database and relevance policy belongs in the service.

        Returns:
            Matching notes, most similar first, each carrying its similarity.
        """
        if self.embedder is None:
            logger.warning(
                "Conversation note search called while embeddings are disabled; "
                "returning no results"
            )
            return []

        query_vector = await asyncio.to_thread(self.embedder.embed_query, query)
        rows = await asyncio.to_thread(
            self.table.search_by_embedding,
            to_vector_json(query_vector),
            self.embedder.model_name,
            EMBEDDING_BLOB_BYTES,
            limit,
        )

        results = [
            UserConversationNoteSearchResult(
                id=row.id,
                date=row.date,
                note=row.note,
                created_at=row.created_at,
                # The model emits L2-normalised vectors, so cosine distance and
                # cosine similarity are exact complements.
                similarity=1.0 - row.distance,
            )
            for row in rows
        ]

        if min_similarity is not None:
            results = [r for r in results if r.similarity >= min_similarity]

        return results

    async def backfill_embeddings(self, batch_size: int = 32) -> int:
        """
        Embed every note that has no vector or was embedded by another model.

        Returns:
            The number of notes embedded.
        """
        if self.embedder is None:
            raise RuntimeError(
                "Cannot backfill embeddings while EMBEDDING_ENABLED is false."
            )

        model_name = self.embedder.model_name
        rows = await asyncio.to_thread(
            self.table.get_notes_missing_embedding, model_name
        )

        for start in range(0, len(rows), batch_size):
            batch = rows[start : start + batch_size]
            vectors = await asyncio.to_thread(
                self.embedder.embed_documents, [row.note for row in batch]
            )
            for row, vector in zip(batch, vectors):
                await asyncio.to_thread(
                    self.table.upsert_embedding,
                    row.id,
                    to_vector_json(vector),
                    model_name,
                )

        return len(rows)


class UserProfileService:
    def __init__(self, table: UserProfileNotesTable):
        self.table = table

    async def create_user_profile_note(self, note: str) -> UserProfileNote:
        row = await asyncio.to_thread(self.table.create_user_profile_note, note)
        return UserProfileNote(
            id=row.id,
            note=row.note,
            created_at=row.created_at
        )

    async def get_user_profile_notes(self) -> list[UserProfileNote]:
        rows = await asyncio.to_thread(self.table.get_user_profile_notes, False)
        return [
            UserProfileNote(
                id=row.id,
                note=row.note,
                created_at=row.created_at
            )
            for row in rows
        ]

    async def mark_note_as_outdated(self, note_id: str) -> None:
        await asyncio.to_thread(self.table.mark_as_outdated, note_id)

    async def get_client_profile(self) -> str:
        """
        Build the client profile that gets injected into the agent system prompts,
        from the notes that are not marked as outdated.

        Returns:
            The profile as a bullet list, or a placeholder line when nothing is
            recorded yet.
        """
        notes = await self.get_user_profile_notes()
        if not notes:
            return "No profile information recorded for this client yet."

        return "\n".join(f"- {note.note}" for note in notes)

