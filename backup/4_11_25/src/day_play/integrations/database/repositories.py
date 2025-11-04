# integrations/database/repositories.py - Database operations

from sqlalchemy.orm import Session
from typing import Optional

from .models import ToDoItem, User, Message
from ...models.entities import UserEntity, MessageEntity, ToDoItemEntity


class UserRepository:
    """Manages user data in database"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_entity: UserEntity) -> UserEntity:
        """Save a new user"""
        db_user = User(
            telegram_id=user_entity.telegram_id,
            username=user_entity.username,
            first_name=user_entity.first_name,
            last_name=user_entity.last_name,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        print(f"✅ User {user_entity.first_name} saved!")
        return UserEntity.model_validate(db_user)
    
    def get_by_telegram_id(self, telegram_id: int) -> Optional[UserEntity]:
        """Find user by Telegram ID"""
        db_user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
        if db_user:
            return UserEntity.model_validate(db_user)
        return None
    
    def get_or_create(self, user_entity: UserEntity) -> UserEntity:
        """Get existing user or create new one"""
        existing = self.get_by_telegram_id(user_entity.telegram_id)
        if existing:
            print(f"👤 Welcome back, {existing.first_name}!")
            return existing
        print(f"🆕 New user: {user_entity.first_name}")
        return self.create(user_entity)


class MessageRepository:
    """Manages messages in database"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, message_entity: MessageEntity) -> MessageEntity:
        """Save a message"""
        db_message = Message(
            telegram_id=message_entity.telegram_id,
            text=message_entity.text,
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        
        print(f"💾 Message saved!")
        return MessageEntity.model_validate(db_message)
    
    def count_by_user(self, telegram_id: int) -> int:
        """Count messages from user"""
        return self.db.query(Message).filter(Message.telegram_id == telegram_id).count()
    
class ToDoRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, todo_entity: ToDoItemEntity) -> ToDoItemEntity:
        """Save a new to-do item"""
        db_todo = ToDoItem(
            user_id=todo_entity.user_id,
            title=todo_entity.title,
            description=todo_entity.description,
            is_completed=1 if todo_entity.is_completed else 0,  # Convert bool to int
            score=todo_entity.score,
        )
        self.db.add(db_todo)
        self.db.commit()
        self.db.refresh(db_todo)
        
        # Convert back to entity
        return ToDoItemEntity.model_validate(db_todo)
    
    def get_by_user(self, user_id: int) -> list[ToDoItemEntity]:
        """Get all todos for a user"""
        db_todos = self.db.query(ToDoItem).filter(ToDoItem.user_id == user_id).all()
        return [ToDoItemEntity.model_validate(todo) for todo in db_todos]
    
    def update(self, todo_entity: ToDoItemEntity) -> ToDoItemEntity | None:
        """Update an existing to-do item"""
        db_todo = self.db.query(ToDoItem).filter(ToDoItem.id == todo_entity.id).first()
        if db_todo:
            db_todo.user_id = todo_entity.user_id
            db_todo.title = todo_entity.title
            db_todo.description = todo_entity.description
            db_todo.is_completed = 1 if todo_entity.is_completed else 0
            db_todo.score = todo_entity.score
            self.db.commit()
            self.db.refresh(db_todo)
            return ToDoItemEntity.model_validate(db_todo)
        return None
    
    def delete(self, todo_id: int) -> bool:
        """Delete a to-do item"""
        db_todo = self.db.query(ToDoItem).filter(ToDoItem.id == todo_id).first()
        if db_todo:
            self.db.delete(db_todo)
            self.db.commit()
            return True
        return False