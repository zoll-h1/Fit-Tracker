import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(engine):
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def exercise_id(engine) -> int:
    """Insert a test exercise into the DB and return its id (idempotent)."""
    from sqlalchemy import text
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        await session.execute(
            text(
                "INSERT OR IGNORE INTO exercise_library (name, slug, muscle_primary, category, difficulty, is_custom, met_value) "
                "VALUES ('Test Exercise', 'test-exercise', 'chest', 'strength', 'beginner', 1, 5.0)"
            )
        )
        await session.commit()
        result = await session.execute(
            text("SELECT id FROM exercise_library WHERE slug = 'test-exercise'")
        )
        return result.scalar_one()


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client):
    """Register + login user1, return auth headers."""
    await client.post("/api/auth/register", json={
        "username": "testuser1",
        "email": "test1@example.com",
        "password": "TestPass123!",
        "full_name": "Test User 1",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "test1@example.com",
        "password": "TestPass123!",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def auth_headers2(client):
    """Register + login user2, return auth headers."""
    await client.post("/api/auth/register", json={
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "TestPass123!",
        "full_name": "Test User 2",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "test2@example.com",
        "password": "TestPass123!",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
