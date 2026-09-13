from enum import Enum

from pydantic import BaseModel, Field


class HoldingKind(str, Enum):
    CASH = "cash"
    FIXED_INCOME = "fixed_income"
    EQUITY = "equity"
    ETF = "etf"
    CRYPTO = "crypto"
    PRIVATE_EQUITY = "private_equity"
    OTHER = "other"


class HoldingSource(str, Enum):
    """Where the numbers came from, which decides how far to trust them.

    Anything other than MANUAL is a cache of a broker's own record: refresh it
    from that broker whenever the broker is reachable, and quote it only with its
    `as_of` date when it is not.
    """

    MANUAL = "manual"
    INTERACTIVE_BROKERS = "interactive_brokers"
    COINBASE = "coinbase"
    ALPACA = "alpaca"


class Holding(BaseModel):
    holding_id: str = Field(description="Unique id of the holding")
    name: str = Field(
        description=(
            "What the position is, e.g. 'NVDA', 'Bank cash', 'Sophic EU 3M T-bill'. "
            "Together with the custodian this identifies the position: writing the "
            "same name and custodian again updates this row rather than adding one."
        )
    )
    kind: HoldingKind = Field(description="The asset class of the holding")
    ticker: str | None = Field(
        default=None, description="Exchange ticker, when the holding has one"
    )
    quantity: float | None = Field(
        default=None, description="Shares or units held"
    )
    cost_basis: float | None = Field(
        default=None, description="Average cost per unit, in `currency`"
    )
    amount: float | None = Field(
        default=None,
        description=(
            "Total value, for holdings with no meaningful unit price such as cash "
            "balances or the face value of a bill. Leave unset when quantity and "
            "cost_basis carry the information, and never store a market value here "
            "that a price lookup would give you."
        ),
    )
    currency: str | None = Field(default=None, description="ISO currency code")
    custodian: str | None = Field(
        default=None,
        description=(
            "Who holds it: 'Interactive Brokers', 'Coinbase', 'Sophic', 'Bank', "
            "'Carta'. Part of the holding's identity."
        ),
    )
    source: HoldingSource = Field(
        description=(
            "Where the figures came from. Use the broker's own value when you read "
            "them from that broker's tools, and 'manual' when the client told you."
        )
    )
    as_of: str | None = Field(
        default=None,
        description=(
            "YYYY-MM-DD: the date these figures were true. There is no 'current' "
            "value here, only a value as of a date, so never quote this holding "
            "without saying when it was accurate."
        ),
    )
    detail: str | None = Field(
        default=None,
        description=(
            "Free text for facts the columns do not carry: interest rate, maturity "
            "date, vesting schedule, strike price. Not for theses or price targets, "
            "which belong in the ticker record."
        ),
    )
    created_at: str = Field(description="ISO 8601 creation timestamp")
    updated_at: str = Field(description="ISO 8601 timestamp of the last write")
    closed_at: str | None = Field(
        default=None,
        description="ISO 8601 timestamp when the position was closed, if it was",
    )
