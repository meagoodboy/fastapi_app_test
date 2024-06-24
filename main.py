from fastapi import FastAPI, Depends, HTTPException, status, Body, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from models.models import User, UserCreate, Item
from models.dbm import User as UserModel
from models.dbm import Item as ItemModel
from database.session import get_db
from typing import Optional, Annotated, Union

app = FastAPI()

EXAMPLE_USER_ID = "acba3ee8-aedc-4b11-9855-032c06a8a474"
EXAMPLE_ITEM_ID = "00027144-db13-4b33-b340-3f7013d058a2"

@app.get("/")
async def root():
    return {"message": "Hello World "}

@app.get(
    "/users/{user_id}",
    response_model=Optional[User],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": dict, "description": "User not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": dict, "description": "Internal server error"},
    },
    summary="Get a user by ID",
    description="Retrieve a user by their unique identifier.",
    tags=["users"]
)
async def get_user(
    user_id: Annotated[str,Path(
            examples=EXAMPLE_USER_ID,
        ),],
        db: Annotated[User,Depends(get_db)]
) -> Union[User, dict, HTTPException]:
    try:
        # find the user
        user = await db.execute(select(UserModel).where(UserModel.id == user_id))
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

@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": dict, "description": "User not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": dict, "description": "Internal server error"},
    },
    summary="Delete a user by ID",
    description="Delete a user and their items by the user's unique identifier.",
    tags=["users"]
)
async def delete_user(
    user_id: Annotated[str, Path(example=EXAMPLE_USER_ID)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
    try:
        # Find the user
        user_result = await db.execute(select(UserModel).where(UserModel.id == user_id))
        user = user_result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        # Find and delete user's items
        items_result = await db.execute(select(ItemModel).where(ItemModel.user_id == user_id))
        items = items_result.scalars().all()
        items_deleted = len(items)
        for item in items:
            await db.delete(item)
        # Delete the user
        await db.delete(user)
        await db.commit()
        return {"message": f"User {user.username} and {items_deleted} item(s) deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@app.post(
    "/users",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": dict, "description": "Internal server error"},
    },
    summary="Create a user given username",
    description="Create a user with a unique identifier and a username.",
    tags=["users"]
)
async def create_user(
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Union[User, dict, HTTPException]:
    try:
        new_user = UserModel(username=user.username)
        db.add(new_user)
        await db.commit()
        result = await db.execute(select(UserModel).where(UserModel.username == user.username))
        new_user = result.scalar_one()
        return {"id": str(new_user.id), "username": new_user.username}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@app.get(
    "/users/{user_id}/items",
    response_model=list[Item],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": dict, "description": "User not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": dict, "description": "Internal server error"},
    },
    summary="Get all items by user ID",
    description="Retrieve all items by the user's unique identifier.",
    tags=["items","users"]
)
async def get_items_by_user(
    user_id: str = Path(..., example=EXAMPLE_USER_ID),
    db: AsyncSession = Depends(get_db)
) -> Union[list[Item], dict, HTTPException]:
    try:
        user_result = await db.execute(select(UserModel).where(UserModel.id == user_id))
        user = user_result.scalars().first()
        if user:
            items_result = await db.execute(select(ItemModel).where(ItemModel.user_id == user_id))
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

@app.get(
    "/users/{user_id}/items/total",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": dict, "description": "User not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": dict, "description": "Internal server error"},
    },
    summary="Get the total sum of prices of all items by user ID",
    description="Retrieve the total sum of prices of all items by the user's unique identifier . this is the updated funcction",
    tags=["items","users"]
)
async def get_total_price_of_items_by_user(
    user_id: str = Path(..., example=EXAMPLE_USER_ID),
    db: AsyncSession = Depends(get_db)
) -> Union[dict, HTTPException]:
    try:
        user_result = await db.execute(select(UserModel).where(UserModel.id == user_id))
        user = user_result.scalars().first()
        if user:
            query = select(func.sum(ItemModel.price)).where(ItemModel.user_id == user_id)
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

@app.get(
        "/user_total",
        response_model=dict,
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": dict, "description": "Internal server error"},
        },
        summary="Get the total sum of prices of all items for all users",
        description="Retrieve the total sum of prices of all items by all users.",
        tags=["items","users"]
)
async def get_total_price_of_items_by_all_users(
    db: AsyncSession = Depends(get_db)
):# -> Union[dict, HTTPException]:
    try:
        ## join users and items and get the sum of prices after grouping it where use.id = item.id
        query = (
        select(UserModel.username, func.sum(ItemModel.price).label('total_price'))
        .join(ItemModel, UserModel.id == ItemModel.user_id)
        .group_by(UserModel.username)
        .order_by(func.sum(ItemModel.price).desc())
    )
        result = await db.execute(query)
        total_prices = result.all()
        # print(total_prices)
        # return {"total_prices": total_prices[:10]}
        serializable_total_prices = [
            {"username": row.username, "total_price": float(row.total_price)}
            for row in total_prices[:10]
        ]
        return {"total_prices": serializable_total_prices}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@app.get(
    "/items/{item_id}",
    response_model=Item,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": dict, "description": "Item not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": dict, "description": "Internal server error"},
    },
    summary="Get an item by ID",
    description="Retrieve an item by its unique identifier.",
    tags=["items"]
)
async def get_item(
    item_id: str = Path(..., example=EXAMPLE_ITEM_ID),
    db: AsyncSession = Depends(get_db)
) -> Union[Item, dict, HTTPException]:
    try:
        item_result = await db.execute(select(ItemModel).where(ItemModel.id == item_id))
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

@app.patch(
    "/items",
    response_model=Item,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": dict, "description": "Item not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": dict, "description": "Internal server error"},
    },
    summary="Edit an item by ID",
    description="Edit an item by its unique identifier.",
    tags=["items"]
)
async def edit_item(
    item: Item = Body(...),
    db: AsyncSession = Depends(get_db)
) -> Union[Item, dict, HTTPException]:
    try:
        item_result = await db.execute(select(ItemModel).where(ItemModel.id == item.id))
        item_db = item_result.scalars().first()
        if item_db:
            item_db.name = item.name
            item_db.description = item.description
            item_db.price = item.price
            item_db.quantity = item.quantity
            item_db.user_id = item.user_id
            ## check if its a valid user id
            user_result = await db.execute(select(UserModel).where(UserModel.id == item.user_id))
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