"""Week 6 Social Features Tests"""
import pytest
import pytest_asyncio


# Helper: complete a workout and return the workout id
async def complete_workout(client, headers) -> int:
    r = await client.post("/api/workouts", json={"name": "Test Workout"}, headers=headers)
    assert r.status_code == 201
    wid = r.json()["id"]
    r2 = await client.post(f"/api/workouts/{wid}/finish", json={}, headers=headers)
    assert r2.status_code == 200
    return wid


# Helper: get current user's ID
async def get_user_id(client, headers) -> int:
    r = await client.get("/api/auth/me", headers=headers)
    return r.json()["id"]


# ─── Follow / Unfollow ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_follow_user(client, auth_headers, auth_headers2):
    user2_id = await get_user_id(client, auth_headers2)
    r = await client.post(f"/api/social/follow/{user2_id}", headers=auth_headers)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_cannot_follow_self(client, auth_headers):
    user1_id = await get_user_id(client, auth_headers)
    r = await client.post(f"/api/social/follow/{user1_id}", headers=auth_headers)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_duplicate_follow(client, auth_headers, auth_headers2):
    user2_id = await get_user_id(client, auth_headers2)
    await client.post(f"/api/social/follow/{user2_id}", headers=auth_headers)
    r = await client.post(f"/api/social/follow/{user2_id}", headers=auth_headers)
    assert r.status_code == 400
    assert "Already following" in r.json()["detail"]


@pytest.mark.asyncio
async def test_unfollow_user(client, auth_headers, auth_headers2):
    user2_id = await get_user_id(client, auth_headers2)
    await client.post(f"/api/social/follow/{user2_id}", headers=auth_headers)
    r = await client.delete(f"/api/social/follow/{user2_id}", headers=auth_headers)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_unfollow_not_following(client, auth_headers, auth_headers2):
    user2_id = await get_user_id(client, auth_headers2)
    r = await client.delete(f"/api/social/follow/{user2_id}", headers=auth_headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_following_list(client, auth_headers, auth_headers2):
    user2_id = await get_user_id(client, auth_headers2)
    await client.post(f"/api/social/follow/{user2_id}", headers=auth_headers)
    r = await client.get("/api/social/following", headers=auth_headers)
    assert r.status_code == 200
    ids = [u["id"] for u in r.json()]
    assert user2_id in ids


@pytest.mark.asyncio
async def test_get_followers_list(client, auth_headers, auth_headers2):
    user2_id = await get_user_id(client, auth_headers2)
    await client.post(f"/api/social/follow/{user2_id}", headers=auth_headers)
    r = await client.get("/api/social/followers", headers=auth_headers2)
    assert r.status_code == 200
    ids = [u["id"] for u in r.json()]
    user1_id = await get_user_id(client, auth_headers)
    assert user1_id in ids


# ─── Feed ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_feed_returns_list(client, auth_headers):
    r = await client.get("/api/social/feed", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_feed_no_auth(client):
    r = await client.get("/api/social/feed")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_feed_contains_own_workout(client, auth_headers):
    await complete_workout(client, auth_headers)
    r = await client.get("/api/social/feed", headers=auth_headers)
    assert r.status_code == 200
    feed = r.json()
    workout_items = [i for i in feed if i["activity_type"] == "workout"]
    assert len(workout_items) >= 1
    assert "Completed workout" in workout_items[0]["title"]


# ─── Likes ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_like_feed_item(client, auth_headers):
    await complete_workout(client, auth_headers)
    feed_r = await client.get("/api/social/feed", headers=auth_headers)
    feed = feed_r.json()
    assert len(feed) >= 1
    feed_id = feed[0]["id"]
    r = await client.post(f"/api/social/feed/{feed_id}/like", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["liked"] is True
    assert r.json()["likes_count"] == 1


@pytest.mark.asyncio
async def test_unlike_feed_item(client, auth_headers):
    await complete_workout(client, auth_headers)
    feed_r = await client.get("/api/social/feed", headers=auth_headers)
    feed_id = feed_r.json()[0]["id"]
    await client.post(f"/api/social/feed/{feed_id}/like", headers=auth_headers)
    r = await client.post(f"/api/social/feed/{feed_id}/like", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["liked"] is False
    assert r.json()["likes_count"] == 0


# ─── Comments ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_comment(client, auth_headers):
    await complete_workout(client, auth_headers)
    feed_r = await client.get("/api/social/feed", headers=auth_headers)
    feed_id = feed_r.json()[0]["id"]
    r = await client.post(
        f"/api/social/feed/{feed_id}/comments",
        json={"content": "Great workout!"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["content"] == "Great workout!"
    assert data["feed_id"] == feed_id


@pytest.mark.asyncio
async def test_get_comments(client, auth_headers):
    await complete_workout(client, auth_headers)
    feed_r = await client.get("/api/social/feed", headers=auth_headers)
    feed_id = feed_r.json()[0]["id"]
    await client.post(
        f"/api/social/feed/{feed_id}/comments",
        json={"content": "Nice!"},
        headers=auth_headers,
    )
    r = await client.get(f"/api/social/feed/{feed_id}/comments", headers=auth_headers)
    assert r.status_code == 200
    comments = r.json()
    assert len(comments) >= 1
    assert any(c["content"] == "Nice!" for c in comments)


@pytest.mark.asyncio
async def test_delete_comment(client, auth_headers):
    await complete_workout(client, auth_headers)
    feed_r = await client.get("/api/social/feed", headers=auth_headers)
    feed_id = feed_r.json()[0]["id"]
    add_r = await client.post(
        f"/api/social/feed/{feed_id}/comments",
        json={"content": "To be deleted"},
        headers=auth_headers,
    )
    comment_id = add_r.json()["id"]
    del_r = await client.delete(
        f"/api/social/feed/{feed_id}/comments/{comment_id}",
        headers=auth_headers,
    )
    assert del_r.status_code == 200
    comments_r = await client.get(f"/api/social/feed/{feed_id}/comments", headers=auth_headers)
    assert not any(c["id"] == comment_id for c in comments_r.json())


@pytest.mark.asyncio
async def test_delete_other_users_comment(client, auth_headers, auth_headers2):
    await complete_workout(client, auth_headers)
    feed_r = await client.get("/api/social/feed", headers=auth_headers)
    feed_id = feed_r.json()[0]["id"]
    add_r = await client.post(
        f"/api/social/feed/{feed_id}/comments",
        json={"content": "User1's comment"},
        headers=auth_headers,
    )
    comment_id = add_r.json()["id"]
    r = await client.delete(
        f"/api/social/feed/{feed_id}/comments/{comment_id}",
        headers=auth_headers2,
    )
    assert r.status_code == 403


# ─── Public Profile ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_public_profile(client, auth_headers, auth_headers2):
    user2_id = await get_user_id(client, auth_headers2)
    r = await client.get(f"/api/users/{user2_id}/profile", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "username" in data
    assert "email" not in data
    assert "followers_count" in data
    assert "following_count" in data


@pytest.mark.asyncio
async def test_public_profile_not_found(client, auth_headers):
    r = await client.get("/api/users/99999/profile", headers=auth_headers)
    assert r.status_code == 404


# ─── User Search ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_user_search(client, auth_headers, auth_headers2):
    r = await client.get("/api/users/search?q=testuser", headers=auth_headers)
    assert r.status_code == 200
    results = r.json()
    assert isinstance(results, list)
    assert len(results) >= 1
    usernames = [u["username"] for u in results]
    assert any("testuser" in un for un in usernames)


@pytest.mark.asyncio
async def test_user_search_no_auth(client):
    r = await client.get("/api/users/search?q=test")
    assert r.status_code == 401
