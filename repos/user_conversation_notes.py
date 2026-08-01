import uuid
from dataclasses import dataclass
from datetime import datetime

from config import settings
from repos.db import connect


@dataclass
class UserConversationNoteRow:
    id: str
    date: str
    note: str
    created_at: str


@dataclass
class ConversationNoteSearchRow:
    id: str
    date: str
    note: str
    created_at: str
    distance: float


class UserConversationNotesTable:
    def __init__(self, db_path: str = settings.TURSO_DB_PATH):
        self._db_path = db_path
        self._table_name = "user_conversation_notes"
        self._embeddings_table_name = "user_conversation_note_embeddings"

    def create_note(self, date: str, note: str) -> UserConversationNoteRow:
        note_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        with connect(self._db_path) as conn:
            conn.execute(
                f"INSERT INTO {self._table_name} (id, date, note, created_at) VALUES (?, ?, ?, ?)",
                (note_id, date, note, created_at),
            )

        return UserConversationNoteRow(
            id=note_id, date=date, note=note, created_at=created_at
        )

    def get_notes(self, limit: int | None = None) -> list[UserConversationNoteRow]:
        query = (
            f"SELECT id, date, note, created_at FROM {self._table_name} "
            "ORDER BY date DESC, created_at DESC"
        )
        params: tuple = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)

        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        return [
            UserConversationNoteRow(
                id=row[0], date=row[1], note=row[2], created_at=row[3]
            )
            for row in rows
        ]

    def upsert_embedding(self, note_id: str, vector_json: str, model: str) -> None:
        """Store or replace the embedding for a note.

        `vector_json` is the vector in `[0.1,0.2,...]` form; Turso's `vector32()`
        parses it into the F32_BLOB representation.

        Deliberately no RETURNING clause: turso leaves such a statement
        un-finalized and the next commit on the connection then fails with
        "database is locked" (see repos/db.py:first_row).
        """
        with connect(self._db_path) as conn:
            conn.execute(
                f"INSERT INTO {self._embeddings_table_name} "
                "(note_id, embedding, model, created_at) "
                "VALUES (?, vector32(?), ?, ?) "
                "ON CONFLICT(note_id) DO UPDATE SET "
                "embedding = excluded.embedding, "
                "model = excluded.model, "
                "created_at = excluded.created_at",
                (note_id, vector_json, model, datetime.now().isoformat()),
            )

    def search_by_embedding(
        self,
        query_json: str,
        model: str,
        blob_bytes: int,
        limit: int,
    ) -> list[ConversationNoteSearchRow]:
        """Return notes ordered by cosine distance to the query vector, nearest first.

        A brute-force scan: the installed turso build has no ANN index
        (`libsql_vector_idx` / `vector_top_k` do not exist), which is fine at
        this table's scale.

        The `model` and `length` predicates are load-bearing rather than
        defensive. `vector_distance_cos` raises on a dimension mismatch and the
        error aborts the whole statement, so a single row written by a
        different-dimension model would otherwise break every search until it
        was deleted.
        """
        query = (
            "SELECT n.id, n.date, n.note, n.created_at, "
            "vector_distance_cos(e.embedding, vector32(?)) AS distance "
            f"FROM {self._table_name} n "
            f"JOIN {self._embeddings_table_name} e ON e.note_id = n.id "
            "WHERE e.model = ? AND length(e.embedding) = ? "
            "ORDER BY distance ASC "
            "LIMIT ?"
        )

        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (query_json, model, blob_bytes, limit))
            rows = cursor.fetchall()

        return [
            ConversationNoteSearchRow(
                id=row[0], date=row[1], note=row[2], created_at=row[3], distance=row[4]
            )
            for row in rows
        ]

    def get_notes_missing_embedding(self, model: str) -> list[UserConversationNoteRow]:
        """Notes with no embedding, or one written by a different model."""
        query = (
            "SELECT n.id, n.date, n.note, n.created_at "
            f"FROM {self._table_name} n "
            f"LEFT JOIN {self._embeddings_table_name} e ON e.note_id = n.id "
            "WHERE e.note_id IS NULL OR e.model != ? "
            "ORDER BY n.created_at ASC"
        )

        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (model,))
            rows = cursor.fetchall()

        return [
            UserConversationNoteRow(
                id=row[0], date=row[1], note=row[2], created_at=row[3]
            )
            for row in rows
        ]
