from typing import Union

from database.session import get_db
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import (
    ItemResponse,
    Item,
    User,
)

item_router = APIRouter(prefix="/item", tags=["Item"])

EXAMPLE_USER_ID = "acba3ee8-aedc-4b11-9855-032c06a8a474"
EXAMPLE_ITEM_ID = "00027144-db13-4b33-b340-3f7013d058a2"


@item_router.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": dict, "description": "Item not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": dict,
            "description": "Internal server error",
        },
    },
    summary="Get an item by ID",
    description="Retrieve an item by its unique identifier.",
)
async def get_item(
    item_id: str = Path(..., example=EXAMPLE_ITEM_ID),
    db: AsyncSession = Depends(get_db),
) -> Union[ItemResponse, dict, HTTPException]:
    try:
        item_result = await db.execute(select(Item).where(Item.id == item_id))
        item = item_result.scalars().first()
        if item:
            return item
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@item_router.patch(
    "/items",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": dict, "description": "Item not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": dict,
            "description": "Internal server error",
        },
    },
    summary="Edit an item by ID",
    description="Edit an item by its unique identifier.",
)
async def edit_item(
    item: ItemResponse = Body(...), db: AsyncSession = Depends(get_db)
) -> Union[ItemResponse, dict, HTTPException]:
    try:
        item_result = await db.execute(select(Item).where(Item.id == item.id))
        item_db = item_result.scalars().first()
        if item_db:
            item_db.name = item.name
            item_db.description = item.description
            item_db.price = item.price
            item_db.quantity = item.quantity
            item_db.user_id = item.user_id
            ## check if its a valid user id
            user_result = await db.execute(
                select(User).where(User.id == item.user_id)
            )
            user = user_result.scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            await db.commit()
            return item_db
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
