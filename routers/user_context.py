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
    UserContext,
    UserPortfolioHolding,
    UserContextAlreadyExistsError,
    UserContextNotFoundError,
)
from dependencies import get_db_client

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
        userid=request.user_id,
        userprofile=request.user_profile or {},
        userportfolio=[UserPortfolioHolding(
            assetclass=holding.asset_class,
            symbol=holding.symbol,
            name=holding.name,
            quantity=holding.quantity,
        ) for holding in request.user_portfolio or []
        ],
    )

    try:
        created_user_context = await user_context_service.create_user_context(
            user_id=user_context.userid,
            user_profile=user_context.userprofile,
            user_portfolio=user_context.userportfolio,
        )
    except UserContextAlreadyExistsError as e:
        raise HTTPException(status_code=http.HTTPStatus.CONFLICT, detail=str(e))
    
    return UserContextResponseSchema(
        user_id=created_user_context.userid,
        user_profile=created_user_context.userprofile,
        user_portfolio=[UserPortfolioHoldingSchema(
            asset_class=holding.assetclass,
            symbol=holding.symbol,
            name=holding.name,
            quantity=holding.quantity,
        ) for holding in created_user_context.userportfolio],
        created_at=created_user_context.createdat,
        updated_at=created_user_context.updatedat,
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
        user_id=user_context.userid,
        user_profile=user_context.userprofile,
        user_portfolio=[UserPortfolioHoldingSchema(
            asset_class=holding.assetclass,
            symbol=holding.symbol,
            name=holding.name,
            quantity=holding.quantity,
        ) for holding in user_context.userportfolio],
        created_at=user_context.createdat,
        updated_at=user_context.updatedat,
    )

@router.put("/user_context", response_model=UserContextResponseSchema)
async def update_user_context(request: UserContextSchema, db_client: AsyncMongoClient = Depends(get_db_client)):
    user_context_service = MongoDBUserContextService(
        mongo_client=db_client,
    )

    if not request.user_portfolio:
        request.user_portfolio = []

    try:
        user_context = await user_context_service.update_user_context(
            user_id=request.user_id,
            user_context=UserContext(
                userid=request.user_id,
                userprofile=request.user_profile,
                userportfolio=[UserPortfolioHolding(
                    assetclass=holding.asset_class,
                    symbol=holding.symbol,
                    name=holding.name,
                    quantity=holding.quantity,
                ) for holding in request.user_portfolio],
            ),
        )
    except UserContextNotFoundError as e:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=str(e))
    
    return UserContextResponseSchema(
        user_id=user_context.userid,
        user_profile=user_context.userprofile,
        user_portfolio=[UserPortfolioHoldingSchema(
            asset_class=holding.assetclass,
            symbol=holding.symbol,
            name=holding.name,
            quantity=holding.quantity,
        ) for holding in user_context.userportfolio],
        created_at=user_context.createdat,
        updated_at=user_context.updatedat,
    )
