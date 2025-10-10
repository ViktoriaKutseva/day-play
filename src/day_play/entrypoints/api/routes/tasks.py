"""API routes for task management."""
from fastapi import APIRouter, HTTPException, Depends

from src.day_play.entrypoints.api.dependencies import get_task_service
from src.day_play.entrypoints.api.schemas import TaskResponse, TaskSingleResponse, TaskListResponse
from src.day_play.business.services import TaskService
from src.day_play.models.entities import TaskCreate, TaskUpdate
from src.day_play.models.exceptions import TaskNotFoundError

router = APIRouter()


@router.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {"message": "Task Management API", "version": "1.0.0"}


@router.get("/tasks", response_model=TaskListResponse)
async def read_tasks(
    task_service: TaskService = Depends(get_task_service)
) -> TaskListResponse:
    """Retrieve all tasks."""
    try:
        tasks = await task_service.get_all_tasks()
        task_responses = [TaskResponse.from_entity(task) for task in tasks]
        return TaskListResponse(data=task_responses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tasks: {str(e)}")


@router.get("/tasks/{task_id}", response_model=TaskSingleResponse)
async def read_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service)
) -> TaskSingleResponse:
    """Retrieve a specific task by ID."""
    try:
        task = await task_service.get_task(task_id)
        return TaskSingleResponse(data=TaskResponse.from_entity(task))
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve task: {str(e)}")


@router.post("/tasks", response_model=TaskSingleResponse, status_code=201)
async def create_task(
    task: TaskCreate,
    task_service: TaskService = Depends(get_task_service)
) -> TaskSingleResponse:
    """Create a new task."""
    try:
        created_task = await task_service.create_task(task)
        return TaskSingleResponse(data=TaskResponse.from_entity(created_task))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@router.put("/tasks/{task_id}", response_model=TaskSingleResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    task_service: TaskService = Depends(get_task_service)
) -> TaskSingleResponse:
    """Update an existing task."""
    try:
        updated_task = await task_service.update_task(task_id, task_update)
        return TaskSingleResponse(data=TaskResponse.from_entity(updated_task))
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service)
) -> None:
    """Delete a task by ID."""
    try:
        await task_service.delete_task(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")