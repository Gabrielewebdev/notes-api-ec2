import pytest
from fastapi.testclient import TestClient

import notes.api as api
from notes.service import InMemoryNoteRepository, NotesService


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        api, "service", NotesService(InMemoryNoteRepository())
    )
    with TestClient(api.app) as client:
        yield client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_note_lifecycle(client):
    response = client.post(
        "/notes", json={"title": " Test ", "content": "Docker"}
    )
    assert response.status_code == 201
    note = response.json()
    assert note["title"] == "Test"

    response = client.get(f"/notes/{note['id']}")
    assert response.status_code == 200
    assert response.json() == note

    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json()["notes"] == [note]

    assert client.delete(f"/notes/{note['id']}").status_code == 204
    assert client.get(f"/notes/{note['id']}").status_code == 404
    assert client.delete(f"/notes/{note['id']}").status_code == 404


@pytest.mark.parametrize("title", ["", "   ", "x" * 201])
def test_invalid_title(client, title):
    assert client.post("/notes", json={"title": title}).status_code == 400


def test_invalid_content(client):
    response = client.post(
        "/notes", json={"title": "Test", "content": "x" * 10001}
    )
    assert response.status_code == 400


def test_invalid_type(client):
    assert client.post("/notes", json={"title": 123}).status_code == 422


@pytest.mark.parametrize("limit", [0, 101])
def test_invalid_limit(client, limit):
    assert client.get("/notes", params={"limit": limit}).status_code == 400


def test_invalid_cursor(client):
    response = client.get("/notes", params={"cursor": "invalid/cursor"})
    assert response.status_code == 400


def test_pagination(client):
    for title in ["Prima", "Seconda", "Terza"]:
        assert client.post("/notes", json={"title": title}).status_code == 201

    first = client.get("/notes", params={"limit": 2}).json()
    assert len(first["notes"]) == 2
    assert first["next_cursor"] is not None

    second = client.get(
        "/notes", params={"limit": 2, "cursor": first["next_cursor"]}
    ).json()
    assert len(second["notes"]) == 1
    assert second["next_cursor"] is None

    ids = [note["id"] for note in first["notes"] + second["notes"]]
    assert len(set(ids)) == 3
