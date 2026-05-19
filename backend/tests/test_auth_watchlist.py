def _register_and_login(client, username="alice", password="secret123"):
    response = client.post("/api/auth/register", json={"username": username, "password": password})
    assert response.status_code == 201
    return response.json()["access_token"]


def test_register_and_duplicate(client):
    token = _register_and_login(client)
    assert token

    dup = client.post("/api/auth/register", json={"username": "alice", "password": "secret123"})
    assert dup.status_code == 409


def test_watchlist_crud(client):
    token = _register_and_login(client, "bob")
    headers = {"Authorization": f"Bearer {token}"}

    empty = client.get("/api/watchlist", headers=headers)
    assert empty.status_code == 200
    assert empty.json() == []

    add = client.post(
        "/api/watchlist",
        headers=headers,
        json={"tmdb_id": 27205, "title": "Inception", "poster_path": "/x.jpg"},
    )
    assert add.status_code == 201
    assert add.json()["title"] == "Inception"

    dup = client.post(
        "/api/watchlist",
        headers=headers,
        json={"tmdb_id": 27205, "title": "Inception"},
    )
    assert dup.status_code == 409

    listed = client.get("/api/watchlist", headers=headers)
    assert len(listed.json()) == 1

    remove = client.delete("/api/watchlist/27205", headers=headers)
    assert remove.status_code == 204


def test_watchlist_requires_auth(client):
    response = client.get("/api/watchlist")
    assert response.status_code == 401
