from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

## make a psql session using async engine
ENGINE_URL = f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_service}:{settings.postgres_port}/{settings.postgres_db}"

engine = create_async_engine(ENGINE_URL, echo=True)

AsyncSessionMaker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    try:
        async with AsyncSessionMaker() as session:
            yield session
    finally:
        await session.close()
