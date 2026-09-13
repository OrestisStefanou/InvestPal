from enum import Enum

from pydantic import BaseModel, Field


class TickerStatus(str, Enum):
    WATCHING = "watching"
    HELD = "held"
    EXITED = "exited"
    REJECTED = "rejected"


class TickerRecord(BaseModel):
    ticker: str = Field(
        description="Exchange ticker, e.g. 'LHX', 'ENR.DE', '7011.T'. The record's id."
    )
    status: TickerStatus = Field(
        description=(
            "'watching' for a name on the watchlist, 'held' once a position exists, "
            "'exited' once it is sold, 'rejected' for a name screened and turned down. "
            "Move the status rather than deleting and re-adding: the thesis and the "
            "reason it was rejected are worth keeping."
        )
    )
    thesis: str | None = Field(
        default=None,
        description=(
            "Why this name is interesting, in a few sentences: the business, the "
            "structural case, and what makes it different from what is already owned."
        ),
    )
    entry_trigger: str | None = Field(
        default=None,
        description=(
            "The condition that would make this a buy, stated so it can be checked "
            "against live data, e.g. 'limit $238,22 or below'. Overwrite it when the "
            "level moves; the reasoning behind the change belongs in a conversation note."
        ),
    )
    falsifier: str | None = Field(
        default=None,
        description=(
            "What would prove the thesis wrong and take this off the list, e.g. "
            "'two consecutive quarters of negative revenue growth'."
        ),
    )
    notes: str | None = Field(
        default=None,
        description=(
            "Anything else durable about the name that the other fields do not hold, "
            "such as why a position was sized small or how it overlaps existing holdings."
        ),
    )
    created_at: str = Field(description="ISO 8601 creation timestamp")
    updated_at: str = Field(description="ISO 8601 timestamp of the last write")
