"""Week 8 tests: Admin Panel + Notifications Frontend (backend APIs)."""
import pytest
import pytest_asyncio

ADMIN_COOKIES = {"admin_session": "fittracker_admin_secret_2024"}


# ── Helper ─────────────────────────────────────────────────────────────────────

async def do_complete_workout(client, headers):
    """Create and finish a workout to trigger gamification/notifications."""
    # Create exercise
    from sqlalchemy import text
    r = await client.post("/api/workouts", json={"name": "Notif Test Workout"}, headers=headers)
    assert r.status_code == 201
    wid = r.json()["id"]
    await client.post(f"/api/workouts/{wid}/finish", json={}, headers=headers)
    return wid


# ── Admin Panel Tests ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_login_page_get(client):
    """GET /admin/login returns 200 HTML."""
    r = await client.get("/admin/login")
    assert r.status_code == 200
    assert "FitTracker Admin" in r.text


@pytest.mark.asyncio
async def test_admin_login_wrong_password(client):
    """POST /admin/login with wrong password returns 200 with error message."""
    r = await client.post("/admin/login", data={"password": "wrongpassword"}, follow_redirects=False)
    assert r.status_code == 200
    assert "Invalid password" in r.text


@pytest.mark.asyncio
async def test_admin_login_success(client):
    """POST /admin/login with correct password redirects to /admin and sets cookie."""
    r = await client.post("/admin/login", data={"password": "admin123"}, follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] in ("/admin", "http://test/admin")
    assert "admin_session" in r.cookies


@pytest.mark.asyncio
async def test_admin_dashboard_no_auth(client):
    """GET /admin without cookie redirects to login."""
    r = await client.get("/admin", follow_redirects=False)
    assert r.status_code in (302, 307)
    assert "login" in r.headers["location"]


@pytest.mark.asyncio
async def test_admin_dashboard_authenticated(client):
    """GET /admin with admin cookie returns 200 HTML with Dashboard content."""
    r = await client.get("/admin", cookies=ADMIN_COOKIES)
    assert r.status_code == 200
    assert "Dashboard" in r.text


@pytest.mark.asyncio
async def test_admin_users_page(client):
    """GET /admin/users with admin cookie returns 200 HTML."""
    r = await client.get("/admin/users", cookies=ADMIN_COOKIES)
    assert r.status_code == 200
    assert "Users" in r.text


@pytest.mark.asyncio
async def test_admin_toggle_user_status(client, auth_headers):
    """POST /admin/users/{id}/toggle toggles user status and redirects."""
    # Get the user id
    me = await client.get("/api/auth/me", headers=auth_headers)
    user_id = me.json()["id"]

    r = await client.post(f"/admin/users/{user_id}/toggle", cookies=ADMIN_COOKIES, follow_redirects=False)
    assert r.status_code == 302

    # Re-activate so subsequent tests using this user still work
    await client.post(f"/admin/users/{user_id}/toggle", cookies=ADMIN_COOKIES, follow_redirects=False)


@pytest.mark.asyncio
async def test_admin_exercises_page(client):
    """GET /admin/exercises with admin cookie returns 200 HTML."""
    r = await client.get("/admin/exercises", cookies=ADMIN_COOKIES)
    assert r.status_code == 200
    assert "Exercise" in r.text


@pytest.mark.asyncio
async def test_admin_add_exercise(client):
    """POST /admin/exercises adds exercise and redirects."""
    r = await client.post(
        "/admin/exercises",
        data={
            "name": "Admin Test Exercise",
            "muscle_primary": "chest",
            "category": "strength",
            "difficulty": "beginner",
        },
        cookies=ADMIN_COOKIES,
        follow_redirects=False,
    )
    assert r.status_code == 302


@pytest.mark.asyncio
async def test_admin_logs_page(client):
    """GET /admin/logs with admin cookie returns 200 HTML."""
    r = await client.get("/admin/logs", cookies=ADMIN_COOKIES)
    assert r.status_code == 200
    assert "Recent" in r.text


# ── Notification API Tests ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_notifications_empty(client, auth_headers):
    """GET /api/notifications returns 200 with a list."""
    r = await client.get("/api/notifications", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_notifications_unread_count(client, auth_headers):
    """GET /api/notifications/unread-count returns 200 with count field."""
    r = await client.get("/api/notifications/unread-count", headers=auth_headers)
    assert r.status_code == 200
    assert "count" in r.json()


@pytest.mark.asyncio
async def test_notifications_no_auth(client):
    """GET /api/notifications without auth returns 401."""
    r = await client.get("/api/notifications")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_notifications_mark_read_not_found(client, auth_headers):
    """PUT /api/notifications/99999/read returns 404 for non-existent notification."""
    r = await client.put("/api/notifications/99999/read", headers=auth_headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_notifications_settings_default(client, auth_headers):
    """GET /api/notifications/settings returns 200 with all setting fields."""
    r = await client.get("/api/notifications/settings", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "streak_alerts" in data
    assert "workout_reminders" in data
    assert "achievement_alerts" in data


@pytest.mark.asyncio
async def test_notifications_settings_update(client, auth_headers):
    """PUT /api/notifications/settings updates a field and returns updated settings."""
    r = await client.put(
        "/api/notifications/settings",
        json={"streak_alerts": False},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["streak_alerts"] is False


@pytest.mark.asyncio
async def test_notifications_mark_all_read(client, auth_headers):
    """PUT /api/notifications/read-all returns 204."""
    r = await client.put("/api/notifications/read-all", headers=auth_headers)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_notifications_delete_not_found(client, auth_headers):
    """DELETE /api/notifications/99999 returns 404 for non-existent notification."""
    r = await client.delete("/api/notifications/99999", headers=auth_headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_notifications_after_workout(client, auth_headers2):
    """Completing a workout may create notifications; list returns a list regardless."""
    await do_complete_workout(client, auth_headers2)
    r = await client.get("/api/notifications", headers=auth_headers2)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_notifications_unread_decreases_after_mark_all_read(client, auth_headers2):
    """After mark-all-read, unread count is 0."""
    await do_complete_workout(client, auth_headers2)

    # Mark all read
    r = await client.put("/api/notifications/read-all", headers=auth_headers2)
    assert r.status_code == 204

    # Unread count should be 0
    r = await client.get("/api/notifications/unread-count", headers=auth_headers2)
    assert r.status_code == 200
    assert r.json()["count"] == 0
