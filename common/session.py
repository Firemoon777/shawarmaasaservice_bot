import asyncio

from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from common.model.base import BaseTable
from common.settings import DatabaseSettings

SessionLocal = sessionmaker(autocommit=False, autoflush=False, class_=AsyncSession, expire_on_commit=False)


def get_engine(dsn) -> Engine:

    engine = create_async_engine(
        dsn,
        pool_pre_ping=True,
        pool_use_lifo=True,
        future=True,
        echo=False,
        max_overflow=10,
        pool_size=100,
        pool_recycle=60,
        query_cache_size=5000,
    )

    return engine


def make_session(settings: DatabaseSettings, create=False):
    engine = get_engine(
        settings.dsn
    )

    async def create_schema():
        async with engine.begin() as conn:
            await conn.run_sync(BaseTable.metadata.drop_all)
            await conn.run_sync(BaseTable.metadata.create_all)

    if create:
        import common.model
        asyncio.run(create_schema())

    SessionLocal.configure(bind=engine)

    return SessionLocal


async def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
