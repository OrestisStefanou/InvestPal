import asyncio
import datetime as dt
import logging

from models.holdings import Holding
from repos.holdings import HoldingRow, HoldingsTable


logger = logging.getLogger(__name__)


def _to_model(row: HoldingRow) -> Holding:
    return Holding(
        holding_id=row.id,
        name=row.name,
        kind=row.kind,  # type: ignore[arg-type]
        ticker=row.ticker,
        quantity=row.quantity,
        cost_basis=row.cost_basis,
        amount=row.amount,
        currency=row.currency,
        custodian=row.custodian,
        source=row.source,  # type: ignore[arg-type]
        as_of=row.as_of,
        detail=row.detail,
        created_at=row.created_at,
        updated_at=row.updated_at,
        closed_at=row.closed_at,
    )


class HoldingsService:
    """What the client owns, from a broker or recorded by hand."""

    def __init__(self, table: HoldingsTable):
        self.table = table

    async def get_holdings(self, include_closed: bool = False) -> list[Holding]:
        rows = await asyncio.to_thread(self.table.get_holdings, include_closed)
        return [_to_model(row) for row in rows]

    async def upsert_holding(
        self,
        name: str,
        kind: str | None = None,
        ticker: str | None = None,
        quantity: float | None = None,
        cost_basis: float | None = None,
        amount: float | None = None,
        currency: str | None = None,
        custodian: str | None = None,
        source: str | None = None,
        as_of: str | None = None,
        detail: str | None = None,
    ) -> Holding:
        """Create the position, or update the open row that already holds it.

        Only the arguments actually passed are written, so refreshing a share
        count from a broker does not blank the cost basis recorded months ago.

        Raises:
            ValueError: if `as_of` is not YYYY-MM-DD, or if a field required to
                create a new holding is missing.
        """
        if as_of is not None:
            try:
                dt.datetime.strptime(as_of, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid as_of date: {as_of}. Expected YYYY-MM-DD.")

        fields = {
            "name": name,
            "kind": kind,
            "ticker": ticker,
            "quantity": quantity,
            "cost_basis": cost_basis,
            "amount": amount,
            "currency": currency,
            "custodian": custodian,
            "source": source,
            "as_of": as_of,
            "detail": detail,
        }
        # `name` always goes through so the repo can identify the row; everything
        # else is omitted when unset so a partial refresh stays partial.
        fields = {
            key: value
            for key, value in fields.items()
            if value is not None or key == "name"
        }
        # custodian is part of the holding's identity, so an explicit None has to
        # reach the repo rather than being dropped as "unset".
        fields.setdefault("custodian", custodian)

        row = await asyncio.to_thread(self.table.upsert, **fields)
        return _to_model(row)

    async def close_holding(self, holding_id: str) -> bool:
        return await asyncio.to_thread(self.table.close, holding_id)
