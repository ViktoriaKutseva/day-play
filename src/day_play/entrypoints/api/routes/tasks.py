
from fastapi import APIRouter, Depends, HTTPException, Query

from day_play.business.gamification_engine import GamificationEngine
from day_play.business.task_manager import TaskManager
from day_play.entrypoints.api.dependencies import (
    get_gamification_engine,
    get_task_manager,
)
from day_play.entrypoints.api.schemas.task_schema import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from day_play.models.enums import TaskStatus
from day_play.models.exceptions import TaskNotFoundError

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(
    task_data: TaskCreate,
    user_id: int = Query(default=1, description="User ID"),
    task_manager: TaskManager = Depends(get_task_manager),
    gamification: GamificationEngine = Depends(get_gamification_engine),
) -> TaskResponse:
    """Create a new task."""
    task = task_data.to_entity(user_id=user_id)
    created_task = task_manager.create_task(task)
    return TaskResponse.from_entity(created_task, gamification)


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    task_manager: TaskManager = Depends(get_task_manager),
    gamification: GamificationEngine = Depends(get_gamification_engine),
    user_id: int = Query(default=1, description="User ID"),  # TODO: Get from auth
    status: TaskStatus | None = Query(default=None, description="Filter by status"),
    overdue_only: bool = Query(default=False, description="Only return overdue tasks"),
) -> list[TaskResponse]:
    """List all tasks for a user with optional filters."""
    tasks = task_manager.get_tasks(
        user_id=user_id,
        status=status,
        overdue_only=overdue_only,
    )
    return [TaskResponse.from_entity(task, gamification) for task in tasks]

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    user_id: int = Query(default=1, description="User ID"),
    task_manager: TaskManager = Depends(get_task_manager),
    gamification: GamificationEngine = Depends(get_gamification_engine),
) -> TaskResponse:
    """Get task details by ID."""
    task = task_manager.get_task(task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.from_entity(task, gamification)

@router.put("/{task_id}", response_model=TaskResponse)
def put_task(
    task_id: int,
    task_data: TaskUpdate,
    user_id: int = Query(default=1, description="User ID"),
    task_manager: TaskManager = Depends(get_task_manager),
    gamification: GamificationEngine = Depends(get_gamification_engine),
) -> TaskResponse:
    """Update a task."""
    existing_task = task_manager.get_task(task_id)
    if existing_task is None or existing_task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    updated_entity = task_data.apply_to(existing_task)
    updated_task = task_manager.update_task(updated_entity)
    return TaskResponse.from_entity(updated_task, gamification)

@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    user_id: int = Query(default=1, description="User ID"),
    task_manager: TaskManager = Depends(get_task_manager),
) -> None:
    """Delete a task."""
    existing_task = task_manager.get_task(task_id)
    if existing_task is None or existing_task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    task_manager.delete_task(task_id)

@router.post("/{task_id}/complete", status_code=200)
def complete_task(
    task_id: int,
    user_id: int = Query(default=1, description="User ID"),
    task_manager: TaskManager = Depends(get_task_manager),
    gamification: GamificationEngine = Depends(get_gamification_engine),
    ) -> TaskResponse:

    try:
        completed_task, achievements = task_manager.complete_task(task_id, user_id)
        return TaskResponse.from_entity(completed_task, gamification)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")

@router.post("/{task_id}/undo", status_code=200)
def undo_task(
    task_id: int,
    user_id: int = Query(default=1, description="User ID"),
    task_manager: TaskManager = Depends(get_task_manager),
    gamification: GamificationEngine = Depends(get_gamification_engine),
    ) -> TaskResponse:
    try:
        undone_task = task_manager.undo_task(task_id, user_id)
        return TaskResponse.from_entity(undone_task, gamification)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
