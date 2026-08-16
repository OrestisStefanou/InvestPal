import asyncio
import datetime as dt
import logging

from models.user_context import (
    UserConversationNote,
    UserConversationNoteSearchResult,
    UserProfileNote,
)
from repos.user_conversation_note_embeddings import (
    UserConversationNoteEmbeddingsTable,
)
from repos.user_conversation_notes import UserConversationNotesTable
from repos.user_profile_notes import UserProfileNotesTable


logger = logging.getLogger(__name__)


class UserConversationNotesService:
    def __init__(
        self,
        table: UserConversationNotesTable,
        embeddings_table: UserConversationNoteEmbeddingsTable | None = None,
    ):
        self.table = table
        self.embeddings_table = embeddings_table

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
        if self.embeddings_table is None:
            return

        try:
            await asyncio.to_thread(self.embeddings_table.store, note_id, note)
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
                nothing. Filtering happens here rather than in the index
                because relevance is a policy question, not a storage one.

        Returns:
            Matching notes, most similar first, each carrying its similarity.
        """
        if self.embeddings_table is None:
            logger.warning(
                "Conversation note search called while embeddings are disabled; "
                "returning no results"
            )
            return []

        # The index ranks note ids; the notes themselves come from their own
        # table, so neither repo has to reach into the other's.
        hits = await asyncio.to_thread(self.embeddings_table.search, query, limit)
        if not hits:
            return []

        distance_by_id = dict(hits)
        rows = await asyncio.to_thread(
            self.table.get_notes_by_ids, list(distance_by_id)
        )

        results = [
            UserConversationNoteSearchResult(
                id=row.id,
                date=row.date,
                note=row.note,
                created_at=row.created_at,
                # The model emits L2-normalised vectors, so cosine distance and
                # cosine similarity are exact complements.
                similarity=1.0 - distance_by_id[row.id],
            )
            for row in rows
        ]
        # get_notes_by_ids does not preserve order, so restore the ranking.
        results.sort(key=lambda r: r.similarity, reverse=True)

        if min_similarity is not None:
            results = [r for r in results if r.similarity >= min_similarity]

        return results

    async def backfill_embeddings(self, batch_size: int = 32) -> int:
        """
        Embed every note that has no vector, or whose vector is from another model.

        Returns:
            The number of notes embedded.
        """
        if self.embeddings_table is None:
            raise RuntimeError(
                "Cannot backfill embeddings while EMBEDDING_ENABLED is false."
            )

        notes = await asyncio.to_thread(self.table.get_notes)
        embedded_ids = await asyncio.to_thread(
            self.embeddings_table.get_embedded_note_ids
        )
        pending = [(row.id, row.note) for row in notes if row.id not in embedded_ids]

        for start in range(0, len(pending), batch_size):
            await asyncio.to_thread(
                self.embeddings_table.store_many, pending[start : start + batch_size]
            )

        return len(pending)


class UserProfileService:
    def __init__(self, table: UserProfileNotesTable):
        self.table = table

    async def create_user_profile_note(self, note: str) -> UserProfileNote:
        row = await asyncio.to_thread(self.table.create_user_profile_note, note)
        return UserProfileNote(
            id=row.id,
            note=row.note,
            created_at=row.created_at.isoformat()
        )

    async def get_user_profile_notes(self) -> list[UserProfileNote]:
        rows = await asyncio.to_thread(self.table.get_user_profile_notes, False)
        return [
            UserProfileNote(
                id=row.id,
                note=row.note,
                created_at=row.created_at.isoformat()
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

