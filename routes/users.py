from typing import Annotated, Optional, Union

from database.session import get_db
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from models import (
    Item,
    ItemResponse,
    User,
    UserCreate,
    UserResponse,
)
from app_logging import logger
## import annotated

user_router = APIRouter(prefix="/user", tags=["User"])

EXAMPLE_USER_ID = "acba3ee8-aedc-4b11-9855-032c06a8a474"
EXAMPLE_ITEM_ID = "00027144-db13-4b33-b340-3f7013d058a2"


@user_router.get(
    "/{user_id}",
    response_model=Optional[UserResponse],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": dict, "description": "User not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": dict,
            "description": "Internal server error",
        },
    },
    summary="Get a user by ID",
    description="Retrieve a user by their unique identifier.",
)
async def get_user(
    user_id: Annotated[
        str,
        Path(
            examples=EXAMPLE_USER_ID,
        ),
    ],
    db: Annotated[User, Depends(get_db)],
) -> Union[UserResponse, dict, HTTPException]:
    try:
        # find the user
        user = await db.execute(select(User).where(User.id == user_id))
        user_data = user.scalars().first()
        if user_data:
            return {"id": str(user_data.id), "username": user_data.username}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@user_router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": dict, "description": "User not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": dict,
            "description": "Internal server error",
        },
    },
    summary="Delete a user by ID",
    description="Delete a user and their items by the user's unique identifier.",
)
async def delete_user(
    user_id: Annotated[str, Path(example=EXAMPLE_USER_ID)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    try:
        # Find the user
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        # Find and delete user's items
        items_result = await db.execute(
            select(Item).where(Item.user_id == user_id)
        )
        items = items_result.scalars().all()
        items_deleted = len(items)
        for item in items:
            await db.delete(item)
        # Delete the user
        await db.delete(user)
        await db.commit()
        return {
            "message": f"User {user.username} and {items_deleted} item(s) deleted successfully"
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@user_router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": dict,
            "description": "Internal server error",
        },
    },
    summary="Create a user given username",
    description="Create a user with a unique identifier and a username.",
)
async def create_user(
    user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]
) -> Union[UserResponse, dict, HTTPException]:
    try:
        new_user = User(username=user.username)
        db.add(new_user)
        await db.commit()
        result = await db.execute(
            select(User).where(User.username == user.username)
        )
        new_user = result.scalar_one()
        return {"id": str(new_user.id), "username": new_user.username}
    except Exception as e:
        raise e
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@user_router.get(
    "/{user_id}/items",
    response_model=list[ItemResponse],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": dict, "description": "User not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": dict,
            "description": "Internal server error",
        },
    },
    summary="Get all items by user ID",
    description="Retrieve all items by the user's unique identifier.",
)
async def get_items_by_user(
    user_id: str = Path(..., example=EXAMPLE_USER_ID),
    db: AsyncSession = Depends(get_db),
) -> Union[list[ItemResponse], dict, HTTPException]:
    try:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user:
            items_result = await db.execute(
                select(Item).where(Item.user_id == user_id)
            )
            items = items_result.scalars().all()
            return items
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@user_router.get(
    "/{user_id}/items/total",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": dict, "description": "User not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": dict,
            "description": "Internal server error",
        },
    },
    summary="Get the total sum of prices of all items by user ID",
    description="Retrieve the total sum of prices of all items by the user's unique identifier . this is the updated funcction",
)
async def get_total_price_of_items_by_user(
    user_id: str = Path(..., example=EXAMPLE_USER_ID),
    db: AsyncSession = Depends(get_db),
) -> Union[dict, HTTPException]:
    try:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user:
            query = select(func.sum(Item.price)).where(
                Item.user_id == user_id
            )
            result = await db.execute(query)
            total_price = result.scalar_one_or_none()
            return {"total_price": total_price}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@user_router.get(
    "/user-total",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": dict,
            "description": "Internal server error",
        },
    },
    summary="Get the total sum of prices of all items for all users lol",
    description="Retrieve the total sum of prices of all items by all users.",
)
async def get_total_price_of_items_by_all_users(
    db: AsyncSession = Depends(get_db),
):
    try:
        # Join users and items and get the sum of prices grouped by user
        query = (
            select(User.username,
                   func.sum(Item.price).label("total_price"))
            .join(Item, Item.user_id == User.id)  # Corrected join condition
            .group_by(User.username)
            .order_by(func.sum(Item.price).desc())
        )

        result = await db.execute(query)
        total_prices = result.all()

        # Convert the result to a serializable format
        serializable_total_prices = [
            {"username": row.username, "total_price": float(row.total_price)}
            for row in total_prices[:10]
        ]
        return {"total_prices": serializable_total_prices}
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
