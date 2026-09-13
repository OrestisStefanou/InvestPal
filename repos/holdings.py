import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from config import settings
from repos.db import connect, first_row


@dataclass
class HoldingRow:
    id: str
    name: str
    kind: str
    ticker: str | None
    quantity: float | None
    cost_basis: float | None
    amount: float | None
    currency: str | None
    custodian: str | None
    source: str
    as_of: str
    detail: str | None
    created_at: str
    updated_at: str
    closed_at: str | None


_HOLDING_COLUMNS = (
    "id, name, kind, ticker, quantity, cost_basis, amount, currency, custodian, "
    "source, as_of, detail, created_at, updated_at, closed_at"
)

# Everything the caller may set. `id`, `created_at` and `updated_at` are owned by
# this table; `closed_at` moves only through close()/reopen().
_WRITABLE_COLUMNS = (
    "name",
    "kind",
    "ticker",
    "quantity",
    "cost_basis",
    "amount",
    "currency",
    "custodian",
    "source",
    "as_of",
    "detail",
)


def _to_holding_row(row) -> HoldingRow:
    return HoldingRow(
        id=row[0],
        name=row[1],
        kind=row[2],
        ticker=row[3],
        quantity=row[4],
        cost_basis=row[5],
        amount=row[6],
        currency=row[7],
        custodian=row[8],
        source=row[9],
        as_of=row[10],
        detail=row[11],
        created_at=row[12],
        updated_at=row[13],
        closed_at=row[14],
    )


class HoldingsTable:
    """What the client owns, from a broker or recorded by hand.

    Identity is (name, custodian), not the surrogate id: a refresh of the same
    position must update the existing row rather than append a second one, which
    is what `find_open` and `upsert` are for.
    """

    def __init__(self, db_path: str = settings.TURSO_DB_PATH):
        self._db_path = db_path
        self._table_name = "holdings"

    def get_holdings(self, include_closed: bool = False) -> list[HoldingRow]:
        query = f"SELECT {_HOLDING_COLUMNS} FROM {self._table_name}"
        if not include_closed:
            query += " WHERE closed_at IS NULL"
        query += " ORDER BY custodian, name"

        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        return [_to_holding_row(row) for row in rows]

    def get_holding(self, holding_id: str) -> HoldingRow | None:
        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT {_HOLDING_COLUMNS} FROM {self._table_name} WHERE id = ?",
                (holding_id,),
            )
            rows = cursor.fetchall()

        return _to_holding_row(rows[0]) if rows else None

    def find_open(self, name: str, custodian: str | None) -> HoldingRow | None:
        """The open row for this position, if one exists.

        `custodian IS ?` rather than `= ?` so a holding recorded without a
        custodian still matches itself on the next refresh.
        """
        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT {_HOLDING_COLUMNS} FROM {self._table_name} "
                "WHERE name = ? AND custodian IS ? AND closed_at IS NULL",
                (name, custodian),
            )
            rows = cursor.fetchall()

        return _to_holding_row(rows[0]) if rows else None

    def upsert(self, **fields) -> HoldingRow:
        """Create the position, or update the open row that already holds it.

        Only the fields passed are written, so a refresh that knows the new
        quantity but not the cost basis does not blank the cost basis.
        """
        unknown = set(fields) - set(_WRITABLE_COLUMNS)
        if unknown:
            raise ValueError(f"Unknown holding columns: {sorted(unknown)}")

        existing = self.find_open(fields["name"], fields.get("custodian"))
        now = datetime.now(timezone.utc).isoformat()

        if existing is None:
            # NOT NULL in schema.sql. Caught here rather than as an opaque
            # integrity error, and `as_of` in particular is the column the whole
            # freshness contract rests on.
            missing = [
                column
                for column in ("name", "kind", "source", "as_of")
                if not fields.get(column)
            ]
            if missing:
                raise ValueError(
                    f"Creating a holding requires {', '.join(missing)}"
                )
            values = {column: fields.get(column) for column in _WRITABLE_COLUMNS}
            holding_id = str(uuid.uuid4())
            with connect(self._db_path) as conn:
                conn.execute(
                    f"INSERT INTO {self._table_name} "
                    f"(id, {', '.join(_WRITABLE_COLUMNS)}, created_at, updated_at, closed_at) "
                    f"VALUES (?, {', '.join('?' * len(_WRITABLE_COLUMNS))}, ?, ?, NULL)",
                    (
                        holding_id,
                        *(values[column] for column in _WRITABLE_COLUMNS),
                        now,
                        now,
                    ),
                )
            return HoldingRow(
                id=holding_id,
                name=str(fields["name"]),
                kind=str(fields["kind"]),
                ticker=values["ticker"],
                quantity=values["quantity"],
                cost_basis=values["cost_basis"],
                amount=values["amount"],
                currency=values["currency"],
                custodian=values["custodian"],
                source=str(fields["source"]),
                as_of=str(fields["as_of"]),
                detail=values["detail"],
                created_at=now,
                updated_at=now,
                closed_at=None,
            )

        assignments = [f"{column} = ?" for column in fields]
        params = list(fields.values())
        with connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {self._table_name} SET {', '.join(assignments)}, updated_at = ? "
                f"WHERE id = ? RETURNING {_HOLDING_COLUMNS}",
                (*params, now, existing.id),
            )
            row = first_row(cursor)

        return _to_holding_row(row)

    def close(self, holding_id: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        with connect(self._db_path) as conn:
            cursor = conn.execute(
                f"UPDATE {self._table_name} SET closed_at = ?, updated_at = ? "
                "WHERE id = ? AND closed_at IS NULL",
                (now, now, holding_id),
            )
            return cursor.rowcount > 0
