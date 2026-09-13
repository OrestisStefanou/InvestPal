import asyncio
import logging

from models.ticker_records import TickerRecord
from repos.ticker_records import TickerRecordRow, TickerRecordsTable


logger = logging.getLogger(__name__)


def _to_model(row: TickerRecordRow) -> TickerRecord:
    return TickerRecord(
        ticker=row.ticker,
        status=row.status,  # type: ignore[arg-type]
        thesis=row.thesis,
        entry_trigger=row.entry_trigger,
        falsifier=row.falsifier,
        notes=row.notes,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class TickerRecordsService:
    """Why a name is interesting and what would make us act on it."""

    def __init__(self, table: TickerRecordsTable):
        self.table = table

    async def get_ticker_records(self, status: str | None = None) -> list[TickerRecord]:
        rows = await asyncio.to_thread(self.table.get_ticker_records, status)
        return [_to_model(row) for row in rows]

    async def get_ticker_record(self, ticker: str) -> TickerRecord | None:
        row = await asyncio.to_thread(self.table.get_ticker_record, ticker)
        return _to_model(row) if row else None

    async def upsert_ticker_record(
        self,
        ticker: str,
        status: str | None = None,
        thesis: str | None = None,
        entry_trigger: str | None = None,
        falsifier: str | None = None,
        notes: str | None = None,
    ) -> TickerRecord:
        """Create the record, or update the fields passed on the existing one.

        Only the arguments actually passed are written, so moving a name to
        `held` does not wipe the thesis recorded when it was added.

        Raises:
            ValueError: if `status` is missing when creating a new record.
        """
        fields = {
            "status": status,
            "thesis": thesis,
            "entry_trigger": entry_trigger,
            "falsifier": falsifier,
            "notes": notes,
        }
        fields = {key: value for key, value in fields.items() if value is not None}

        row = await asyncio.to_thread(self.table.upsert, ticker, **fields)
        return _to_model(row)

    async def delete_ticker_record(self, ticker: str) -> bool:
        return await asyncio.to_thread(self.table.delete, ticker)
