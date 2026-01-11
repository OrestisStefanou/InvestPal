import http

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException
)
from pydantic import BaseModel
from pymongo import AsyncMongoClient

from services.user_context import (
    MongoDBUserContextService,
)
from dependencies import get_db_client
from errors.user_context import (
    UserContextAlreadyExistsError,
    UserContextNotFoundError,
)
from models.user_context import (
    UserContext,
    UserPortfolioHolding,
)
router = APIRouter()

class UserPortfolioHoldingSchema(BaseModel):
    asset_class: str
    symbol: str
    name: str
    quantity: float


class UserContextSchema(BaseModel):
    user_id: str
    user_profile: dict | None = None
    user_portfolio: list[UserPortfolioHoldingSchema] | None = None


class UserContextResponseSchema(UserContextSchema):
    created_at: str | None
    updated_at: str | None


@router.post("/user_context", response_model=UserContextResponseSchema, status_code=http.HTTPStatus.CREATED)
async def create_user_context(request: UserContextSchema, db_client: AsyncMongoClient = Depends(get_db_client)):
    user_context_service = MongoDBUserContextService(
        mongo_client=db_client,
    )

    # Convert UserContextSchema to UserContext
    user_context = UserContext(
        user_id=request.user_id,
        user_profile=request.user_profile or {},
        user_portfolio=[
            UserPortfolioHolding(
                asset_class=holding.asset_class,
                symbol=holding.symbol,
                name=holding.name,
                quantity=holding.quantity,
            ) for holding in request.user_portfolio or []
        ],
    )

    try:
        created_user_context = await user_context_service.create_user_context(
            user_id=user_context.user_id,
            user_profile=user_context.user_profile,
            user_portfolio=user_context.user_portfolio,
        )
    except UserContextAlreadyExistsError as e:
        raise HTTPException(status_code=http.HTTPStatus.CONFLICT, detail=str(e))
    
    return UserContextResponseSchema(
        user_id=created_user_context.user_id,
        user_profile=created_user_context.user_profile,
        user_portfolio=[UserPortfolioHoldingSchema(
            asset_class=holding.asset_class,
            symbol=holding.symbol,
            name=holding.name,
            quantity=holding.quantity,
        ) for holding in created_user_context.user_portfolio],
        created_at=created_user_context.created_at,
        updated_at=created_user_context.updated_at,
    )

@router.get("/user_context/{user_id}", response_model=UserContextResponseSchema)
async def get_user_context(user_id: str, db_client: AsyncMongoClient = Depends(get_db_client)):
    user_context_service = MongoDBUserContextService(
        mongo_client=db_client,
    )
    user_context = await user_context_service.get_user_context(user_id)
    
    if not user_context:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="User context not found")

    return UserContextResponseSchema(
        user_id=user_context.user_id,
        user_profile=user_context.user_profile,
        user_portfolio=[UserPortfolioHoldingSchema(
            asset_class=holding.asset_class,
            symbol=holding.symbol,
            name=holding.name,
            quantity=holding.quantity,
        ) for holding in user_context.user_portfolio],
        created_at=user_context.created_at,
        updated_at=user_context.updated_at,
    )

@router.put("/user_context", response_model=UserContextResponseSchema)
async def update_user_context(request: UserContextSchema, db_client: AsyncMongoClient = Depends(get_db_client)):
    user_context_service = MongoDBUserContextService(
        mongo_client=db_client,
    )

    try:
        user_context = await user_context_service.update_user_context(
            user_id=request.user_id,
            user_context=UserContext(
                user_id=request.user_id,
                user_profile=request.user_profile,
                user_portfolio=[
                    UserPortfolioHolding(
                        asset_class=holding.asset_class,
                        symbol=holding.symbol,
                        name=holding.name,
                        quantity=holding.quantity,
                    ) for holding in request.user_portfolio or []
                ],
            ),
        )
    except UserContextNotFoundError as e:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=str(e))
    
    return UserContextResponseSchema(
        user_id=user_context.user_id,
        user_profile=user_context.user_profile,
        user_portfolio=[UserPortfolioHoldingSchema(
            asset_class=holding.asset_class,
            symbol=holding.symbol,
            name=holding.name,
            quantity=holding.quantity,
        ) for holding in user_context.user_portfolio],
        created_at=user_context.created_at,
        updated_at=user_context.updated_at,
    )
