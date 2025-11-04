# entrypoints/bot/handlers.py - REFACTORED

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from ...models.entities import UserEntity, ToDoItemEntity
from ...integrations.database.repositories import UserRepository, MessageRepository, ToDoRepository
from ...integrations.database.database import SessionLocal



router = Router()

class AddTaskStates(StatesGroup):
    waiting_for_task = State()

def get_user_repository():
    """Factory function for UserRepository"""
    db = SessionLocal()
    return UserRepository(db)

def get_message_repository():
    """Factory function for MessageRepository"""
    db = SessionLocal()
    return MessageRepository(db)

@router.message(CommandStart())
async def cmd_start(message: Message):
    kb = [
        [KeyboardButton(text="Добавить задачу")],
        [KeyboardButton(text="Посмотреть задачи")],
        [KeyboardButton(text="Помощь")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="пу пу пу")  
    await message.answer("Что хочешь сделать?", reply_markup=keyboard)
    user_entity = UserEntity(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    logger.info(f"User started bot: {user_entity}") 
    # Use repository to save/get user
    repo = get_user_repository()
    saved_user = repo.get_or_create(user_entity)
    
    msg_repo = get_message_repository()
    message_count = msg_repo.count_by_user(message.from_user.id)
    
    if message_count == 0:
        await message.answer(f"Hello, {saved_user.first_name}! 👋\n\nYou're NEW here! Welcome!")
    else:
        await message.answer(f"Welcome back, {saved_user.first_name}! 👋\n\nYou've sent me {message_count} messages before!")

@router.message(F.text == "/help")
async def process_help_command(message: Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")

def get_todo_reposito ry():
    """Factory function for ToDoRepository"""
    db = SessionLocal()
    return ToDoRepository(db)

@router.message(F.text == "/list_todos")
async def list_todos(message: Message):
    """List all user's to-do items"""
    # Note: You'll need to add a method to ToDoRepository for this
    # For now, this shows the pattern
    await message.answer("Todo listing not implemented yet")

@router.message(F.text == "Добавить задачу")
async def handle_add_task_button(message: Message, state: FSMContext):
    """Handle the 'Add task' button click"""
    await state.set_state(AddTaskStates.waiting_for_task)
    await message.answer("Введите задачу")
    if message.from_user:
        logger.info(f"User {message.from_user.id} started adding task")
    else:
        logger.warning("Message from unknown user")

@router.message(AddTaskStates.waiting_for_task)
async def process_task_input(message: Message, state: FSMContext):
    """Process the task input from user"""
    if not message.text or not message.text.strip():
        await message.answer("Пожалуйста, введите текст задачи.")
        return
    
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.")
        await state.clear()
        return
    
    todo_entity = ToDoItemEntity(
        user_id=message.from_user.id,
        title=message.text.strip(),
        description=None,
        is_completed=False,
        score=0
    )
    repo = get_todo_repository()
    saved_todo = repo.create(todo_entity)
    
    await message.answer(f"✅ Задача добавлена: {saved_todo.title}")
    await state.clear()
    logger.info(f"User {message.from_user.id} added task: {saved_todo}")

@router.message(F.text == "Посмотреть задачи")
async def handle_view_tasks_button(message: Message):
    """Handle the 'View tasks' button click"""
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.")
        return
    
    repo = get_todo_repository()
    todos = repo.list_by_user(message.from_user.id)
    
    if not todos:
        await message.answer("У вас нет задач.")
        return
    
    response_lines = ["Ваши задачи:"]
    for todo in todos:
        status = "✅" if todo.is_completed else "❌"
        response_lines.append(f"{status} {todo.title}")
    
    response_text = "\n".join(response_lines)
    await message.answer(response_text)