"""Week 10 — Trainer features tests."""

import pytest
import app.models.trainer  # ensure models are registered  # noqa: F401


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _become_trainer(client, headers):
    resp = await client.post("/api/trainer/become-trainer", headers=headers)
    assert resp.status_code == 200
    return resp


async def _register_and_login(client, username, email):
    await client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": "TestPass123!",
        "full_name": "Extra User",
    })
    resp = await client.post("/api/auth/login", json={"email": email, "password": "TestPass123!"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _program_payload(**kwargs):
    return {"title": "Strength Program", "duration_weeks": 4, "difficulty": "intermediate", "is_public": False, **kwargs}


# ── Tests ─────────────────────────────────────────────────────────────────────

# 1. become-trainer
@pytest.mark.asyncio
async def test_become_trainer(client, auth_headers):
    resp = await client.post("/api/trainer/become-trainer", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "trainer"


# 2. can call become-trainer again
@pytest.mark.asyncio
async def test_become_trainer_again(client, auth_headers):
    await client.post("/api/trainer/become-trainer", headers=auth_headers)
    resp = await client.post("/api/trainer/become-trainer", headers=auth_headers)
    assert resp.status_code == 200


# 3. create program requires trainer role
@pytest.mark.asyncio
async def test_create_program_requires_trainer(client):
    # Use a fresh user that has never been promoted to trainer
    headers = await _register_and_login(client, "nontrainer_t3", "nontrainer_t3@example.com")
    resp = await client.post("/api/trainer/programs", json=_program_payload(), headers=headers)
    assert resp.status_code == 403


# 4. trainer creates program with no days
@pytest.mark.asyncio
async def test_create_program_empty_days(client, auth_headers):
    await _become_trainer(client, auth_headers)
    resp = await client.post("/api/trainer/programs", json=_program_payload(), headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Strength Program"
    assert data["days"] == []


# 5. trainer creates program with 1 day + 1 exercise
@pytest.mark.asyncio
async def test_create_program_with_days(client, auth_headers, exercise_id):
    await _become_trainer(client, auth_headers)
    payload = _program_payload(days=[{
        "week_number": 1,
        "day_number": 1,
        "name": "Chest Day",
        "exercises": [{
            "exercise_id": exercise_id,
            "exercise_order": 1,
            "sets": 4,
            "reps": "8-12",
        }]
    }])
    resp = await client.post("/api/trainer/programs", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["days"]) == 1
    assert len(data["days"][0]["exercises"]) == 1
    assert "exercise_name" in data["days"][0]["exercises"][0]
    assert data["days"][0]["exercises"][0]["reps"] == "8-12"


# 6. list my programs — empty
@pytest.mark.asyncio
async def test_list_my_programs_empty(client):
    # Use a fresh trainer who has created no programs
    headers = await _register_and_login(client, "freshtrainer_t6", "freshtrainer_t6@example.com")
    await _become_trainer(client, headers)
    resp = await client.get("/api/trainer/programs", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


# 7. list my programs — 2 items
@pytest.mark.asyncio
async def test_list_my_programs(client):
    headers = await _register_and_login(client, "freshtrainer_t7", "freshtrainer_t7@example.com")
    await _become_trainer(client, headers)
    await client.post("/api/trainer/programs", json=_program_payload(title="Program A"), headers=headers)
    await client.post("/api/trainer/programs", json=_program_payload(title="Program B"), headers=headers)
    resp = await client.get("/api/trainer/programs", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    titles = {p["title"] for p in data}
    assert titles == {"Program A", "Program B"}


# 8. get program detail
@pytest.mark.asyncio
async def test_get_program_detail(client, auth_headers):
    await _become_trainer(client, auth_headers)
    create_resp = await client.post("/api/trainer/programs", json=_program_payload(title="Detail Test"), headers=auth_headers)
    pid = create_resp.json()["id"]
    resp = await client.get(f"/api/trainer/programs/{pid}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Detail Test"
    assert "days" in data


# 9. get program not found
@pytest.mark.asyncio
async def test_get_program_not_found(client, auth_headers):
    resp = await client.get("/api/trainer/programs/99999", headers=auth_headers)
    assert resp.status_code == 404


# 10. trainer B cannot access trainer A's private program
@pytest.mark.asyncio
async def test_get_private_program_other_user(client, auth_headers):
    await _become_trainer(client, auth_headers)
    create_resp = await client.post("/api/trainer/programs", json=_program_payload(is_public=False), headers=auth_headers)
    pid = create_resp.json()["id"]

    headers_b = await _register_and_login(client, "trainerb10", "trainerb10@example.com")
    resp = await client.get(f"/api/trainer/programs/{pid}", headers=headers_b)
    assert resp.status_code == 403


# 11. public programs list
@pytest.mark.asyncio
async def test_list_public_programs(client, auth_headers):
    await _become_trainer(client, auth_headers)
    await client.post("/api/trainer/programs", json=_program_payload(title="Public One", is_public=True), headers=auth_headers)
    resp = await client.get("/api/trainer/programs/public", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert any(p["title"] == "Public One" for p in data)


# 12. delete program
@pytest.mark.asyncio
async def test_delete_program(client, auth_headers):
    await _become_trainer(client, auth_headers)
    create_resp = await client.post("/api/trainer/programs", json=_program_payload(), headers=auth_headers)
    pid = create_resp.json()["id"]
    del_resp = await client.delete(f"/api/trainer/programs/{pid}", headers=auth_headers)
    assert del_resp.status_code == 204
    get_resp = await client.get(f"/api/trainer/programs/{pid}", headers=auth_headers)
    assert get_resp.status_code == 404


# 13. trainer B cannot delete trainer A's program
@pytest.mark.asyncio
async def test_delete_program_other_trainer(client, auth_headers):
    await _become_trainer(client, auth_headers)
    create_resp = await client.post("/api/trainer/programs", json=_program_payload(), headers=auth_headers)
    pid = create_resp.json()["id"]

    headers_b = await _register_and_login(client, "trainerc13", "trainerc13@example.com")
    await client.post("/api/trainer/become-trainer", headers=headers_b)
    del_resp = await client.delete(f"/api/trainer/programs/{pid}", headers=headers_b)
    assert del_resp.status_code == 403


# 14. assign program to client
@pytest.mark.asyncio
async def test_assign_program(client, auth_headers):
    await _become_trainer(client, auth_headers)
    create_resp = await client.post("/api/trainer/programs", json=_program_payload(), headers=auth_headers)
    pid = create_resp.json()["id"]

    client_headers = await _register_and_login(client, "client14", "client14@example.com")
    resp = await client.post(
        f"/api/trainer/programs/{pid}/assign",
        json={"client_username": "client14"},
        headers=auth_headers
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["client_username"] == "client14"
    assert data["status"] == "active"


# 15. assign to unknown client → 404
@pytest.mark.asyncio
async def test_assign_program_unknown_client(client, auth_headers):
    await _become_trainer(client, auth_headers)
    create_resp = await client.post("/api/trainer/programs", json=_program_payload(), headers=auth_headers)
    pid = create_resp.json()["id"]
    resp = await client.post(
        f"/api/trainer/programs/{pid}/assign",
        json={"client_username": "nobody_exists_xyz"},
        headers=auth_headers
    )
    assert resp.status_code == 404


# 16. get my clients — empty
@pytest.mark.asyncio
async def test_get_my_clients_empty(client):
    headers = await _register_and_login(client, "freshtrainer_t16", "freshtrainer_t16@example.com")
    await _become_trainer(client, headers)
    resp = await client.get("/api/trainer/clients", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


# 17. get my clients after assignment
@pytest.mark.asyncio
async def test_get_my_clients(client):
    headers = await _register_and_login(client, "freshtrainer_t17", "freshtrainer_t17@example.com")
    await _become_trainer(client, headers)
    create_resp = await client.post("/api/trainer/programs", json=_program_payload(), headers=headers)
    pid = create_resp.json()["id"]

    await _register_and_login(client, "client_17b", "client_17b@example.com")
    await client.post(
        f"/api/trainer/programs/{pid}/assign",
        json={"client_username": "client_17b"},
        headers=headers
    )
    resp = await client.get("/api/trainer/clients", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["username"] == "client_17b"
    assert "total_workouts" in data[0]
    assert "assigned_programs" in data[0]


# 18. assigned user sees their assignment
@pytest.mark.asyncio
async def test_my_assignments_as_client(client, auth_headers):
    await _become_trainer(client, auth_headers)
    create_resp = await client.post("/api/trainer/programs", json=_program_payload(title="Client Prog"), headers=auth_headers)
    pid = create_resp.json()["id"]

    client_headers = await _register_and_login(client, "client18", "client18@example.com")
    await client.post(
        f"/api/trainer/programs/{pid}/assign",
        json={"client_username": "client18"},
        headers=auth_headers
    )
    resp = await client.get("/api/trainer/my-assignments", headers=client_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["program_id"] == pid


# 19. GET /programs without token → 401
@pytest.mark.asyncio
async def test_program_auth_required(client):
    resp = await client.get("/api/trainer/programs")
    assert resp.status_code == 401


# 20. GET /programs/public without token → 401
@pytest.mark.asyncio
async def test_public_programs_auth_required(client):
    resp = await client.get("/api/trainer/programs/public")
    assert resp.status_code == 401
