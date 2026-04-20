"""Week 9 — Advanced Analytics: 20 tests."""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

# Shared engine is the session-scoped fixture from conftest.py


# ── helpers ───────────────────────────────────────────────────────────────────

async def _unique_headers(client) -> dict:
    """Register a brand-new user and return auth headers (guaranteed empty data)."""
    import uuid
    uid = uuid.uuid4().hex[:8]
    await client.post("/api/auth/register", json={
        "username": f"user_{uid}",
        "email": f"user_{uid}@example.com",
        "password": "TestPass123!",
        "full_name": "Unique User",
    })
    resp = await client.post("/api/auth/login", json={
        "email": f"user_{uid}@example.com",
        "password": "TestPass123!",
    })
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


async def _create_exercise(engine, muscle_primary: str = "chest", name: str = None, slug: str = None) -> int:
    """Insert an exercise directly into DB and return its id."""
    import uuid
    slug = slug or f"ex-{uuid.uuid4().hex[:8]}"
    name = name or f"Exercise {uuid.uuid4().hex[:6]}"
    async_sess = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_sess() as s:
        r = await s.execute(
            text(
                "INSERT INTO exercise_library (name, slug, muscle_primary, category, difficulty, is_custom, met_value)"
                " VALUES (:name, :slug, :mp, 'strength', 'beginner', 1, 5.0)"
            ),
            {"name": name, "slug": slug, "mp": muscle_primary},
        )
        await s.commit()
        return r.lastrowid


async def _create_food(engine) -> int:
    """Insert a test food directly into DB and return its id."""
    async_sess = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_sess() as s:
        r = await s.execute(
            text(
                "INSERT INTO foods (name, calories_per_100g, protein_g, carbs_g, fat_g, fiber_g, sugar_g, sodium_mg, is_custom)"
                " VALUES ('Test Food', 200.0, 10.0, 20.0, 5.0, 2.0, 3.0, 50.0, 0)"
            )
        )
        await s.commit()
        return r.lastrowid


async def _finish_workout(client, headers, exercise_id: int) -> int:
    """Create workout, add exercise + completed set, finish it. Returns session id."""
    wo = await client.post("/api/workouts", json={"name": "Test Workout"}, headers=headers)
    assert wo.status_code == 201
    wid = wo.json()["id"]

    ex = await client.post(
        f"/api/workouts/{wid}/exercises",
        json={"exercise_library_id": exercise_id, "exercise_order": 1},
        headers=headers,
    )
    assert ex.status_code == 201
    eid = ex.json()["id"]

    set_resp = await client.post(
        f"/api/workouts/{wid}/exercises/{eid}/sets",
        json={"set_number": 1, "weight_kg": 100.0, "reps": 5, "set_type": "normal"},
        headers=headers,
    )
    assert set_resp.status_code == 201
    sid = set_resp.json()["id"]

    await client.patch(
        f"/api/workouts/{wid}/exercises/{eid}/sets/{sid}",
        json={"completed": True},
        headers=headers,
    )
    finish = await client.post(f"/api/workouts/{wid}/finish", json={}, headers=headers)
    assert finish.status_code == 200
    return wid


# ── Volume Progression ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_volume_progression_empty(client):
    headers = await _unique_headers(client)
    resp = await client.get("/api/analytics/volume-progression", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_volume_progression_with_workouts(client, auth_headers, engine):
    ex_id = await _create_exercise(engine)
    await _finish_workout(client, auth_headers, ex_id)
    await _finish_workout(client, auth_headers, ex_id)

    resp = await client.get("/api/analytics/volume-progression", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert any("week" in p and p["workout_count"] >= 1 for p in data)


@pytest.mark.asyncio
async def test_volume_progression_rolling_avg(client, auth_headers, engine):
    ex_id = await _create_exercise(engine)
    await _finish_workout(client, auth_headers, ex_id)

    resp = await client.get("/api/analytics/volume-progression", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert "rolling_avg" in data[0]
    assert isinstance(data[0]["rolling_avg"], (int, float))


# ── Muscle Balance ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_muscle_balance_empty(client):
    headers = await _unique_headers(client)
    resp = await client.get("/api/analytics/muscle-balance", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    categories = {d["category"] for d in data}
    assert categories == {"push", "pull", "legs", "core", "other"}
    assert all(d["sets_count"] == 0 for d in data)


@pytest.mark.asyncio
async def test_muscle_balance_with_sets(client, engine):
    headers = await _unique_headers(client)
    chest_ex = await _create_exercise(engine, muscle_primary="chest")
    back_ex = await _create_exercise(engine, muscle_primary="back")

    await _finish_workout(client, headers, chest_ex)
    await _finish_workout(client, headers, back_ex)

    resp = await client.get("/api/analytics/muscle-balance", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    by_cat = {d["category"]: d for d in data}
    assert by_cat["push"]["sets_count"] > 0
    assert by_cat["pull"]["sets_count"] > 0


@pytest.mark.asyncio
async def test_muscle_balance_percentages_sum_100(client, engine):
    headers = await _unique_headers(client)
    chest_ex = await _create_exercise(engine, muscle_primary="chest")
    await _finish_workout(client, headers, chest_ex)

    resp = await client.get("/api/analytics/muscle-balance", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    total_pct = sum(d["percentage"] for d in data)
    assert abs(total_pct - 100.0) < 1.0  # allow minor float rounding


# ── Body Composition ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_body_composition_empty(client):
    headers = await _unique_headers(client)
    resp = await client.get("/api/analytics/body-composition", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_body_composition_returns_data(client):
    headers = await _unique_headers(client)
    await client.post(
        "/api/body/metrics",
        json={"weight_kg": 75.0, "body_fat_pct": 18.5},
        headers=headers,
    )
    resp = await client.get("/api/analytics/body-composition", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["weight_kg"] == pytest.approx(75.0, abs=0.1)
    assert data[0]["body_fat_pct"] == pytest.approx(18.5, abs=0.1)


@pytest.mark.asyncio
async def test_body_composition_max_90_days(client, engine):
    headers = await _unique_headers(client)
    # Insert a metric recorded 100 days ago (beyond 90-day window)
    old_date = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
    # Get user_id from the me endpoint
    me = await client.get("/api/auth/me", headers=headers)
    user_id = me.json()["id"]

    async_sess = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_sess() as s:
        await s.execute(
            text(
                "INSERT INTO body_metrics (user_id, weight_kg, recorded_at)"
                " VALUES (:uid, 80.0, :dt)"
            ),
            {"uid": user_id, "dt": old_date},
        )
        await s.commit()

    resp = await client.get("/api/analytics/body-composition", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []  # old metric not returned


# ── Nutrition Heatmap ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_nutrition_heatmap_empty(client):
    headers = await _unique_headers(client)
    resp = await client.get("/api/analytics/nutrition-heatmap", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 90
    assert all(d["calories_logged"] == 0.0 for d in data)


@pytest.mark.asyncio
async def test_nutrition_heatmap_with_meals(client, engine):
    headers = await _unique_headers(client)
    food_id = await _create_food(engine)

    await client.post(
        "/api/nutrition/log",
        json={"food_id": food_id, "meal_type": "lunch", "quantity_g": 200.0},
        headers=headers,
    )

    resp = await client.get("/api/analytics/nutrition-heatmap", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    today_entries = [d for d in data if d["calories_logged"] > 0]
    assert len(today_entries) >= 1
    # 200g of food at 200 cal/100g = 400 calories
    assert today_entries[0]["calories_logged"] == pytest.approx(400.0, abs=1.0)


@pytest.mark.asyncio
async def test_nutrition_heatmap_with_goal(client, engine):
    headers = await _unique_headers(client)
    food_id = await _create_food(engine)

    await client.put(
        "/api/nutrition/goals",
        json={"calories_target": 2000, "protein_g": 150, "carbs_g": 200, "fat_g": 65, "fiber_g": 25},
        headers=headers,
    )
    await client.post(
        "/api/nutrition/log",
        json={"food_id": food_id, "meal_type": "lunch", "quantity_g": 200.0},
        headers=headers,
    )

    resp = await client.get("/api/analytics/nutrition-heatmap", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    today_entries = [d for d in data if d["calories_logged"] > 0]
    assert len(today_entries) >= 1
    assert today_entries[0]["goal_calories"] == pytest.approx(2000.0, abs=1.0)
    assert today_entries[0]["adherence_pct"] is not None
    assert today_entries[0]["adherence_pct"] == pytest.approx(20.0, abs=1.0)  # 400/2000*100


# ── CSV Export ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_export_csv_empty(client):
    headers = await _unique_headers(client)
    resp = await client.get("/api/analytics/export/csv", headers=headers)
    assert resp.status_code == 200
    lines = [l for l in resp.text.strip().splitlines() if l]
    assert len(lines) == 1  # header only
    assert "date" in lines[0] and "workout_name" in lines[0]


@pytest.mark.asyncio
async def test_export_csv_with_workouts(client, engine):
    headers = await _unique_headers(client)
    ex_id = await _create_exercise(engine)
    await _finish_workout(client, headers, ex_id)

    resp = await client.get("/api/analytics/export/csv", headers=headers)
    assert resp.status_code == 200
    lines = [l for l in resp.text.strip().splitlines() if l]
    assert len(lines) == 2  # header + 1 data row
    assert "Test Workout" in lines[1]


@pytest.mark.asyncio
async def test_export_csv_content_type(client):
    headers = await _unique_headers(client)
    resp = await client.get("/api/analytics/export/csv", headers=headers)
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_export_csv_filename_header(client):
    headers = await _unique_headers(client)
    resp = await client.get("/api/analytics/export/csv", headers=headers)
    assert resp.status_code == 200
    disposition = resp.headers.get("content-disposition", "")
    assert "attachment" in disposition
    assert "filename=" in disposition
    assert ".csv" in disposition


# ── Auth Required ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_volume_progression_auth_required(client):
    resp = await client.get("/api/analytics/volume-progression")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_muscle_balance_auth_required(client):
    resp = await client.get("/api/analytics/muscle-balance")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_body_composition_auth_required(client):
    resp = await client.get("/api/analytics/body-composition")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_nutrition_heatmap_auth_required(client):
    resp = await client.get("/api/analytics/nutrition-heatmap")
    assert resp.status_code == 401
