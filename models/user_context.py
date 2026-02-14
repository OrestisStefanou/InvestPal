from pydantic import BaseModel, Field


class UserPortfolioHolding(BaseModel):
    asset_class: str = Field(description="The category of the asset (e.g., Stock, Crypto, ETF)")
    symbol: str = Field(description="The ticker symbol or unique identifier for the asset")
    name: str = Field(description="The descriptive name of the asset")
    quantity: float = Field(description="The amount of the asset held in the portfolio (zero means not known/given)")


class UserContext(BaseModel):
    user_id: str = Field(description="The unique identifier for the user")
    user_profile: dict = Field(description="A dictionary containing user preferences and profile information")
    user_portfolio: list[UserPortfolioHolding] = Field(description="A list of the user's current holdings")
    created_at: str | None = Field(default=None, description="The ISO timestamp when the context was created")
    updated_at: str | None = Field(default=None, description="The ISO timestamp when the context was last updated")