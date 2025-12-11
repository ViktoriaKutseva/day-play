from pydantic import BaseModel, Field

from day_play.entrypoints.api.schemas.task_schema import TaskResponse


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(description="Response message")


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str = Field(description="Error detail message")

class TaskListResponse(BaseModel):
    """Paginated task list response."""
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
