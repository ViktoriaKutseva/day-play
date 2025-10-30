# entrypoints/bot/handlers.py - What the bot does

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from ...integrations.database import SessionLocal
from ...integrations.database.models import User, Message as DBMessage

router = Router()


def save_user(telegram_user):
    """Save or update user in database"""
    db = SessionLocal()
    try:
        # Check if user exists
        user = db.query(User).filter(User.telegram_id == telegram_user.id).first()
        
        if not user:
            # New user! Create them
            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name
            )
            db.add(user)
            db.commit()
            print(f"👤 New user saved: {telegram_user.first_name}")
        else:
            print(f"👤 Existing user: {telegram_user.first_name}")
    finally:
        db.close()


def save_message(telegram_id: int, text: str):
    """Save message to database"""
    db = SessionLocal()
    try:
        msg = DBMessage(telegram_id=telegram_id, text=text)
        db.add(msg)
        db.commit()
        print(f"💾 Message saved from user {telegram_id}")
    finally:
        db.close()


@router.message(CommandStart())
async def say_hello(message: Message):
    """When user types /start"""
    # Save this user
    save_user(message.from_user)
    
    # Count how many messages they sent before
    db = SessionLocal()
    count = db.query(DBMessage).filter(DBMessage.telegram_id == message.from_user.id).count()
    db.close()
    
    if count == 0:
        await message.answer(f"Hello, {message.from_user.first_name}! 👋\n\nYou're NEW here! Welcome!")
    else:
        await message.answer(f"Welcome back, {message.from_user.first_name}! 👋\n\nYou've sent me {count} messages before!")


@router.message(F.text)
async def echo(message: Message):
    """Echo back any text message"""
    # Save this message
    save_message(message.from_user.id, message.text)
    
    # Echo it back
    await message.answer(f"You said: {message.text}")