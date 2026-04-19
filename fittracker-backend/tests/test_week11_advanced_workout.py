"""Week 11 Advanced Workout Features tests."""
import pytest
import pytest_asyncio
import app.models.trainer  # noqa: F401


# ── 1. Start strength workout ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_start_strength_workout(client, auth_headers):
    resp = await client.post("/api/workouts", json={"name": "Strength Day", "session_type": "strength"}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["session_type"] == "strength"
    assert data["status"] == "in_progress"


# ── 2. Start cardio workout ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_start_cardio_workout(client, auth_headers):
    resp = await client.post("/api/workouts", json={"name": "Morning Run", "session_type": "cardio"}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["session_type"] == "cardio"


# ── 3. Update cardio data ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_cardio_data(client, auth_headers):
    r = await client.post("/api/workouts", json={"name": "Run", "session_type": "cardio"}, headers=auth_headers)
    session_id = r.json()["id"]

    resp = await client.patch(
        f"/api/workouts/{session_id}/cardio",
        json={"distance_km": 5.2, "avg_pace_min_km": 5.45, "avg_heart_rate": 145, "max_heart_rate": 162, "session_type": "cardio"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert float(data["distance_km"]) == pytest.approx(5.2, rel=1e-2)
    assert data["avg_heart_rate"] == 145


# ── 4. Update cardio requires auth ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_cardio_requires_auth(client, auth_headers):
    r = await client.post("/api/workouts", json={"name": "Run"}, headers=auth_headers)
    session_id = r.json()["id"]

    resp = await client.patch(f"/api/workouts/{session_id}/cardio", json={"distance_km": 3.0})
    assert resp.status_code == 401


# ── 5. Update cardio wrong user ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_cardio_wrong_user(client, auth_headers, auth_headers2):
    r = await client.post("/api/workouts", json={"name": "My Run"}, headers=auth_headers)
    session_id = r.json()["id"]

    resp = await client.patch(
        f"/api/workouts/{session_id}/cardio",
        json={"distance_km": 4.0},
        headers=auth_headers2,
    )
    assert resp.status_code == 404


# ── 6. Set superset group ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_set_superset_group(client, auth_headers, exercise_id):
    r = await client.post("/api/workouts", json={"name": "Superset Day"}, headers=auth_headers)
    session_id = r.json()["id"]

    r2 = await client.post(
        f"/api/workouts/{session_id}/exercises",
        json={"exercise_library_id": exercise_id, "exercise_order": 1},
        headers=auth_headers,
    )
    we_id = r2.json()["id"]

    resp = await client.patch(
        f"/api/workouts/exercises/{we_id}/superset",
        json={"superset_group": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["superset_group"] == 1


# ── 7. Clear superset group ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_clear_superset_group(client, auth_headers, exercise_id):
    r = await client.post("/api/workouts", json={"name": "Workout"}, headers=auth_headers)
    session_id = r.json()["id"]

    r2 = await client.post(
        f"/api/workouts/{session_id}/exercises",
        json={"exercise_library_id": exercise_id, "exercise_order": 1},
        headers=auth_headers,
    )
    we_id = r2.json()["id"]

    await client.patch(f"/api/workouts/exercises/{we_id}/superset", json={"superset_group": 2}, headers=auth_headers)
    resp = await client.patch(f"/api/workouts/exercises/{we_id}/superset", json={"superset_group": None}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["superset_group"] is None


# ── 8. Superset requires auth ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_superset_requires_auth(client, auth_headers, exercise_id):
    r = await client.post("/api/workouts", json={"name": "Workout"}, headers=auth_headers)
    session_id = r.json()["id"]
    r2 = await client.post(
        f"/api/workouts/{session_id}/exercises",
        json={"exercise_library_id": exercise_id, "exercise_order": 1},
        headers=auth_headers,
    )
    we_id = r2.json()["id"]

    resp = await client.patch(f"/api/workouts/exercises/{we_id}/superset", json={"superset_group": 1})
    assert resp.status_code == 401


# ── 9. Create custom exercise ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_custom_exercise(client, auth_headers):
    resp = await client.post(
        "/api/exercises/custom",
        json={"name": "My Custom Curl", "muscle_primary": "biceps", "category": "strength", "difficulty": "beginner"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["is_custom"] is True
    assert data["name"] == "My Custom Curl"
    assert data["created_by_user_id"] is not None


# ── 10. Create custom exercise name required ─────────────────────────────────

@pytest.mark.asyncio
async def test_create_custom_exercise_name_required(client, auth_headers):
    resp = await client.post(
        "/api/exercises/custom",
        json={"muscle_primary": "biceps", "category": "strength"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


# ── 11. Get custom exercises ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_custom_exercises(client, auth_headers):
    await client.post("/api/exercises/custom", json={"name": "Custom A", "category": "strength", "difficulty": "beginner"}, headers=auth_headers)
    await client.post("/api/exercises/custom", json={"name": "Custom B", "category": "cardio", "difficulty": "intermediate"}, headers=auth_headers)

    resp = await client.get("/api/exercises/custom", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()
    names = [e["name"] for e in items]
    assert "Custom A" in names
    assert "Custom B" in names


# ── 12. Custom exercise not visible to others ─────────────────────────────────

@pytest.mark.asyncio
async def test_custom_exercise_not_visible_to_others(client, auth_headers, auth_headers2):
    await client.post("/api/exercises/custom", json={"name": "My Private Exercise", "category": "strength", "difficulty": "beginner"}, headers=auth_headers)

    resp = await client.get("/api/exercises/custom", headers=auth_headers2)
    assert resp.status_code == 200
    data = resp.json()
    names = [e["name"] for e in data]
    assert "My Private Exercise" not in names


# ── 13. Exercise video_url in response ────────────────────────────────────────

@pytest.mark.asyncio
async def test_exercise_video_url(client, auth_headers, exercise_id):
    resp = await client.get(f"/api/exercises/{exercise_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert "video_url" in resp.json()


# ── 14. Workout session has session_type ─────────────────────────────────────

@pytest.mark.asyncio
async def test_workout_session_has_session_type(client, auth_headers):
    r = await client.post("/api/workouts", json={"name": "Type Test", "session_type": "cardio"}, headers=auth_headers)
    session_id = r.json()["id"]

    resp = await client.get(f"/api/workouts/{session_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["session_type"] == "cardio"


# ── 15. Cardio fields in response after update ───────────────────────────────

@pytest.mark.asyncio
async def test_workout_cardio_fields_in_response(client, auth_headers):
    r = await client.post("/api/workouts", json={"name": "Cardio Run", "session_type": "cardio"}, headers=auth_headers)
    session_id = r.json()["id"]

    await client.patch(
        f"/api/workouts/{session_id}/cardio",
        json={"distance_km": 10.0, "avg_heart_rate": 155},
        headers=auth_headers,
    )

    resp = await client.get(f"/api/workouts/{session_id}", headers=auth_headers)
    data = resp.json()
    assert float(data["distance_km"]) == pytest.approx(10.0, rel=1e-2)
    assert data["avg_heart_rate"] == 155


# ── 16. Custom exercise slug uniqueness ──────────────────────────────────────

@pytest.mark.asyncio
async def test_custom_exercise_slug_unique(client, auth_headers):
    r1 = await client.post("/api/exercises/custom", json={"name": "Same Name Exercise", "category": "strength", "difficulty": "beginner"}, headers=auth_headers)
    r2 = await client.post("/api/exercises/custom", json={"name": "Same Name Exercise", "category": "strength", "difficulty": "beginner"}, headers=auth_headers)
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["slug"] != r2.json()["slug"]


# ── 17. Workout exercise superset in response ─────────────────────────────────

@pytest.mark.asyncio
async def test_workout_exercise_superset_in_response(client, auth_headers, exercise_id):
    r = await client.post("/api/workouts", json={"name": "SS Workout"}, headers=auth_headers)
    session_id = r.json()["id"]

    r2 = await client.post(
        f"/api/workouts/{session_id}/exercises",
        json={"exercise_library_id": exercise_id, "exercise_order": 1},
        headers=auth_headers,
    )
    we_id = r2.json()["id"]
    await client.patch(f"/api/workouts/exercises/{we_id}/superset", json={"superset_group": 3}, headers=auth_headers)

    resp = await client.get(f"/api/workouts/{session_id}", headers=auth_headers)
    exercises = resp.json()["exercises"]
    match = next((e for e in exercises if e["id"] == we_id), None)
    assert match is not None
    assert match["superset_group"] == 3


# ── 18. Update cardio invalid session ────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_cardio_invalid_session(client, auth_headers):
    resp = await client.patch(
        "/api/workouts/999999/cardio",
        json={"distance_km": 5.0},
        headers=auth_headers,
    )
    assert resp.status_code == 404


# ── 19. Create custom exercise requires auth ─────────────────────────────────

@pytest.mark.asyncio
async def test_create_custom_exercise_requires_auth(client):
    resp = await client.post(
        "/api/exercises/custom",
        json={"name": "Unauthorized Exercise", "category": "strength", "difficulty": "beginner"},
    )
    assert resp.status_code == 401


# ── 20. Cardio workout finishes correctly ────────────────────────────────────

@pytest.mark.asyncio
async def test_cardio_workout_finishes_correctly(client, auth_headers, exercise_id):
    r = await client.post("/api/workouts", json={"name": "Cardio Session", "session_type": "cardio"}, headers=auth_headers)
    session_id = r.json()["id"]

    await client.post(
        f"/api/workouts/{session_id}/exercises",
        json={"exercise_library_id": exercise_id, "exercise_order": 1},
        headers=auth_headers,
    )

    resp = await client.post(f"/api/workouts/{session_id}/finish", json={}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "finished"
