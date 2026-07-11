from datetime import UTC, datetime
from typing import Annotated, Generic, TypeVar

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select

from config import settings


class Task(SQLModel, table=True):
    task_id: int | None = Field(default=None, primary_key=True)
    task_name: str = Field(index=True)
    completed: bool = Field(default=False)
    due_date: datetime | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=True, index=True
    )

class TaskCreate(SQLModel):
    task_name: str
    completed: bool = Field(default=False)
    due_date: datetime | None = Field(default=None)

class TaskUpdate(SQLModel):
    task_name: str | None = None
    completed: bool | None = None
    due_date: datetime | None = None

connect_args = {"check_same_thread": False}
engine = create_engine(settings.sqlite_url, connect_args=connect_args, echo=settings.debug)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Task)).first():
            session.add_all(
                [
                    Task(task_name="tpu", due_date=datetime(2026, 8, 1, tzinfo=UTC)),
                    Task(task_name="task2", due_date=datetime(2026, 8, 15, tzinfo=UTC)),
                    Task(task_name="task3", due_date=datetime(2026, 9, 1, tzinfo=UTC))
                ]
            )
            session.commit()
    yield

app = FastAPI(root_path=settings.root_path, lifespan=lifespan)

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    data: T


@app.get("/")
async def root():
    message = "Hello, World!"
    return {"message": message}

@app.get("/tasks", response_model=Response[list[Task]])
async def read_tasks(
    session: SessionDep,
    limit: Annotated[int, Query(gt=0, le=100)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    tasks = session.exec(select(Task).offset(offset).limit(limit)).all()
    return {"data": tasks}

@app.get("/tasks/{task_id}", response_model=Response[Task])
async def read_task(task_id: int, session: SessionDep):
    data = session.get(Task, task_id)
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    return {'data': data}

@app.post("/tasks", response_model=Response[Task], status_code=201)
async def create_task(task: TaskCreate, session: SessionDep):
    db_task = Task.model_validate(task)
    session.add(db_task)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(db_task)
    return {"data": db_task}

@app.put("/tasks/{task_id}", response_model=Response[Task])
async def update_task(task_id: int, updated_task: TaskCreate, session: SessionDep):
    data = session.get(Task, task_id)
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    data.task_name = updated_task.task_name
    data.completed = updated_task.completed
    data.due_date = updated_task.due_date
    session.add(data)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(data)
    return {'data': data}

@app.patch("/tasks/{task_id}", response_model=Response[Task])
async def patch_task(task_id: int, updated_task: TaskUpdate, session: SessionDep):
    data = session.get(Task, task_id)
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    updates = updated_task.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(data, key, value)
    session.add(data)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(data)
    return {'data': data}

@app.delete('/tasks/{task_id}', status_code=204)
async def delete_task(task_id: int, session: SessionDep):
    data = session.get(Task, task_id)
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(data)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
