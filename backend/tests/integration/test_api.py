def test_create_and_get_note(client):
    response = client.post("/api/notes/", json={"title": "Integration Note", "content": "Content"})
    assert response.status_code == 201
    note = response.json()
    assert note["title"] == "Integration Note"

    response = client.get(f"/api/notes/{note['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Integration Note"


def test_list_notes(client):
    client.post("/api/notes/", json={"title": "Note 1", "content": ""})
    client.post("/api/notes/", json={"title": "Note 2", "content": ""})
    response = client.get("/api/notes/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_note(client):
    response = client.post("/api/notes/", json={"title": "Old", "content": ""})
    note_id = response.json()["id"]
    response = client.patch(f"/api/notes/{note_id}", json={"title": "New"})
    assert response.status_code == 200
    assert response.json()["title"] == "New"


def test_delete_note_returns_204(client):
    response = client.post("/api/notes/", json={"title": "Delete Me", "content": ""})
    note_id = response.json()["id"]
    assert client.delete(f"/api/notes/{note_id}").status_code == 204
    assert client.get(f"/api/notes/{note_id}").status_code == 404


def test_create_and_list_tasks(client):
    client.post("/api/tasks/", json={"title": "Task A"})
    client.post("/api/tasks/", json={"title": "Task B", "is_focus": True})
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_focus_tasks_endpoint(client):
    client.post("/api/tasks/", json={"title": "Not focus"})
    client.post("/api/tasks/", json={"title": "Focus task", "is_focus": True})
    response = client.get("/api/tasks/focus")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Focus task"


def test_settings_upsert_and_list(client):
    client.put("/api/settings/username", json={"value": "Marc"})
    client.put("/api/settings/username", json={"value": "Bob"})
    response = client.get("/api/settings/")
    settings = {s["key"]: s["value"] for s in response.json()}
    assert settings["username"] == "Bob"


def test_create_folder_and_note_in_folder(client):
    folder_resp = client.post("/api/folders/", json={"name": "Work"})
    assert folder_resp.status_code == 201
    folder_id = folder_resp.json()["id"]

    note_resp = client.post("/api/notes/", json={"title": "Work Note", "content": "", "folder_id": folder_id})
    assert note_resp.status_code == 201
    assert note_resp.json()["folder_id"] == folder_id