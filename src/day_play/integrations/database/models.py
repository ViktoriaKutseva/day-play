# integrations/database/models.py - Database tables

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from . import Base


class User(Base):
    """User table in database"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Message(Base):
    """Message table in database"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, nullable=False, index=True)
    text = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)