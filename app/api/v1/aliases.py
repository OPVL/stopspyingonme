from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.alias import (
    AliasCreate,
    AliasListResponse,
    AliasResponse,
    AliasUpdate,
    RandomAliasRequest,
    RandomAliasResponse,
)
from app.services.alias import AliasService

router = APIRouter()


@router.post("/", response_model=AliasResponse, status_code=status.HTTP_201_CREATED)
async def create_alias(
    alias_data: AliasCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AliasResponse:
    """Create a new alias."""
    service = AliasService(db)

    try:
        alias = await service.create_alias(
            user_id=current_user.id,
            name=alias_data.name,
            domain=alias_data.domain,
            destination_id=alias_data.destination_id,
            note=alias_data.note,
            labels=alias_data.labels,
            expires_at=alias_data.expires_at,
        )
        return AliasResponse.model_validate(alias)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=AliasListResponse)
async def list_aliases(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    label: Annotated[str | None, Query()] = None,
    active_only: Annotated[bool | None, Query()] = None,
) -> AliasListResponse:
    """List aliases for the current user."""
    service = AliasService(db)

    aliases, total = await service.list_aliases(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        label=label,
        active_only=active_only,
    )

    pages = ceil(total / per_page) if total > 0 else 1

    return AliasListResponse(
        aliases=[AliasResponse.model_validate(alias) for alias in aliases],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/{alias_id}", response_model=AliasResponse)
async def get_alias(
    alias_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AliasResponse:
    """Get a specific alias."""
    service = AliasService(db)

    alias = await service.get_alias(alias_id, current_user.id)
    if not alias:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alias not found"
        )

    return AliasResponse.model_validate(alias)


@router.patch("/{alias_id}", response_model=AliasResponse)
async def update_alias(
    alias_id: int,
    alias_data: AliasUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AliasResponse:
    """Update an alias."""
    service = AliasService(db)

    # Only include non-None values in the update
    updates = alias_data.model_dump(exclude_unset=True, exclude_none=True)

    try:
        alias = await service.update_alias(alias_id, current_user.id, **updates)
        if not alias:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Alias not found"
            )

        return AliasResponse.model_validate(alias)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{alias_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alias(
    alias_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete an alias."""
    service = AliasService(db)

    success = await service.delete_alias(alias_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alias not found"
        )


@router.post("/generate", response_model=RandomAliasResponse)
async def generate_random_alias(
    request: RandomAliasRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RandomAliasResponse:
    """Generate a random alias name."""
    service = AliasService(db)

    try:
        name = await service.generate_random_alias(
            domain=request.domain,
            prefix=request.prefix,
            length=request.length,
        )

        full_address = f"{name}@{request.domain}"

        return RandomAliasResponse(
            name=name,
            domain=request.domain,
            full_address=full_address,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
