import asyncio
import datetime as dt

from models.user_context import (
    UserConversationNote,
    UserProfileNote,
)
from repos.user_conversation_notes import UserConversationNotesTable
from repos.user_profile_notes import UserProfileNotesTable


class UserConversationNotesService:
    def __init__(self, table: UserConversationNotesTable):
        self.table = table

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
        return UserConversationNote(
            id=row.id,
            date=row.date,
            note=row.note,
            created_at=row.created_at,
        )


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

