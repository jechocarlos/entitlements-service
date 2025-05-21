from fastapi import FastAPI
from dotenv import load_dotenv
import os

from app.routers import entitlements
from app.database import engine, Base # Make sure Base is imported

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "Entitlements Service"),
    version="0.1.0",
    description="API for managing entitlements."
)

API_V1_STR = os.getenv("API_V1_STR", "/api/v1")

app.include_router(entitlements.router, prefix=API_V1_STR + "/entitlements", tags=["entitlements"])

@app.on_event("startup")
async def startup_event():
    # This will create tables based on your SQLAlchemy models.
    # Suitable for development. For production, consider a more robust migration strategy
    # if you anticipate schema changes.
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Optional: drop tables for a clean start during dev
        await conn.run_sync(Base.metadata.create_all)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {app.title}"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
