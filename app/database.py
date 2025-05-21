import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Load individual database components from environment variables
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError("One or more database connection environment variables are not set (POSTGRES_USER, POSTGRES_PASSWORD, DB_HOST, DB_PORT, POSTGRES_DB)")

# Construct the DATABASE_URL
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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
