import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as c:
        yield c


SONG = {"title": "Aquarela", "artist": "Toquinho", "duration_seconds": 240, "genre": "MPB"}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_song_crud(client):
    r = client.post("/songs", json=SONG)
    assert r.status_code == 201
    sid = r.json()["id"]

    assert client.get(f"/songs/{sid}").json()["title"] == "Aquarela"
    r = client.put(f"/songs/{sid}", json={"title": "Aquarela (Ao Vivo)"})
    assert r.json()["title"] == "Aquarela (Ao Vivo)"
    assert len(client.get("/songs", params={"genre": "MPB"}).json()) == 1
    assert client.delete(f"/songs/{sid}").status_code == 204
    assert client.get(f"/songs/{sid}").status_code == 404


def test_song_validation(client):
    assert client.post("/songs", json={**SONG, "duration_seconds": 0}).status_code == 422


def test_playlist_flow(client):
    sid = client.post("/songs", json=SONG).json()["id"]
    pid = client.post("/playlists", json={"name": "Favoritas"}).json()["id"]

    r = client.post(f"/playlists/{pid}/songs/{sid}")
    assert r.status_code == 200 and len(r.json()["songs"]) == 1
    assert client.post(f"/playlists/{pid}/songs/{sid}").status_code == 409

    r = client.delete(f"/playlists/{pid}/songs/{sid}")
    assert r.json()["songs"] == []
    assert client.delete(f"/playlists/{pid}").status_code == 204
