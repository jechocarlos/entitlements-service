import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from uuid import uuid4

# Load environment variables for tests
load_dotenv()

# Use a separate test database if possible, or ensure cleanup
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/test_entitlements_db"))
if "entitlements_db" in TEST_DATABASE_URL and "test_entitlements_db" not in TEST_DATABASE_URL:
    print(f"WARNING: Test database URL might be pointing to production DB: {TEST_DATABASE_URL}. Ensure this is intended.")

# Ensure the main app module can be imported
# This might require adjusting PYTHONPATH or how tests are run
from app.main import app # FastAPI app instance
from app.database import Base, get_db # Base for table creation, get_db for overriding
from app.schemas import EntitlementCreate, EntitlementUpdate, Entitlement as EntitlementSchema

# Setup test database engine and session
engine = create_async_engine(TEST_DATABASE_URL, echo=False) # echo=False for cleaner test output
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Fixture to create and drop tables for each test function
@pytest.fixture(scope="function")
async def db_session() -> AsyncSession:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        await session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

# Fixture to override the get_db dependency in the app
@pytest.fixture(scope="function")
async def override_get_db(db_session: AsyncSession):
    async def _override_get_db():
        try:
            yield db_session
        finally:
            pass # Session is managed by db_session fixture
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None) # Clean up override

# Async client for making API requests
@pytest.fixture(scope="function")
async def client(override_get_db) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

# --- Test Cases --- #

@pytest.mark.asyncio
async def test_create_entitlement(client: AsyncClient, db_session: AsyncSession):
    entitlement_data = {
        "user_id": "test_user_123",
        "resource_type": "document",
        "resource_id": "doc_abc_789",
        "access_level": "edit",
        "description": "Test document entitlement"
    }
    response = await client.post("/api/v1/entitlements/", json=entitlement_data)
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == entitlement_data["user_id"]
    assert data["resource_type"] == entitlement_data["resource_type"]
    assert data["resource_id"] == entitlement_data["resource_id"]
    assert data["access_level"] == entitlement_data["access_level"]
    assert "id" in data
    assert data["is_active"] == True # Default value

@pytest.mark.asyncio
async def test_create_entitlement_missing_fields(client: AsyncClient):
    response = await client.post("/api/v1/entitlements/", json={"user_id": "user1"})
    assert response.status_code == 400 # Or 422 if FastAPI handles it earlier
    # Based on custom validation in router: detail="user_id, resource_type, and resource_id are required"
    # If Pydantic handles it, the detail structure will be different.
    # assert "resource_type" in response.json()["detail"][0]["loc"]

@pytest.mark.asyncio
async def test_read_entitlements_empty(client: AsyncClient):
    response = await client.get("/api/v1/entitlements/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0

@pytest.mark.asyncio
async def test_read_entitlements_with_data(client: AsyncClient, db_session: AsyncSession):
    # Create some entitlements first
    ent1_data = {"user_id": "user1", "resource_type": "collection", "resource_id": "col1", "access_level": "read"}
    ent2_data = {"user_id": "user2", "resource_type": "document", "resource_id": "doc1", "access_level": "write", "is_active": False}
    await client.post("/api/v1/entitlements/", json=ent1_data)
    await client.post("/api/v1/entitlements/", json=ent2_data)

    response = await client.get("/api/v1/entitlements/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 2
    assert data["items"][0]["user_id"] == "user1"
    assert data["items"][1]["user_id"] == "user2"

@pytest.mark.asyncio
async def test_read_single_entitlement(client: AsyncClient, db_session: AsyncSession):
    ent_data = {"user_id": "user_single", "resource_type": "tool", "resource_id": "tool_xyz", "access_level": "use"}
    create_response = await client.post("/api/v1/entitlements/", json=ent_data)
    ent_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/entitlements/{ent_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ent_id
    assert data["user_id"] == ent_data["user_id"]

@pytest.mark.asyncio
async def test_read_single_entitlement_not_found(client: AsyncClient):
    random_uuid = str(uuid4())
    response = await client.get(f"/api/v1/entitlements/{random_uuid}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entitlement not found"

@pytest.mark.asyncio
async def test_update_entitlement(client: AsyncClient, db_session: AsyncSession):
    ent_data = {"user_id": "user_to_update", "resource_type": "system", "resource_id": "sys_main", "access_level": "admin"}
    create_response = await client.post("/api/v1/entitlements/", json=ent_data)
    ent_id = create_response.json()["id"]

    update_payload = {"access_level": "viewer", "is_active": False, "description": "Updated access"}
    response = await client.put(f"/api/v1/entitlements/{ent_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ent_id
    assert data["access_level"] == "viewer"
    assert data["is_active"] == False
    assert data["description"] == "Updated access"
    assert data["user_id"] == ent_data["user_id"] # Unchanged field

@pytest.mark.asyncio
async def test_update_entitlement_not_found(client: AsyncClient):
    random_uuid = str(uuid4())
    update_payload = {"access_level": "none"}
    response = await client.put(f"/api/v1/entitlements/{random_uuid}", json=update_payload)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_entitlement(client: AsyncClient, db_session: AsyncSession):
    ent_data = {"user_id": "user_to_delete", "resource_type": "feature", "resource_id": "feat_beta", "access_level": "tester"}
    create_response = await client.post("/api/v1/entitlements/", json=ent_data)
    ent_id = create_response.json()["id"]

    # Verify it exists
    get_response = await client.get(f"/api/v1/entitlements/{ent_id}")
    assert get_response.status_code == 200

    # Delete it
    delete_response = await client.delete(f"/api/v1/entitlements/{ent_id}")
    assert delete_response.status_code == 200
    deleted_data = delete_response.json()
    assert deleted_data["id"] == ent_id

    # Verify it's gone
    get_after_delete_response = await client.get(f"/api/v1/entitlements/{ent_id}")
    assert get_after_delete_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_entitlement_not_found(client: AsyncClient):
    random_uuid = str(uuid4())
    response = await client.delete(f"/api/v1/entitlements/{random_uuid}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_entitlements_with_filters(client: AsyncClient, db_session: AsyncSession):
    # Create diverse entitlements
    await client.post("/api/v1/entitlements/", json={"user_id": "filter_user1", "resource_type": "doc", "resource_id": "doc1", "access_level": "read"})
    await client.post("/api/v1/entitlements/", json={"user_id": "filter_user1", "resource_type": "col", "resource_id": "col1", "access_level": "edit"})
    await client.post("/api/v1/entitlements/", json={"user_id": "filter_user2", "resource_type": "doc", "resource_id": "doc2", "access_level": "read", "is_active": False})
    await client.post("/api/v1/entitlements/", json={"user_id": "filter_user1", "resource_type": "doc", "resource_id": "doc3", "access_level": "admin", "is_active": False})

    # Filter by user_id
    response = await client.get("/api/v1/entitlements/?user_id=filter_user1")
    data = response.json()
    assert response.status_code == 200
    assert data["total"] == 3
    assert all(item["user_id"] == "filter_user1" for item in data["items"])

    # Filter by user_id and resource_type
    response = await client.get("/api/v1/entitlements/?user_id=filter_user1&resource_type=doc")
    data = response.json()
    assert response.status_code == 200
    assert data["total"] == 2
    assert all(item["user_id"] == "filter_user1" and item["resource_type"] == "doc" for item in data["items"])

    # Filter by user_id, resource_type, and is_active=False
    response = await client.get("/api/v1/entitlements/?user_id=filter_user1&resource_type=doc&is_active=false")
    data = response.json()
    assert response.status_code == 200
    assert data["total"] == 1
    item = data["items"][0]
    assert item["user_id"] == "filter_user1" and item["resource_type"] == "doc" and item["is_active"] == False and item["resource_id"] == "doc3"

    # Filter by is_active=true
    response = await client.get("/api/v1/entitlements/?is_active=true")
    data = response.json()
    assert response.status_code == 200
    assert data["total"] == 2 # user1/doc/doc1, user1/col/col1
    assert all(item["is_active"] == True for item in data["items"])
