import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from faker import Faker
import random

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    username = Column(String, unique=True, nullable=False)

class Item(Base):
    __tablename__ = 'items'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

DATABASE_URL = "postgresql+asyncpg://tester:qwertyuiop[]\\@localhost/testdb"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def create_fake_data():
    fake = Faker()
    async with AsyncSessionLocal() as session:
        users = []
        for _ in range(500):
            user = User(username=fake.unique.user_name())
            users.append(user)
        session.add_all(users)
        await session.flush()

        items = []
        for _ in range(20000):
            item = Item(
                name=f"{fake.word()} {fake.word()}",
                description=fake.text(max_nb_chars=200),
                price=round(random.uniform(1, 1000), 2),
                quantity=random.randint(1, 100),
                user_id=random.choice(users).id
            )
            items.append(item)
        session.add_all(items)
        await session.commit()

async def main():
    await create_tables()
    print("*********************************************************")
    print("Tables created")
    await create_fake_data()

if __name__ == "__main__":
    asyncio.run(main())