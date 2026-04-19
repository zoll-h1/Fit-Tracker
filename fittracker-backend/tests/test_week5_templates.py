"""
Week 5 — Workout Templates: 20 tests
SQLite in-memory; FK not enforced so exercise_library_id=1 is fine.
"""
import pytest


# ─── helpers ─────────────────────────────────────────────────────────────────

EXERCISE_ID = 1  # SQLite won't enforce FK, safe to use

def _template_payload(**kwargs):
    data = {"name": "Test Template", "exercises": []}
    data.update(kwargs)
    return data


async def _create_template(client, headers, **kwargs) -> dict:
    resp = await client.post("/api/templates", json=_template_payload(**kwargs), headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def _create_workout(client, headers) -> dict:
    resp = await client.post("/api/workouts", json={"name": "Test WO"}, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ─── Tests ───────────────────────────────────────────────────────────────────

async def test_create_template_success(client, auth_headers):
    resp = await client.post(
        "/api/templates",
        json={
            "name": "Push Day",
            "exercises": [
                {"exercise_library_id": EXERCISE_ID, "exercise_order": 1, "target_sets": 3, "target_reps": 10},
                {"exercise_library_id": EXERCISE_ID, "exercise_order": 2, "target_sets": 4, "target_reps": 8},
            ],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["name"] == "Push Day"
    assert data["exercise_count"] == 2


async def test_create_template_no_auth(client):
    resp = await client.post("/api/templates", json={"name": "X"})
    assert resp.status_code == 401


async def test_create_template_empty_name(client, auth_headers):
    resp = await client.post("/api/templates", json={"name": ""}, headers=auth_headers)
    assert resp.status_code == 422


async def test_get_my_templates(client, auth_headers):
    await _create_template(client, auth_headers, name="My Template")
    resp = await client.get("/api/templates?mine=true", headers=auth_headers)
    assert resp.status_code == 200
    names = [t["name"] for t in resp.json()]
    assert "My Template" in names


async def test_get_public_templates(client, auth_headers, auth_headers2):
    await _create_template(client, auth_headers, name="Public One", is_public=True)
    resp = await client.get("/api/templates?public=true", headers=auth_headers2)
    assert resp.status_code == 200
    names = [t["name"] for t in resp.json()]
    assert "Public One" in names


async def test_get_template_detail(client, auth_headers):
    t = await _create_template(
        client, auth_headers, name="Detail Test",
        exercises=[{"exercise_library_id": EXERCISE_ID, "exercise_order": 1}],
    )
    resp = await client.get(f"/api/templates/{t['id']}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "exercises" in data
    assert isinstance(data["exercises"], list)


async def test_get_template_detail_not_found(client, auth_headers):
    resp = await client.get("/api/templates/99999", headers=auth_headers)
    assert resp.status_code == 404


async def test_update_template(client, auth_headers):
    t = await _create_template(client, auth_headers, name="Old Name")
    resp = await client.put(
        f"/api/templates/{t['id']}",
        json={"name": "New Name"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


async def test_update_template_not_owner(client, auth_headers, auth_headers2):
    t = await _create_template(client, auth_headers, name="Owner Template")
    resp = await client.put(
        f"/api/templates/{t['id']}",
        json={"name": "Hijacked"},
        headers=auth_headers2,
    )
    assert resp.status_code == 403


async def test_delete_template(client, auth_headers):
    t = await _create_template(client, auth_headers, name="To Delete")
    del_resp = await client.delete(f"/api/templates/{t['id']}", headers=auth_headers)
    assert del_resp.status_code == 204
    get_resp = await client.get(f"/api/templates/{t['id']}", headers=auth_headers)
    assert get_resp.status_code == 404


async def test_delete_template_not_owner(client, auth_headers, auth_headers2):
    t = await _create_template(client, auth_headers, name="Protected")
    resp = await client.delete(f"/api/templates/{t['id']}", headers=auth_headers2)
    assert resp.status_code == 403


async def test_start_from_template(client, auth_headers):
    t = await _create_template(
        client, auth_headers, name="Starter",
        exercises=[
            {"exercise_library_id": EXERCISE_ID, "exercise_order": 1},
            {"exercise_library_id": EXERCISE_ID, "exercise_order": 2},
        ],
    )
    resp = await client.post(f"/api/templates/{t['id']}/start", headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["status"] == "in_progress"
    assert len(data["exercises"]) == 2


async def test_start_from_template_increments_times_used(client, auth_headers):
    t = await _create_template(client, auth_headers, name="Counter")
    await client.post(f"/api/templates/{t['id']}/start", headers=auth_headers)
    detail = await client.get(f"/api/templates/{t['id']}", headers=auth_headers)
    assert detail.json()["times_used"] == 1


async def test_start_nonexistent_template(client, auth_headers):
    resp = await client.post("/api/templates/99999/start", headers=auth_headers)
    assert resp.status_code == 404


async def test_save_workout_as_template(client, auth_headers, exercise_id):
    wo = await _create_workout(client, auth_headers)
    # Add an exercise to the workout using the seeded exercise_id
    resp = await client.post(
        f"/api/workouts/{wo['id']}/exercises",
        json={"exercise_library_id": exercise_id, "exercise_order": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    resp = await client.post(
        f"/api/workouts/{wo['id']}/save-as-template",
        json={"name": "From Workout", "is_public": False},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "From Workout"
    assert data["exercise_count"] == 1


async def test_save_as_template_not_owner(client, auth_headers, auth_headers2):
    wo = await _create_workout(client, auth_headers)
    resp = await client.post(
        f"/api/workouts/{wo['id']}/save-as-template",
        json={"name": "Steal"},
        headers=auth_headers2,
    )
    assert resp.status_code == 404


async def test_template_exercises_ordered(client, auth_headers):
    t = await _create_template(
        client, auth_headers, name="Ordered",
        exercises=[
            {"exercise_library_id": EXERCISE_ID, "exercise_order": 3},
            {"exercise_library_id": EXERCISE_ID, "exercise_order": 1},
            {"exercise_library_id": EXERCISE_ID, "exercise_order": 2},
        ],
    )
    resp = await client.get(f"/api/templates/{t['id']}", headers=auth_headers)
    exercises = resp.json()["exercises"]
    orders = [e["exercise_order"] for e in exercises]
    assert orders == sorted(orders)


async def test_private_template_not_visible_to_others(client, auth_headers, auth_headers2):
    await _create_template(client, auth_headers, name="Secret Template", is_public=False)
    resp = await client.get("/api/templates?public=true", headers=auth_headers2)
    assert resp.status_code == 200
    names = [t["name"] for t in resp.json()]
    assert "Secret Template" not in names


async def test_create_template_with_no_exercises(client, auth_headers):
    resp = await client.post(
        "/api/templates",
        json={"name": "Empty Template", "exercises": []},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["exercise_count"] == 0


async def test_update_template_make_public(client, auth_headers, auth_headers2):
    t = await _create_template(client, auth_headers, name="Was Private", is_public=False)
    await client.put(
        f"/api/templates/{t['id']}",
        json={"is_public": True},
        headers=auth_headers,
    )
    resp = await client.get("/api/templates?public=true", headers=auth_headers2)
    names = [item["name"] for item in resp.json()]
    assert "Was Private" in names
