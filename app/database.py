from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Async engine for FastAPI
engine = create_async_engine(DATABASE_URL, echo=True) # echo=True for logging SQL queries, remove in prod

# Async session
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# For Alembic, it typically uses a synchronous engine for migrations.
# If you need a synchronous engine for Alembic or other tools:
# from sqlalchemy import create_engine
# DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC", DATABASE_URL.replace("asyncpg", "psycopg2"))
# sync_engine = create_engine(DATABASE_URL_SYNC)
