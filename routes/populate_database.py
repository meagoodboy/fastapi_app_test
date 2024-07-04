import random
from faker import Faker
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models import Item, User, DatabaseRequest, Base
from database.session import get_db
from database.session import engine as dbengine

database_router = APIRouter(prefix="/database")

# Function to create tables in the database
async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

# Function to create fake data and populate the database
async def create_fake_data(db: AsyncSession, user_count: int, item_count: int):
    fake = Faker()
    users = []
    for _ in range(user_count):
        user = User(username=fake.unique.user_name())
        users.append(user)
    db.add_all(users)
    await db.flush()

    items = []
    for _ in range(item_count):
        item = Item(
            name=f"{fake.word()} {fake.word()}",
            description=fake.text(max_nb_chars=200),
            price=round(random.uniform(1, 1000), 2),
            quantity=random.randint(1, 100),
            user_id=random.choice(users).id,
        )
        items.append(item)
    db.add_all(items)
    await db.commit()

# Endpoint to populate the database with fake data
@database_router.put(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": dict,
            "description": "Internal server error",
        },
    },
    summary="Populate the database",
    description="Uses faker to populate the database with fake data.",
    tags=["db"],
)
async def populate_db(
    request: DatabaseRequest, db: AsyncSession = Depends(get_db)
):
    try:
        engine = dbengine
        await create_tables(engine)
        await create_fake_data(db, request.user_count, request.item_count)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {"message": "Database populated successfully"}