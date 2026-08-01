from datetime import datetime

from config import settings
from repos.db import connect
from repos.embeddings import (
    EMBEDDING_BLOB_BYTES,
    FastEmbedEmbedder,
    to_vector_json,
)


class UserConversationNoteEmbeddingsTable:
    """Semantic index over the notes in `user_conversation_notes`.

    Owns exactly one table. Turning text into a vector is how this table is
    addressed, so the embedder lives here and callers only ever deal in
    strings: nothing above this class needs to know that a vector is JSON on
    the way in or 1536 bytes at rest.

    Lookups return note ids, not notes. Reading the note text is
    `UserConversationNotesTable`'s job.
    """

    def __init__(
        self,
        db_path: str = settings.TURSO_DB_PATH,
        embedder: FastEmbedEmbedder | None = None,
    ):
        self._db_path = db_path
        self._table_name = "user_conversation_note_embeddings"
        # Injected, never constructed here. Repo classes are rebuilt on every
        # request, while the embedder holds a 64MB ONNX model that has to be
        # process-wide. None means embeddings are disabled.
        self._embedder = embedder

    @property
    def enabled(self) -> bool:
        return self._embedder is not None

    def store_many(self, notes: list[tuple[str, str]]) -> int:
        """Embed and store `(note_id, text)` pairs, replacing any existing vector.

        Returns the number stored, or 0 when embeddings are disabled.
        """
        if self._embedder is None or not notes:
            return 0

        # Embedded before opening the connection, never inside it: `connect`
        # holds the database lock for the whole block, and inference is slow
        # enough to stall the other process.
        vectors = self._embedder.embed_documents([text for _, text in notes])
        model = self._embedder.model_name
        created_at = datetime.now().isoformat()

        with connect(self._db_path) as conn:
            for (note_id, _), vector in zip(notes, vectors):
                # No RETURNING clause: turso leaves such a statement
                # un-finalized and the next commit then fails with
                # "database is locked" (see repos/db.py:first_row).
                conn.execute(
                    f"INSERT INTO {self._table_name} "
                    "(note_id, embedding, model, created_at) "
                    "VALUES (?, vector32(?), ?, ?) "
                    "ON CONFLICT(note_id) DO UPDATE SET "
                    "embedding = excluded.embedding, "
                    "model = excluded.model, "
                    "created_at = excluded.created_at",
                    (note_id, to_vector_json(vector), model, created_at),
                )

        return len(notes)

    def store(self, note_id: str, text: str) -> int:
        return self.store_many([(note_id, text)])

    def search(self, query: str, limit: int) -> list[tuple[str, float]]:
        """Return `(note_id, cosine distance)` for the nearest notes, closest first.

        A brute-force scan: this turso build has no ANN index
        (`libsql_vector_idx` and `vector_top_k` do not exist), which is fine at
        the scale conversation notes reach.

        The `model` and `length` predicates are load-bearing rather than
        defensive. `vector_distance_cos` raises on a dimension mismatch and
        that error aborts the whole statement, so one row written by a
        different-dimension model would otherwise break every search until it
        was deleted.
        """
        if self._embedder is None:
            return []

        query_vector = to_vector_json(self._embedder.embed_query(query))

        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT note_id, vector_distance_cos(embedding, vector32(?)) AS distance "
                f"FROM {self._table_name} "
                "WHERE model = ? AND length(embedding) = ? "
                "ORDER BY distance ASC "
                "LIMIT ?",
                (
                    query_vector,
                    self._embedder.model_name,
                    EMBEDDING_BLOB_BYTES,
                    limit,
                ),
            )
            rows = cursor.fetchall()

        return [(row[0], row[1]) for row in rows]

    def get_embedded_note_ids(self) -> set[str]:
        """Ids holding a usable vector from the current model.

        Rows left by a previous model are excluded, so changing the model makes
        every note show up as needing a backfill. The length predicate matches
        the one in `search`: a row search cannot use is a row the backfill
        should replace, otherwise a bad vector stays invisible forever.
        """
        if self._embedder is None:
            return set()

        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT note_id FROM {self._table_name} "
                "WHERE model = ? AND length(embedding) = ?",
                (self._embedder.model_name, EMBEDDING_BLOB_BYTES),
            )
            rows = cursor.fetchall()

        return {row[0] for row in rows}
