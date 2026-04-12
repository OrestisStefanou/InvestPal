import http

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException
)
from pydantic import BaseModel

from services.user_context import UserContextService
from dependencies import get_user_context_service
from services.user_context import (
    UserContextAlreadyExistsError,
    UserContextNotFoundError,
)


router = APIRouter()


class UserContextSchema(BaseModel):
    user_id: str
    user_profile: dict | None = None


class UserContextResponseSchema(UserContextSchema):
    created_at: str | None
    updated_at: str | None


@router.post("/user_context", response_model=UserContextResponseSchema, status_code=http.HTTPStatus.CREATED)
async def create_user_context(request: UserContextSchema, user_context_service: UserContextService = Depends(get_user_context_service)):
    try:
        created_user_context = await user_context_service.create_user_context(
            user_id=request.user_id,
            user_profile=request.user_profile or {},
        )
    except UserContextAlreadyExistsError as e:
        raise HTTPException(status_code=http.HTTPStatus.CONFLICT, detail=str(e))
    
    return UserContextResponseSchema(
        user_id=created_user_context.user_id,
        user_profile=created_user_context.user_profile,
        created_at=created_user_context.created_at,
        updated_at=created_user_context.updated_at,
    )

@router.get("/user_context/{user_id}", response_model=UserContextResponseSchema)
async def get_user_context(user_id: str, user_context_service: UserContextService = Depends(get_user_context_service)):
    user_context = await user_context_service.get_user_context(user_id)
    
    if not user_context:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="User context not found")

    return UserContextResponseSchema(
        user_id=user_context.user_id,
        user_profile=user_context.user_profile,
        created_at=user_context.created_at,
        updated_at=user_context.updated_at,
    )

@router.put("/user_context", response_model=UserContextResponseSchema)
async def update_user_context(request: UserContextSchema, user_context_service: UserContextService = Depends(get_user_context_service)):
    try:
        user_context = await user_context_service.update_user_context(
            user_id=request.user_id,
            user_profile=request.user_profile,
        )
    except UserContextNotFoundError as e:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail=str(e))
    
    return UserContextResponseSchema(
        user_id=user_context.user_id,
        user_profile=user_context.user_profile,
        created_at=user_context.created_at,
        updated_at=user_context.updated_at,
    )
