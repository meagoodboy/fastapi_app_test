## make a psql session using async engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


ENGINE_URL='postgresql+asyncpg://tester:qwertyuiop[]@localhost:5432/testdb'
engine = create_async_engine(ENGINE_URL, echo=True)

AsyncSessionMaker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    try:
        async with AsyncSessionMaker() as session:
            yield session
    finally:
        session.close()