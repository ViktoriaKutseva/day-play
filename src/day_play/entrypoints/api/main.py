from fastapi import FastAPI, HTTPException, Depends
from datetime import date
from typing import Annotated, Generic, TypeVar, Optional
from fastapi.concurrency import asynccontextmanager
from sqlmodel import Session, select
from pydantic import BaseModel
from loguru import logger

from src.day_play.models.models import User, Task, RecurrenceType
from src.day_play.integrations.database.database import db_manager
from src.day_play.entrypoints.api.schemas import (
    Response,
    UserCreate,
    TaskCreate,
    TaskUpdate,
    TaskCompletionCreate
)

def get_session():
    with Session(db_manager.engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI application")
    # Database tables are already created by db_manager
    # Add sample data for testing if needed
    with Session(db_manager.engine) as session:
        # Check if we have any users
        if not session.exec(select(User)).first():
            logger.info("Adding sample data for testing")
            # Create a sample user
            sample_user = User(user_id=123456789, name="Test User", lvl=1, score=0)
            session.add(sample_user)
            session.commit()
            session.refresh(sample_user)
            
            # Ensure sample_user.id is not None before creating tasks
            if sample_user.id is None:
                raise ValueError("Failed to create sample user")
            
            # Create sample tasks
            sample_tasks = [
                Task(name="Morning Exercise", description="30 minutes cardio", 
                     recurrence=RecurrenceType.DAILY, score=20, creator_id=sample_user.id),
                Task(name="Read a book", description="Read for 30 minutes", 
                     recurrence=RecurrenceType.DAILY, score=15, creator_id=sample_user.id),
                Task(name="Weekly review", description="Review goals and progress", 
                     recurrence=RecurrenceType.WEEKLY, score=50, creator_id=sample_user.id)
            ]
            session.add_all(sample_tasks)
            session.commit()
            logger.info("Sample data added successfully")
    
    yield
    
    logger.info("Shutting down FastAPI application")
    
app = FastAPI(root_path="/api/v1", lifespan=lifespan, title="Day Play API", version="1.0.0")

T = TypeVar('T')


class Response(BaseModel, Generic[T]):
    """Generic response wrapper."""
    data: T



@app.post("/users", response_model=Response[User], status_code=201)
async def create_user(user: UserCreate, session: SessionDep):
    """Create a new user."""
    try:
        # Check if user already exists
        existing_user = session.exec(select(User).where(User.user_id == user.user_id)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this user_id already exists")
        
        db_user = User(user_id=user.user_id, name=user.name)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        logger.info(f"Created user: {db_user.name} (ID: {db_user.id})")
        return {"data": db_user}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")


@app.get("/users/{user_id}", response_model=Response[User])
async def get_user(user_id: int, session: SessionDep):
    """Get user by Telegram user_id."""
    user = session.exec(select(User).where(User.user_id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"data": user}


@app.get("/users", response_model=Response[list[User]])
async def get_all_users(session: SessionDep):
    """Get all users."""
    users = session.exec(select(User)).all()
    return {"data": users}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Day Play API - Gamified Task Management", "version": "1.0.0"}


@app.get("/tasks", response_model=Response[list[Task]])
async def get_tasks(session: SessionDep, creator_id: Optional[int] = None):
    """Get all tasks, optionally filtered by creator."""
    try:
        query = select(Task)
        if creator_id:
            query = query.where(Task.creator_id == creator_id)
        tasks = session.exec(query).all()
        return {"data": tasks}
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tasks")


@app.get("/tasks/{task_id}", response_model=Response[Task])
async def get_task(task_id: int, session: SessionDep):
    """Get a specific task by ID."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"data": task}


@app.post("/tasks", response_model=Response[Task], status_code=201)
async def create_task(task: TaskCreate, session: SessionDep):
    """Create a new task."""
    try:
        # Verify creator exists
        creator = session.get(User, task.creator_id)
        if not creator:
            raise HTTPException(status_code=404, detail="Creator user not found")
        
        db_task = Task(
            name=task.name,
            description=task.description,
            recurrence=task.recurrence,
            due_date=task.due_date,
            score=task.score,
            creator_id=task.creator_id
        )
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        logger.info(f"Created task: {db_task.name} (ID: {db_task.id})")
        return {"data": db_task}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="Failed to create task")


@app.put("/tasks/{task_id}", response_model=Response[Task])
async def update_task(task_id: int, updated_task: TaskUpdate, session: SessionDep):
    """Update an existing task."""
    try:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update only provided fields
        if updated_task.name is not None:
            task.name = updated_task.name
        if updated_task.description is not None:
            task.description = updated_task.description
        if updated_task.recurrence is not None:
            task.recurrence = updated_task.recurrence
        if updated_task.due_date is not None:
            task.due_date = updated_task.due_date
        if updated_task.score is not None:
            task.score = updated_task.score
        
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"Updated task: {task.name} (ID: {task.id})")
        return {"data": task}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail="Failed to update task")


@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, session: SessionDep):
    """Delete a task."""
    try:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        session.delete(task)
        session.commit()
        logger.info(f"Deleted task ID: {task_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete task")


# ============== Task Completion Endpoints ==============

@app.post("/completions", response_model=Response[dict], status_code=201)
async def complete_task(completion: TaskCompletionCreate, session: SessionDep):
    """Record a task completion and award points to user."""
    try:
        # Verify task exists
        task = session.get(Task, completion.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Verify user exists
        user = session.get(User, completion.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create task completion record
        from src.day_play.models.models import TaskCompletion
        db_completion = TaskCompletion(
            task_id=completion.task_id,
            user_id=completion.user_id
        )
        session.add(db_completion)
        
        # Award points to user
        user.score += task.score
        session.add(user)
        
        session.commit()
        session.refresh(db_completion)
        session.refresh(user)
        
        logger.info(f"Task completed: {task.name} by user {user.name}, awarded {task.score} points")
        
        return {
            "data": {
                "completion_id": db_completion.id,
                "task_name": task.name,
                "points_awarded": task.score,
                "user_score": user.score,
                "user_level": user.lvl
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete task")


@app.get("/users/{user_id}/completions", response_model=Response[list[dict]])
async def get_user_completions(user_id: int, session: SessionDep):
    """Get all task completions for a user."""
    try:
        from src.day_play.models.models import TaskCompletion
        
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        completions = session.exec(
            select(TaskCompletion).where(TaskCompletion.user_id == user_id)
        ).all()
        
        # Format response with task names
        result = []
        for comp in completions:
            task = session.get(Task, comp.task_id)
            result.append({
                "completion_id": comp.id,
                "task_id": comp.task_id,
                "task_name": task.name if task else "Unknown",
                "completed_date": comp.completed_date,
                "times_completed": comp.times_completed
            })
        
        return {"data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user completions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get completions")
