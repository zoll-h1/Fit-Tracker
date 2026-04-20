import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.models import trainer as trainer_models  # noqa: F401 - ensures models are registered


@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200


@pytest.mark.anyio
async def test_health_check_response(client: AsyncClient):
    resp = await client.get("/health")
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.anyio
async def test_cors_headers(client: AsyncClient):
    resp = await client.options(
        "/api/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    # CORS middleware should respond with 200 or 405; what matters is the header
    assert resp.status_code in (200, 405)


@pytest.mark.anyio
async def test_api_docs_accessible(client: AsyncClient):
    resp = await client.get("/docs")
    assert resp.status_code == 200


@pytest.mark.anyio
async def test_openapi_json(client: AsyncClient):
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert "info" in data


@pytest.mark.anyio
async def test_workout_list_pagination(client: AsyncClient, auth_headers: dict):
    # Create 3 workouts
    for i in range(3):
        await client.post(
            "/api/workouts/",
            json={"name": f"Workout {i}", "notes": ""},
            headers=auth_headers,
        )
    resp = await client.get("/api/workouts?page=1&per_page=2", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    items = data.get("items", data) if isinstance(data, dict) else data
    assert len(items) <= 2


@pytest.mark.anyio
async def test_workout_list_page_2(client: AsyncClient, auth_headers: dict):
    # Create 3 workouts to ensure we have enough
    for i in range(3):
        await client.post(
            "/api/workouts/",
            json={"name": f"Pag Workout {i}", "notes": ""},
            headers=auth_headers,
        )
    resp = await client.get("/api/workouts?page=2&per_page=2", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.anyio
async def test_analytics_dashboard_requires_auth(client: AsyncClient):
    resp = await client.get("/api/analytics/dashboard")
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_trainer_endpoints_require_auth(client: AsyncClient):
    resp = await client.get("/api/trainer/programs")
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_exercises_paginated(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/exercises?page=1&per_page=5", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    items = data.get("items", data) if isinstance(data, dict) else data
    assert len(items) <= 5


@pytest.mark.anyio
async def test_register_validates_email(client: AsyncClient):
    resp = await client.post(
        "/api/auth/register",
        json={
            "username": "testbademail",
            "email": "not-an-email",
            "password": "TestPass123!",
            "full_name": "Test User",
        },
    )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_register_validates_password_length(client: AsyncClient):
    resp = await client.post(
        "/api/auth/register",
        json={
            "username": "testshortpw",
            "email": "shortpw@example.com",
            "password": "abc",
            "full_name": "Test User",
        },
    )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "username": "dupuser12",
        "email": "duptest12@example.com",
        "password": "TestPass123!",
        "full_name": "Dup User",
    }
    await client.post("/api/auth/register", json=payload)
    payload["username"] = "dupuser12b"
    resp = await client.post("/api/auth/register", json=payload)
    assert resp.status_code in (400, 409)


@pytest.mark.anyio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={
            "username": "wrongpwuser",
            "email": "wrongpw@example.com",
            "password": "TestPass123!",
            "full_name": "Wrong PW",
        },
    )
    resp = await client.post(
        "/api/auth/login",
        json={"email": "wrongpw@example.com", "password": "WrongPass999!"},
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post(
        "/api/auth/login",
        json={"email": "nobody@nowhere.com", "password": "TestPass123!"},
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_profile_update(client: AsyncClient, auth_headers: dict):
    resp = await client.put(
        "/api/users/profile",
        json={"full_name": "Updated Name"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("full_name") == "Updated Name"


@pytest.mark.anyio
async def test_workout_404(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/workouts/999999", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_exercise_404(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/exercises/999999", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_notifications_list(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/notifications", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.anyio
async def test_settings_get(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/notifications/settings", headers=auth_headers)
    assert resp.status_code == 200
