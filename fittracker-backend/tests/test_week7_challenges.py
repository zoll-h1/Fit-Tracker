"""Week 7 — Challenges feature tests."""

import pytest
from datetime import date, timedelta


def _challenge_payload(**kwargs):
    today = date.today()
    return {
        "title": "Test Challenge",
        "description": "A test challenge",
        "challenge_type": "total_workouts",
        "target_value": 10,
        "start_date": str(today),
        "end_date": str(today + timedelta(days=30)),
        "is_public": True,
        **kwargs,
    }


# 1. Create challenge → 201, creator auto-joined
@pytest.mark.asyncio
async def test_create_challenge(client, auth_headers):
    resp = await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["participant_count"] == 1
    assert data["is_joined"] is True


# 2. No auth → 401
@pytest.mark.asyncio
async def test_create_challenge_no_auth(client):
    resp = await client.post("/api/challenges", json=_challenge_payload())
    assert resp.status_code == 401


# 3. Invalid type → 422
@pytest.mark.asyncio
async def test_create_challenge_invalid_type(client, auth_headers):
    resp = await client.post(
        "/api/challenges",
        json=_challenge_payload(challenge_type="invalid"),
        headers=auth_headers,
    )
    assert resp.status_code == 422


# 4. End date before start date → 422
@pytest.mark.asyncio
async def test_create_challenge_end_before_start(client, auth_headers):
    today = date.today()
    resp = await client.post(
        "/api/challenges",
        json=_challenge_payload(
            start_date=str(today + timedelta(days=10)),
            end_date=str(today),
        ),
        headers=auth_headers,
    )
    assert resp.status_code == 422


# 5. List active challenges
@pytest.mark.asyncio
async def test_list_challenges(client, auth_headers):
    await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    resp = await client.get("/api/challenges?status=active", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(c["title"] == "Test Challenge" for c in data)


# 6. List mine
@pytest.mark.asyncio
async def test_list_mine(client, auth_headers):
    await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    resp = await client.get("/api/challenges?mine=true", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert any(c["title"] == "Test Challenge" for c in data)


# 7. Get challenge detail with participants
@pytest.mark.asyncio
async def test_get_challenge_detail(client, auth_headers):
    create_resp = await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    cid = create_resp.json()["id"]
    resp = await client.get(f"/api/challenges/{cid}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "participants" in data
    assert len(data["participants"]) == 1


# 8. Not found → 404
@pytest.mark.asyncio
async def test_get_challenge_not_found(client, auth_headers):
    resp = await client.get("/api/challenges/99999", headers=auth_headers)
    assert resp.status_code == 404


# 9. Update challenge title
@pytest.mark.asyncio
async def test_update_challenge(client, auth_headers):
    create_resp = await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    cid = create_resp.json()["id"]
    resp = await client.put(f"/api/challenges/{cid}", json={"title": "Updated Title"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


# 10. Non-creator update → 403
@pytest.mark.asyncio
async def test_update_challenge_not_creator(client, auth_headers, auth_headers2):
    create_resp = await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    cid = create_resp.json()["id"]
    resp = await client.put(f"/api/challenges/{cid}", json={"title": "Hacked"}, headers=auth_headers2)
    assert resp.status_code == 403


# 11. Cancel challenge → status=cancelled
@pytest.mark.asyncio
async def test_cancel_challenge(client, auth_headers):
    create_resp = await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    cid = create_resp.json()["id"]
    del_resp = await client.delete(f"/api/challenges/{cid}", headers=auth_headers)
    assert del_resp.status_code in (200, 204)
    get_resp = await client.get(f"/api/challenges/{cid}", headers=auth_headers)
    assert get_resp.json()["status"] == "cancelled"


# 12. Non-creator cancel → 403
@pytest.mark.asyncio
async def test_cancel_not_creator(client, auth_headers, auth_headers2):
    create_resp = await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    cid = create_resp.json()["id"]
    resp = await client.delete(f"/api/challenges/{cid}", headers=auth_headers2)
    assert resp.status_code == 403


# 13. user2 joins user1's challenge
@pytest.mark.asyncio
async def test_join_challenge(client, auth_headers, auth_headers2):
    create_resp = await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    cid = create_resp.json()["id"]
    resp = await client.post(f"/api/challenges/{cid}/join", headers=auth_headers2)
    assert resp.status_code == 200
    detail = await client.get(f"/api/challenges/{cid}", headers=auth_headers)
    assert detail.json()["participant_count"] == 2


# 14. Join twice → 400
@pytest.mark.asyncio
async def test_join_already_joined(client, auth_headers, auth_headers2):
    create_resp = await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    cid = create_resp.json()["id"]
    await client.post(f"/api/challenges/{cid}/join", headers=auth_headers2)
    resp = await client.post(f"/api/challenges/{cid}/join", headers=auth_headers2)
    assert resp.status_code == 400


# 15. Join then leave
@pytest.mark.asyncio
async def test_leave_challenge(client, auth_headers, auth_headers2):
    create_resp = await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    cid = create_resp.json()["id"]
    await client.post(f"/api/challenges/{cid}/join", headers=auth_headers2)
    leave_resp = await client.delete(f"/api/challenges/{cid}/leave", headers=auth_headers2)
    assert leave_resp.status_code == 200
    detail = await client.get(f"/api/challenges/{cid}", headers=auth_headers)
    assert detail.json()["participant_count"] == 1


# 16. Creator cannot leave own challenge → 400
@pytest.mark.asyncio
async def test_creator_cannot_leave(client, auth_headers):
    create_resp = await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    cid = create_resp.json()["id"]
    resp = await client.delete(f"/api/challenges/{cid}/leave", headers=auth_headers)
    assert resp.status_code == 400


# 17. Join nonexistent challenge → 404
@pytest.mark.asyncio
async def test_join_nonexistent_challenge(client, auth_headers):
    resp = await client.post("/api/challenges/99999/join", headers=auth_headers)
    assert resp.status_code == 404


# 18. Leaderboard has 2 entries after user2 joins
@pytest.mark.asyncio
async def test_leaderboard(client, auth_headers, auth_headers2):
    create_resp = await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    cid = create_resp.json()["id"]
    await client.post(f"/api/challenges/{cid}/join", headers=auth_headers2)
    resp = await client.get(f"/api/challenges/{cid}/leaderboard", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


# 19. Leaderboard sorted by progress descending
@pytest.mark.asyncio
async def test_leaderboard_sorted_by_progress(client, auth_headers, auth_headers2):
    create_resp = await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    cid = create_resp.json()["id"]
    await client.post(f"/api/challenges/{cid}/join", headers=auth_headers2)
    resp = await client.get(f"/api/challenges/{cid}/leaderboard", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    progresses = [e["current_progress"] for e in data]
    assert progresses == sorted(progresses, reverse=True)


# 20. Leave challenge not joined → 404
@pytest.mark.asyncio
async def test_leave_nonexistent(client, auth_headers, auth_headers2):
    create_resp = await client.post("/api/challenges", json=_challenge_payload(), headers=auth_headers)
    cid = create_resp.json()["id"]
    # user2 never joined
    resp = await client.delete(f"/api/challenges/{cid}/leave", headers=auth_headers2)
    assert resp.status_code == 404
