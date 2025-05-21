# Entitlements Service

This service handles entitlements for various systems like collections, documents, access to tools, etc.

## Features

- CRUD API for entitlements
- Uses FastAPI for the API framework
- Uses PostgreSQL for the database
- Uses SQLAlchemy for ORM
- Uses Pydantic for data validation
- UUIDs for primary keys
- Dockerized for easy deployment

## Setup and Run

### Prerequisites

- Python 3.10+ (or the version specified in your `requirements.txt`)
- Pip (Python package installer)
- Docker and Docker Compose (optional, for containerized setup)

### Local Development (without Docker)

1.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the root directory (copy from `.env.example` if provided) and configure your `DATABASE_URL`.
    Example `.env`:
    ```
    DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
    # e.g., DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/entitlements_db
    ```

4.  **Database Setup:**
    Since Alembic has been removed, you will need to manage database schema manually or use SQLAlchemy's `Base.metadata.create_all(engine)` directly in your application startup for development. For production, a more robust migration strategy would be needed if schema changes are frequent.
    The `app/main.py` currently includes a startup event to create tables:
    ```python
    @app.on_event("startup")
    async def startup_event():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    ```
    This is suitable for development and simple cases.

5.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The application will be available at `http://127.0.0.1:8000`.

### Dockerized Setup

1.  **Build and run the containers:**
    ```bash
    docker-compose up --build
    ```
    This will start the FastAPI application and a PostgreSQL database. The application will be available at `http://localhost:8000`.
    The database tables will be created on startup as defined in `app/main.py`.

## API Endpoints

The API documentation (Swagger UI) is available at `http://localhost:8000/docs`.
The ReDoc documentation is available at `http://localhost:8000/redoc`.

Base URL: `/api/v1`

-   **Entitlements:** `/entitlements`
    -   `POST /`: Create a new entitlement.
    -   `GET /`: Get a list of entitlements.
    -   `GET /{entitlement_id}`: Get a specific entitlement by ID.
    -   `PUT /{entitlement_id}`: Update an entitlement.
    -   `DELETE /{entitlement_id}`: Delete an entitlement.

## Project Structure

```
entitlements-service/
├── app/                  # Main application code
│   ├── __init__.py
│   ├── main.py           # FastAPI app instance and startup
│   ├── crud.py           # CRUD operations for database
│   ├── database.py       # Database connection and session
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic schemas for data validation
│   └── routers/          # API routers
│       ├── __init__.py
│       └── entitlements.py # Router for entitlement endpoints
├── tests/                # Application tests
│   ├── __init__.py
│   └── test_entitlements.py
├── .env.example          # Example environment variables
├── .gitignore
├── Dockerfile            # Docker configuration for the app
├── docker-compose.yml    # Docker Compose for app and database
├── requirements.txt      # Pip dependencies
└── README.md
```

## TODO
- Add more comprehensive tests.
- Implement authentication and authorization.
- Add logging.
- Refine error handling.