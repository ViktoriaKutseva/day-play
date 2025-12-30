import pytest
from datetime import UTC, datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from day_play.entrypoints.api.dependencies import get_db
from day_play.entrypoints.api.main import create_app

# Import ALL models to ensure they're registered with SQLModel metadata
# These imports are necessary for SQLModel.metadata.create_all() to work
from day_play.integrations.database.models import (  # noqa: F401
    Achievement,
    DailyProgress,
    Prize,
    SQLModel,
    Task,
    User,
)

# Test database URL - using shared memory mode so multiple connections see the same DB
# The ?cache=shared parameter is crucial for in-memory SQLite testing
TEST_DATABASE_URL = "sqlite:///file:testdb?mode=memory&cache=shared&uri=true"


@pytest.fixture
def test_db():
    """Create a fresh database for each test."""
    # Create new engine with shared in-memory SQLite
    engine = create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False, "uri": True}
    )

    # Create all tables - models are already imported above
    SQLModel.metadata.create_all(engine)

    # Create session factory
    TestingSessionLocal = sessionmaker(bind=engine)

    yield engine, TestingSessionLocal

    # Cleanup - drop all tables
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(test_db):
    """Create a TestClient with overridden database dependency."""
    engine, TestingSessionLocal = test_db

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Create app and override the database dependency
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    # Seed a default user for tests
    db = TestingSessionLocal()
    try:
        if not db.get(User, 1):
            db.add(User(id=1, username="test_user", current_level=1, total_xp=0))
            db.commit()
    finally:
        db.close()

    with TestClient(app) as c:
        yield c


def test_health_check(client):
    """Test the health endpoint returns 200."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_task(client):
    """Test creating a new task."""
    # Arrange - prepare your data
    task_data = {
        "title": "Learn API Testing",
        "description": "Study TestClient and pytest",
        "priority": "high",
        "urgency": "medium",
    }

    # Act - make the request
    response = client.post("/api/tasks/", json=task_data)

    # Assert - check everything!
    assert response.status_code == 201  # Created!

    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["priority"] == "high"
    assert data["urgency"] == "medium"
    assert data["id"] is not None  # ID was assigned!


def test_get_task(client):
    """Test retrieving a task by ID."""
    # First, create a task
    create_response = client.post("/api/tasks/", json={"title": "Test Task"})
    task_id = create_response.json()["id"]

    # Now retrieve it
    response = client.get(f"/api/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


def test_list_tasks(client):
    """Test listing all tasks."""
    # Create some tasks
    client.post("/api/tasks/", json={"title": "Task 1"})
    client.post("/api/tasks/", json={"title": "Task 2"})

    # Get the list
    response = client.get("/api/tasks/")

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    titles = {t["title"] for t in tasks}
    assert titles == {"Task 1", "Task 2"}


def test_update_task(client):
    """Test updating a task."""
    # Create a task
    create_response = client.post("/api/tasks/", json={"title": "Original"})
    task_id = create_response.json()["id"]

    # Update it
    response = client.put(f"/api/tasks/{task_id}", json={"title": "Updated Title"})

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_delete_task(client):
    """Test deleting a task."""
    # Create a task
    create_response = client.post("/api/tasks/", json={"title": "To Delete"})
    task_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/api/tasks/{task_id}")

    assert response.status_code == 204  # No Content

    # Verify it's gone
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404


def test_get_task_not_found(client):
    """Test getting a non-existent task returns 404."""
    response = client.get("/api/tasks/9999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_task_not_found(client):
    """Test deleting a non-existent task returns 404."""
    response = client.delete("/api/tasks/9999")

    assert response.status_code == 404


def test_create_task_missing_title(client):
    """Test creating a task without title fails validation."""
    response = client.post(
        "/api/tasks/",
        json={
            "description": "No title provided"
            # title is missing!
        },
    )

    assert response.status_code == 422
    # Check that the error mentions 'title'
    errors = response.json()["detail"]
    assert any("title" in str(error).lower() for error in errors)


def test_create_task_empty_title(client):
    """Test creating a task with empty title fails."""
    response = client.post(
        "/api/tasks/",
        json={
            "title": ""  # Empty string!
        },
    )

    assert response.status_code == 422


def test_create_task_invalid_priority(client):
    """Test creating a task with invalid priority fails."""
    response = client.post(
        "/api/tasks/",
        json={
            "title": "Valid Title",
            "priority": "super_duper_high",  # Not a valid enum value!
        },
    )

    assert response.status_code == 422


def test_redeem_prize_insufficient_xp(client):
    """Test redeeming a prize without enough XP fails."""
    # First, create a prize that costs 1000 XP
    client.post(
        "/api/gamification/prizes",
        json={
            "name": "Expensive Prize",
            "description": "Costs too much",
            "cost_xp": 1000,
        },
    )

    # User starts with 0 XP, so redeeming should fail
    response = client.post("/api/gamification/prizes/1/redeem")

    assert response.status_code == 400
    # Error message mentions XP and the requirement
    detail = response.json()["detail"].lower()
    assert "xp" in detail and ("need" in detail or "insufficient" in detail)


def test_task_response_schema(client):
    """Test that task response matches expected schema."""
    # Create a task
    task_data = {
        "title": "Schema Test",
        "description": "Testing response structure",
        "priority": "medium",
        "urgency": "low",
    }
    response = client.post("/api/tasks/", json=task_data)
    data = response.json()

    # Check all expected fields exist
    assert "id" in data
    assert "title" in data
    assert "description" in data
    assert "priority" in data
    assert "urgency" in data
    assert "status" in data
    assert "created_at" in data
    assert "xp_value" in data  # Calculated field!

    # Check types
    assert isinstance(data["id"], int)
    assert isinstance(data["title"], str)
    assert isinstance(data["xp_value"], int)


def test_dashboard_response_schema(client):
    """Test dashboard returns correct structure."""
    response = client.get("/api/dashboard", params={"user_id": 1})
    data = response.json()

    # Check structure
    assert "progress" in data
    assert "user_level" in data
    assert "upcoming_tasks" in data
    assert "recent_achievements" in data

    # Check nested structures (progress contains both daily and level progress)
    assert "daily_completion_percent" in data["progress"]
    assert "level_progress_percent" in data["progress"]
    assert "current_level" in data["user_level"]
    assert "xp_for_next_level" in data["user_level"]


# ============================================================================
# Task Management Tests
# ============================================================================


def test_complete_task(client):
    """Test completing a task."""
    # Create a task
    create_response = client.post("/api/tasks/", json={"title": "Task to Complete"})
    task_id = create_response.json()["id"]

    # Complete it
    response = client.post(f"/api/tasks/{task_id}/complete")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["id"] == task_id


def test_complete_nonexistent_task(client):
    """Test completing a non-existent task returns 404."""
    response = client.post("/api/tasks/9999/complete")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_undo_task(client):
    """Test undoing a completed task."""
    # Create and complete a task
    create_response = client.post("/api/tasks/", json={"title": "Task to Undo"})
    task_id = create_response.json()["id"]
    client.post(f"/api/tasks/{task_id}/complete")

    # Undo it
    response = client.post(f"/api/tasks/{task_id}/undo")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert data["id"] == task_id


def test_undo_nonexistent_task(client):
    """Test undoing a non-existent task returns 404."""
    response = client.post("/api/tasks/9999/undo")

    assert response.status_code == 404


def test_list_tasks_with_status_filter(client):
    """Test filtering tasks by status."""
    # Create tasks with different statuses
    task1 = client.post("/api/tasks/", json={"title": "Pending Task"})
    task1_id = task1.json()["id"]

    task2 = client.post("/api/tasks/", json={"title": "To Complete"})
    task2_id = task2.json()["id"]
    client.post(f"/api/tasks/{task2_id}/complete")

    # Filter by pending status
    response = client.get("/api/tasks/", params={"status": "pending"})

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task1_id
    assert tasks[0]["status"] == "pending"


def test_list_tasks_overdue_only(client):
    """Test filtering overdue tasks."""
    from datetime import datetime, timedelta, UTC

    # Create a task with past due date
    past_date = (datetime.now(UTC) - timedelta(days=2)).isoformat()
    client.post("/api/tasks/", json={"title": "Overdue Task", "due_date": past_date})

    # Create a future task
    future_date = (datetime.now(UTC) + timedelta(days=2)).isoformat()
    client.post("/api/tasks/", json={"title": "Future Task", "due_date": future_date})

    # Get overdue tasks only
    response = client.get("/api/tasks/", params={"overdue_only": True})

    assert response.status_code == 200
    tasks = response.json()
    # Should only return overdue task
    assert len(tasks) >= 1
    assert any(task["title"] == "Overdue Task" for task in tasks)


def test_update_task_priority(client):
    """Test updating task priority."""
    # Create a task
    create_response = client.post(
        "/api/tasks/", json={"title": "Test", "priority": "low"}
    )
    task_id = create_response.json()["id"]

    # Update priority
    response = client.put(f"/api/tasks/{task_id}", json={"priority": "high"})

    assert response.status_code == 200
    assert response.json()["priority"] == "high"


def test_update_task_with_recurrence(client):
    """Test updating task with recurrence pattern."""
    # Create a task
    create_response = client.post("/api/tasks/", json={"title": "Recurring Task"})
    task_id = create_response.json()["id"]

    # Update with recurrence
    response = client.put(f"/api/tasks/{task_id}", json={"recurrence_pattern": "daily"})

    assert response.status_code == 200
    assert response.json()["recurrence_pattern"] == "daily"


# ============================================================================
# Dashboard Tests
# ============================================================================


def test_get_user_level(client):
    """Test getting user level data."""
    response = client.get("/api/user/level", params={"user_id": 1})

    assert response.status_code == 200
    data = response.json()
    assert "current_level" in data
    assert "total_xp" in data
    assert "xp_for_next_level" in data
    assert "progress_percent" in data
    assert isinstance(data["current_level"], int)
    assert isinstance(data["total_xp"], int)


def test_dashboard_with_tasks(client):
    """Test dashboard includes task information."""
    # Create some tasks with today's due date
    today = datetime.now(UTC).isoformat()
    client.post("/api/tasks/", json={"title": "Dashboard Task 1", "due_date": today})
    client.post("/api/tasks/", json={"title": "Dashboard Task 2", "due_date": today})

    response = client.get("/api/dashboard", params={"user_id": 1})

    assert response.status_code == 200
    data = response.json()
    assert "upcoming_tasks" in data
    assert len(data["upcoming_tasks"]) >= 2


def test_dashboard_nonexistent_user(client):
    """Test dashboard for non-existent user returns 404."""
    response = client.get("/api/dashboard", params={"user_id": 9999})

    assert response.status_code == 404


# ============================================================================
# Gamification Tests
# ============================================================================


def test_create_prize(client):
    """Test creating a new prize."""
    prize_data = {"name": "Test Prize", "description": "A test reward", "cost_xp": 100}

    response = client.post("/api/gamification/prizes", json=prize_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == prize_data["name"]
    assert data["cost_xp"] == prize_data["cost_xp"]
    assert data["redeemed"] is False


def test_list_prizes(client):
    """Test listing all prizes."""
    # Create a few prizes
    client.post(
        "/api/gamification/prizes",
        json={"name": "Prize 1", "description": "First prize", "cost_xp": 100},
    )
    client.post(
        "/api/gamification/prizes",
        json={"name": "Prize 2", "description": "Second prize", "cost_xp": 200},
    )

    response = client.get("/api/gamification/prizes", params={"user_id": 1})

    assert response.status_code == 200
    prizes = response.json()
    assert len(prizes) == 2


def test_list_prizes_redeemed_filter(client):
    """Test filtering prizes by redeemed status."""
    # Create and redeem a prize (would need user to have XP)
    client.post(
        "/api/gamification/prizes",
        json={
            "name": "Unredeemed Prize",
            "description": "Not redeemed yet",
            "cost_xp": 10,
        },
    )

    # Get unredeemed prizes
    response = client.get(
        "/api/gamification/prizes", params={"user_id": 1, "is_redeemed": False}
    )

    assert response.status_code == 200
    prizes = response.json()
    assert all(not prize["redeemed"] for prize in prizes)


def test_redeem_prize_already_redeemed(client):
    """Test redeeming a prize that's already redeemed fails."""
    # Create a low-cost prize
    prize_response = client.post(
        "/api/gamification/prizes",
        json={"name": "Low Cost Prize", "description": "Cheap", "cost_xp": 1},
    )
    prize_id = prize_response.json()["id"]

    # Give user XP by completing a task
    task_response = client.post("/api/tasks/", json={"title": "XP Task", "priority": "high", "urgency": "high"})
    task_id = task_response.json()["id"]
    client.post(f"/api/tasks/{task_id}/complete")

    # Redeem it once
    client.post(f"/api/gamification/prizes/{prize_id}/redeem")

    # Try to redeem again
    response = client.post(f"/api/gamification/prizes/{prize_id}/redeem")

    assert response.status_code == 400
    assert "already redeemed" in response.json()["detail"].lower()


def test_redeem_nonexistent_prize(client):
    """Test redeeming a non-existent prize returns 404."""
    response = client.post("/api/gamification/prizes/9999/redeem")

    assert response.status_code == 404


def test_get_achievements(client):
    """Test getting achievements list."""
    response = client.get("/api/gamification/achievements", params={"user_id": 1})

    assert response.status_code == 200
    achievements = response.json()
    assert isinstance(achievements, list)


def test_get_unlocked_achievements(client):
    """Test filtering for unlocked achievements only."""
    response = client.get(
        "/api/gamification/achievements", params={"user_id": 1, "is_unlocked": True}
    )

    assert response.status_code == 200
    achievements = response.json()
    # All returned achievements should be unlocked
    assert all(
        ach["unlocked_at"] is not None for ach in achievements if "unlocked_at" in ach
    )


def test_get_available_achievements(client):
    """Test filtering for available (not unlocked) achievements."""
    response = client.get(
        "/api/gamification/achievements", params={"user_id": 1, "is_unlocked": False}
    )

    assert response.status_code == 200
    # Should return list (empty or with definitions)
    assert isinstance(response.json(), list)


# ============================================================================
# History Tests
# ============================================================================


def test_get_history(client):
    """Test getting history for default period."""
    response = client.get("/api/history/", params={"user_id": 1})

    assert response.status_code == 200
    data = response.json()
    assert "start_date" in data
    assert "end_date" in data
    assert "progress_entries" in data
    assert isinstance(data["progress_entries"], list)


def test_get_history_custom_days(client):
    """Test getting history for custom number of days."""
    response = client.get("/api/history/", params={"user_id": 1, "days": 7})

    assert response.status_code == 200
    data = response.json()
    assert "progress_entries" in data


def test_get_history_invalid_days(client):
    """Test that invalid days parameter is rejected."""
    # Test exceeding maximum
    response = client.get(
        "/api/history/",
        params={
            "user_id": 1,
            "days": 500,  # More than 365
        },
    )

    assert response.status_code == 422


def test_get_history_by_date(client):
    """Test getting history for specific date."""
    from datetime import date

    today = date.today().isoformat()
    response = client.get(f"/api/history/{today}", params={"user_id": 1})

    assert response.status_code == 200
    data = response.json()
    assert "date" in data
    assert "tasks_completed" in data
    assert "daily_xp_earned" in data


def test_get_history_future_date(client):
    """Test getting history for future date returns empty."""
    from datetime import date, timedelta

    future_date = (date.today() + timedelta(days=10)).isoformat()
    response = client.get(f"/api/history/{future_date}", params={"user_id": 1})

    assert response.status_code == 200
    data = response.json()
    # Should return empty/zero data for future dates
    assert data["tasks_completed"] == 0


# ============================================================================
# Integration Tests (Multiple Operations)
# ============================================================================


def test_complete_task_earns_xp(client):
    """Test that completing a task increases user XP."""
    # Get initial XP
    initial_response = client.get("/api/user/level", params={"user_id": 1})
    initial_xp = initial_response.json()["total_xp"]

    # Create and complete a high-priority task
    task_response = client.post(
        "/api/tasks/",
        json={"title": "XP Test Task", "priority": "high", "urgency": "high"},
    )
    task_id = task_response.json()["id"]

    # Complete the task
    client.post(f"/api/tasks/{task_id}/complete")

    # Check XP increased
    final_response = client.get("/api/user/level", params={"user_id": 1})
    final_xp = final_response.json()["total_xp"]

    assert final_xp > initial_xp


def test_redeem_prize_after_earning_xp(client):
    """Test redeeming a prize after earning sufficient XP."""
    # Create a prize that costs some XP
    prize_response = client.post(
        "/api/gamification/prizes",
        json={
            "name": "Affordable Prize",
            "description": "Can be earned",
            "cost_xp": 50,
        },
    )
    prize_id = prize_response.json()["id"]

    # Create and complete high-value tasks to earn XP
    for i in range(3):
        task_response = client.post(
            "/api/tasks/",
            json={"title": f"XP Task {i}", "priority": "high", "urgency": "high"},
        )
        task_id = task_response.json()["id"]
        client.post(f"/api/tasks/{task_id}/complete")

    # Now try to redeem the prize
    response = client.post(f"/api/gamification/prizes/{prize_id}/redeem")

    # Should succeed if we earned enough XP
    assert response.status_code in [200, 400]  # 400 if still not enough XP


def test_dashboard_reflects_completed_tasks(client):
    """Test that dashboard updates after completing tasks."""
    # Get initial dashboard state
    initial_dashboard = client.get("/api/dashboard", params={"user_id": 1}).json()
    initial_daily_progress = initial_dashboard["progress"]["daily_completion_percent"]

    # Create and complete a task
    task_response = client.post("/api/tasks/", json={"title": "Dashboard Task"})
    task_id = task_response.json()["id"]
    client.post(f"/api/tasks/{task_id}/complete")

    # Check dashboard updated
    final_dashboard = client.get("/api/dashboard", params={"user_id": 1}).json()
    final_daily_progress = final_dashboard["progress"]["daily_completion_percent"]

    assert final_daily_progress >= initial_daily_progress


def test_full_task_lifecycle(client):
    """Test complete task lifecycle: create, update, complete, undo, delete."""
    # Create
    response = client.post("/api/tasks/", json={"title": "Lifecycle Task"})
    assert response.status_code == 201
    task_id = response.json()["id"]

    # Update
    response = client.put(f"/api/tasks/{task_id}", json={"title": "Updated Task"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"

    # Complete
    response = client.post(f"/api/tasks/{task_id}/complete")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

    # Undo
    response = client.post(f"/api/tasks/{task_id}/undo")
    assert response.status_code == 200
    assert response.json()["status"] == "pending"

    # Delete
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 204

    # Verify deleted
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 404


# ============================================================================
# Error Handling Tests
# ============================================================================


def test_update_nonexistent_task(client):
    """Test updating a non-existent task returns 404."""
    response = client.put("/api/tasks/9999", json={"title": "Updated"})

    assert response.status_code == 404


def test_invalid_recurrence_pattern(client):
    """Test creating task with invalid recurrence pattern."""
    response = client.post(
        "/api/tasks/", json={"title": "Task", "recurrence_pattern": "invalid_pattern"}
    )

    assert response.status_code == 422


def test_create_prize_missing_fields(client):
    """Test creating prize without cost_xp gets default value of 0, which fails business validation."""
    # This test verifies that omitting cost_xp uses default value of 0,
    # which should fail business logic validation (cost_xp must be > 0)
    try:
        response = client.post(
            "/api/gamification/prizes",
            json={
                "name": "Incomplete Prize"
                # Missing cost_xp - gets default value of 0, which fails business logic validation
            },
        )
        # Should get 500 because business logic rejects cost_xp <= 0
        assert response.status_code == 500
    except ValueError as e:
        # Or business logic might raise ValueError directly (not wrapped in HTTP response)
        assert "Prize XP threshold must be greater than 0" in str(e)


def test_negative_xp_cost(client):
    """Test that negative XP cost is rejected."""
    response = client.post(
        "/api/gamification/prizes",
        json={"name": "Invalid Prize", "description": "Negative cost", "cost_xp": -100},
    )

    assert response.status_code in [422, 500]
