from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import settings

Base = declarative_base()
DATABASE_URL = (f"postgresql+asyncpg://{settings.db.DB_USER}:{settings.db.DB_PASSWORD}@{settings.db.DB_HOST}:{settings.db.DB_PORT}/"
                f"{settings.db.DB_NAME}")
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async def init_db():
    pass


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
