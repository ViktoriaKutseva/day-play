import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app, get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_read_tasks_empty(client: TestClient):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json()["data"] == []


def test_create_task(client: TestClient):
    response = client.post("/tasks", json={"task_name": "write tests"})
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["task_name"] == "write tests"
    assert data["completed"] is False
    assert data["task_id"] is not None


def test_read_task(client: TestClient):
    created = client.post("/tasks", json={"task_name": "read me"}).json()["data"]
    response = client.get(f"/tasks/{created['task_id']}")
    assert response.status_code == 200
    assert response.json()["data"]["task_name"] == "read me"


def test_read_task_not_found(client: TestClient):
    response = client.get("/tasks/999")
    assert response.status_code == 404


def test_read_tasks_pagination(client: TestClient):
    for i in range(5):
        client.post("/tasks", json={"task_name": f"task {i}"})

    response = client.get("/tasks", params={"limit": 2, "offset": 1})
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    assert data[0]["task_name"] == "task 1"


def test_update_task_put(client: TestClient):
    created = client.post("/tasks", json={"task_name": "old name"}).json()["data"]
    response = client.put(
        f"/tasks/{created['task_id']}",
        json={"task_name": "new name", "completed": True},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["task_name"] == "new name"
    assert data["completed"] is True


def test_update_task_not_found(client: TestClient):
    response = client.put("/tasks/999", json={"task_name": "nope"})
    assert response.status_code == 404


def test_patch_task_partial(client: TestClient):
    created = client.post("/tasks", json={"task_name": "toggle me"}).json()["data"]
    response = client.patch(f"/tasks/{created['task_id']}", json={"completed": True})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["completed"] is True
    assert data["task_name"] == "toggle me"


def test_patch_task_not_found(client: TestClient):
    response = client.patch("/tasks/999", json={"completed": True})
    assert response.status_code == 404


def test_delete_task(client: TestClient):
    created = client.post("/tasks", json={"task_name": "delete me"}).json()["data"]
    response = client.delete(f"/tasks/{created['task_id']}")
    assert response.status_code == 204

    response = client.get(f"/tasks/{created['task_id']}")
    assert response.status_code == 404


def test_delete_task_not_found(client: TestClient):
    response = client.delete("/tasks/999")
    assert response.status_code == 404
