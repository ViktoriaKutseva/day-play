# models/entities.py - The basic shapes of our data

from pydantic import BaseModel, Field
from datetime import datetime


class UserEntity(BaseModel):
    """A user - like a profile card"""
    id: int | None = None
    telegram_id: int = Field(..., gt=0)  # Must be positive number
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True  # Can convert from database


class MessageEntity(BaseModel):
    """A message - like a chat bubble"""
    id: int | None = None
    telegram_id: int = Field(..., gt=0)
    text: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True