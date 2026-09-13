from dataclasses import dataclass
from datetime import datetime, timezone

from config import settings
from repos.db import connect, first_row


@dataclass
class TickerRecordRow:
    ticker: str
    status: str
    thesis: str | None
    entry_trigger: str | None
    falsifier: str | None
    notes: str | None
    created_at: str
    updated_at: str


_TICKER_RECORD_COLUMNS = (
    "ticker, status, thesis, entry_trigger, falsifier, notes, created_at, updated_at"
)

_WRITABLE_COLUMNS = ("status", "thesis", "entry_trigger", "falsifier", "notes")


def _to_ticker_record_row(row) -> TickerRecordRow:
    return TickerRecordRow(
        ticker=row[0],
        status=row[1],
        thesis=row[2],
        entry_trigger=row[3],
        falsifier=row[4],
        notes=row[5],
        created_at=row[6],
        updated_at=row[7],
    )


class TickerRecordsTable:
    """Why a name is interesting and what would make us act on it.

    Keyed by ticker and updated in place: a trigger reset edits the row, it does
    not add a second one.
    """

    def __init__(self, db_path: str = settings.TURSO_DB_PATH):
        self._db_path = db_path
        self._table_name = "ticker_records"

    def get_ticker_records(self, status: str | None = None) -> list[TickerRecordRow]:
        query = f"SELECT {_TICKER_RECORD_COLUMNS} FROM {self._table_name}"
        params: tuple = ()
        if status is not None:
            query += " WHERE status = ?"
            params = (status,)
        query += " ORDER BY ticker"

        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        return [_to_ticker_record_row(row) for row in rows]

    def get_ticker_record(self, ticker: str) -> TickerRecordRow | None:
        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT {_TICKER_RECORD_COLUMNS} FROM {self._table_name} WHERE ticker = ?",
                (ticker,),
            )
            rows = cursor.fetchall()

        return _to_ticker_record_row(rows[0]) if rows else None

    def upsert(self, ticker: str, **fields) -> TickerRecordRow:
        """Create the record, or update the fields passed on the existing one.

        Only the fields passed are written, so updating a status does not wipe
        the thesis recorded weeks earlier.
        """
        unknown = set(fields) - set(_WRITABLE_COLUMNS)
        if unknown:
            raise ValueError(f"Unknown ticker record columns: {sorted(unknown)}")

        existing = self.get_ticker_record(ticker)
        now = datetime.now(timezone.utc).isoformat()

        if existing is None:
            # status is NOT NULL in schema.sql. Caught here rather than as an
            # opaque integrity error.
            status = fields.get("status")
            if not status:
                raise ValueError("status is required when creating a ticker record")
            values = {column: fields.get(column) for column in _WRITABLE_COLUMNS}
            with connect(self._db_path) as conn:
                conn.execute(
                    f"INSERT INTO {self._table_name} "
                    f"(ticker, {', '.join(_WRITABLE_COLUMNS)}, created_at, updated_at) "
                    f"VALUES (?, {', '.join('?' * len(_WRITABLE_COLUMNS))}, ?, ?)",
                    (
                        ticker,
                        *(values[column] for column in _WRITABLE_COLUMNS),
                        now,
                        now,
                    ),
                )
            return TickerRecordRow(
                ticker=ticker,
                status=status,
                thesis=values["thesis"],
                entry_trigger=values["entry_trigger"],
                falsifier=values["falsifier"],
                notes=values["notes"],
                created_at=now,
                updated_at=now,
            )

        assignments = [f"{column} = ?" for column in fields]
        params = list(fields.values())
        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {self._table_name} SET {', '.join(assignments)}, updated_at = ? "
                f"WHERE ticker = ? RETURNING {_TICKER_RECORD_COLUMNS}",
                (*params, now, ticker),
            )
            row = first_row(cursor)

        return _to_ticker_record_row(row)

    def delete(self, ticker: str) -> bool:
        with connect(self._db_path) as conn:
            cursor = conn.execute(
                f"DELETE FROM {self._table_name} WHERE ticker = ?", (ticker,)
            )
            return cursor.rowcount > 0
