"""Plant CRUD, watering history, reminders, and cross-user isolation."""

PLANT = {"name": "Fern", "species": "Boston Fern", "watering_interval_days": 5}


async def _create(client, headers, **overrides):
    r = await client.post("/api/v1/plants", json={**PLANT, **overrides}, headers=headers)
    assert r.status_code == 201
    return r.json()


async def test_create_and_list(client, auth_headers):
    headers, _ = auth_headers
    plant = await _create(client, headers)
    assert plant["user_id"]
    assert plant["next_watering_at"]  # scheduled from creation + interval

    r = await client.get("/api/v1/plants", headers=headers)
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["name"] == "Fern"
    # Summary shape should not embed full history
    assert "watering_history" not in items[0]


async def test_plants_require_auth(client):
    r = await client.get("/api/v1/plants")
    assert r.status_code == 401


async def test_get_update_delete(client, auth_headers):
    headers, _ = auth_headers
    plant = await _create(client, headers)

    got = await client.get(f"/api/v1/plants/{plant['id']}", headers=headers)
    assert got.status_code == 200
    assert got.json()["species"] == "Boston Fern"

    upd = await client.patch(
        f"/api/v1/plants/{plant['id']}",
        json={"location": "Living room", "watering_interval_days": 3},
        headers=headers,
    )
    assert upd.status_code == 200
    body = upd.json()
    assert body["location"] == "Living room"
    # Interval change recomputes next watering
    assert body["next_watering_at"] != plant["next_watering_at"]

    dele = await client.delete(f"/api/v1/plants/{plant['id']}", headers=headers)
    assert dele.status_code == 204
    assert (await client.get(f"/api/v1/plants/{plant['id']}", headers=headers)).status_code == 404


async def test_validation_rejects_bad_input(client, auth_headers):
    headers, _ = auth_headers
    r = await client.post("/api/v1/plants", json={"name": ""}, headers=headers)
    assert r.status_code == 422
    r = await client.post(
        "/api/v1/plants", json={"name": "X", "watering_interval_days": 0}, headers=headers
    )
    assert r.status_code == 422
    r = await client.post(
        "/api/v1/plants", json={"name": "X", "watering_interval_days": 9999}, headers=headers
    )
    assert r.status_code == 422


async def test_watering_records_and_history(client, auth_headers):
    headers, _ = auth_headers
    plant = await _create(client, headers)

    r = await client.post(
        f"/api/v1/plants/{plant['id']}/waterings",
        json={"notes": "after repotting"},
        headers=headers,
    )
    assert r.status_code == 200
    watered = r.json()
    assert watered["last_watered_at"] is not None
    assert len(watered["watering_history"]) == 1
    assert watered["next_watering_at"] is not None

    hist = await client.get(f"/api/v1/plants/{plant['id']}/waterings", headers=headers)
    assert hist.status_code == 200
    assert len(hist.json()) == 1
    assert hist.json()[0]["notes"] == "after repotting"


async def test_watering_rejects_future_time(client, auth_headers):
    headers, _ = auth_headers
    plant = await _create(client, headers)
    from datetime import datetime, timedelta, timezone

    future = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    r = await client.post(
        f"/api/v1/plants/{plant['id']}/waterings",
        json={"watered_at": future},
        headers=headers,
    )
    assert r.status_code == 422


async def test_reminder_update_and_postpone(client, auth_headers):
    headers, _ = auth_headers
    plant = await _create(client, headers)

    r = await client.patch(
        f"/api/v1/plants/{plant['id']}/reminder",
        json={"reminder_enabled": False, "watering_interval_days": 10},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["reminder_enabled"] is False
    assert r.json()["watering_interval_days"] == 10

    before = r.json()["next_watering_at"]
    r = await client.post(
        f"/api/v1/plants/{plant['id']}/postpone", json={"days": 2}, headers=headers
    )
    assert r.status_code == 200
    assert r.json()["next_watering_at"] > before

    r = await client.post(
        f"/api/v1/plants/{plant['id']}/postpone", json={"days": 99}, headers=headers
    )
    assert r.status_code == 422


async def test_cross_user_isolation(client, auth_headers, other_auth_headers):
    """User B must not see, modify, water, or delete user A's plants."""
    headers_a, _ = auth_headers
    headers_b, _ = other_auth_headers

    plant = await _create(client, headers_a)

    # List does not include other users' plants
    r = await client.get("/api/v1/plants", headers=headers_b)
    assert r.json() == []

    # Direct reads are 404 (not 403 — do not reveal existence)
    assert (
        await client.get(f"/api/v1/plants/{plant['id']}", headers=headers_b)
    ).status_code == 404
    assert (
        await client.patch(
            f"/api/v1/plants/{plant['id']}", json={"name": "hacked"}, headers=headers_b
        )
    ).status_code == 404
    assert (
        await client.post(
            f"/api/v1/plants/{plant['id']}/waterings", json={}, headers=headers_b
        )
    ).status_code == 404
    assert (
        await client.delete(f"/api/v1/plants/{plant['id']}", headers=headers_b)
    ).status_code == 404
    assert (
        await client.get(f"/api/v1/plants/{plant['id']}/waterings", headers=headers_b)
    ).status_code == 404

    # User A's plant untouched
    r = await client.get(f"/api/v1/plants/{plant['id']}", headers=headers_a)
    assert r.status_code == 200
    assert r.json()["name"] == "Fern"


async def test_client_cannot_spoof_user_id(client, auth_headers, other_auth_headers):
    """A client-supplied user_id field must be ignored — identity comes from JWT."""
    headers_a, user_a = auth_headers
    headers_b, user_b = other_auth_headers
    r = await client.post(
        "/api/v1/plants",
        json={"name": "Spoof", "user_id": user_a.id},  # B claims A's id
        headers=headers_b,
    )
    assert r.status_code == 201
    assert r.json()["user_id"] == user_b.id  # stored owner is B, not A
