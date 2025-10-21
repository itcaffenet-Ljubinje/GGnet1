"""
Database Connection and Session Management

Simple async database setup with SQLite.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config.settings import settings
from db.models import Base

# Engine and session maker
engine = None
async_session_maker = None


async def init_db():
    """Initialize database and create tables"""
    global engine, async_session_maker

    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True
    )

    # Create session factory
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print(f"[OK] Database initialized: {settings.DATABASE_URL}")


async def close_db():
    """Close database connection"""
    global engine
    if engine:
        await engine.dispose()
        print("[OK] Database connection closed")


async def get_db():
    """
    Dependency for getting database session

    Usage:
        @app.get("/machines")
        async def get_machines(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Machine))
            return result.scalars().all()
    """
    if async_session_maker is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
