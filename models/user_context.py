from pydantic import BaseModel

class UserPortfolioHolding(BaseModel):
    asset_class: str
    symbol: str
    name: str
    quantity: float

class UserContext(BaseModel):
    user_id: str
    user_profile: dict
    user_portfolio: list[UserPortfolioHolding]
    created_at: str | None = None
    updated_at: str | None = None