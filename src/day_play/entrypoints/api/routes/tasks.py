"""Task API routes."""
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status

from ....business.services import TaskService
from ....models.exceptions import TaskNotFoundError, InvalidTaskDataError
from ....models.value_objects import TaskCreate, TaskUpdate
from ..dependencies import get_task_service
from ..schemas import Response, TaskResponse, TaskCreateRequest, TaskUpdateRequest

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=Response[List[TaskResponse]])
async def get_tasks(task_service: TaskService = Depends(get_task_service)):
    """Get all tasks."""
    tasks = await task_service.get_all_tasks()
    task_responses = [TaskResponse.from_entity(task) for task in tasks]
    return Response(data=task_responses)


@router.get("/{task_id}", response_model=Response[TaskResponse])
async def get_task(task_id: int, task_service: TaskService = Depends(get_task_service)):
    """Get a task by ID."""
    try:
        task = await task_service.get_task_by_id(task_id)
        return Response(data=TaskResponse.from_entity(task))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidTaskDataError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/", response_model=Response[TaskResponse], status_code=status.HTTP_201_CREATED)
async def create_task(
    task_request: TaskCreateRequest,
    task_service: TaskService = Depends(get_task_service)
):
    """Create a new task."""
    try:
        task_data = TaskCreate(
            task_name=task_request.task_name,
            completed=task_request.completed,
            due_date=task_request.due_date
        )
        task = await task_service.create_task(task_data)
        return Response(data=TaskResponse.from_entity(task))
    except InvalidTaskDataError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{task_id}", response_model=Response[TaskResponse])
async def update_task(
    task_id: int,
    task_request: TaskUpdateRequest,
    task_service: TaskService = Depends(get_task_service)
):
    """Update an existing task."""
    try:
        task_data = TaskUpdate(
            task_name=task_request.task_name,
            completed=task_request.completed,
            due_date=task_request.due_date
        )
        task = await task_service.update_task(task_id, task_data)
        return Response(data=TaskResponse.from_entity(task))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidTaskDataError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, task_service: TaskService = Depends(get_task_service)):
    """Delete a task."""
    try:
        await task_service.delete_task(task_id)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidTaskDataError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))