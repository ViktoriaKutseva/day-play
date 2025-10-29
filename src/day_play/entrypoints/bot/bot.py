from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError
import os
import httpx
from dotenv import load_dotenv
from loguru import logger
from src.day_play.config.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Configure logging
setup_logging()

logger.info("Bot application initialized")

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


async def get_or_create_user(telegram_user_id: int, name: str) -> dict | None:
    """Get or create a user in the database via API."""
    try:
        async with httpx.AsyncClient() as client:
            # Try to get existing user
            response = await client.get(f"{API_BASE_URL}/users/{telegram_user_id}")
            if response.status_code == 200:
                return response.json()["data"]
            
            # User doesn't exist, create new one
            response = await client.post(
                f"{API_BASE_URL}/users",
                json={"user_id": telegram_user_id, "name": name}
            )
            if response.status_code == 201:
                logger.info(f"Created new user: {name} (Telegram ID: {telegram_user_id})")
                return response.json()["data"]
            
            logger.error(f"Failed to create user: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error getting/creating user: {e}")
        return None


async def get_user_tasks(user_db_id: int) -> list[dict]:
    """Get all tasks for a user from the API."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/tasks?creator_id={user_db_id}")
            if response.status_code == 200:
                return response.json()["data"]
            logger.error(f"Failed to get tasks: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return []


async def complete_task(task_id: int, user_db_id: int) -> dict | None:
    """Mark a task as completed via API."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/completions",
                json={"task_id": task_id, "user_id": user_db_id}
            )
            if response.status_code == 201:
                return response.json()["data"]
            logger.error(f"Failed to complete task: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return None


def create_tasks_keyboard(tasks: list[dict]) -> InlineKeyboardMarkup:
    """Create inline keyboard from tasks list."""
    keyboard = []
    for task in tasks:
        # Show task name with score
        button_text = f"⭐ {task['name']} (+{task['score']} pts)"
        callback_data = f"complete_{task['id']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    if not keyboard:
        keyboard.append([InlineKeyboardButton("➕ No tasks yet", callback_data="none")])
    
    return InlineKeyboardMarkup(keyboard)
    
async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /tasks command - show user's tasks."""
    try:
        if not update.message or not update.effective_user:
            logger.warning("Received /tasks command without message or user")
            return

        telegram_user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "User"

        logger.info("Processing /tasks command", user_id=telegram_user_id)

        # Get or create user in database
        user = await get_or_create_user(telegram_user_id, user_name)
        if not user:
            await update.message.reply_text("❌ Sorry, there was an error accessing your account.")
            return

        # Get user's tasks from API
        tasks = await get_user_tasks(user["id"])
        
        if not tasks:
            await update.message.reply_text(
                "📝 You don't have any tasks yet!\n\n"
                f"Your current score: {user['score']} points\n"
                f"Level: {user['lvl']}"
            )
            return

        # Create keyboard with tasks
        keyboard = create_tasks_keyboard(tasks)
        
        # Store user_db_id in context for callback handler
        context.user_data["user_db_id"] = user["id"]
        
        text = (
            f"📝 Your Tasks (Level {user['lvl']})\n"
            f"💰 Current Score: {user['score']} points\n\n"
            f"Click a task to complete it:"
        )
        
        await update.message.reply_text(text, reply_markup=keyboard)

        logger.info("Successfully sent tasks list", user_id=telegram_user_id, task_count=len(tasks))

    except TelegramError as e:
        logger.error("Telegram error in tasks_command", error=str(e), user_id=update.effective_user.id if update.effective_user else None)
        await update.message.reply_text("❌ Sorry, there was an error sending your tasks.")
    except Exception as e:
        logger.error("Unexpected error in tasks_command", error=str(e), user_id=update.effective_user.id if update.effective_user else None)
        await update.message.reply_text("❌ Sorry, something went wrong.")


async def complete_task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks to complete tasks."""
    try:
        if not update.callback_query or not update.effective_user:
            logger.warning("Received callback without callback_query or user")
            return

        query = update.callback_query
        await query.answer()

        # Extract task ID from callback data
        callback_data = query.data
        if not callback_data or not callback_data.startswith("complete_"):
            logger.warning("Invalid callback data received", callback_data=callback_data)
            return
        
        if callback_data == "none":
            await query.answer("No tasks available")
            return

        task_id = int(callback_data.split("_")[1])
        user_db_id = context.user_data.get("user_db_id")
        
        if not user_db_id:
            # Fallback: get user from database
            telegram_user_id = update.effective_user.id
            user_name = update.effective_user.first_name or "User"
            user = await get_or_create_user(telegram_user_id, user_name)
            if not user:
                await query.edit_message_text("❌ Error accessing your account.")
                return
            user_db_id = user["id"]
            context.user_data["user_db_id"] = user_db_id

        logger.info("Processing task completion", task_id=task_id, user_id=update.effective_user.id)

        # Complete the task via API
        result = await complete_task(task_id, user_db_id)
        
        if not result:
            await query.answer("❌ Error completing task")
            return

        # Get updated tasks list
        tasks = await get_user_tasks(user_db_id)
        
        # Show success message with points earned
        success_text = (
            f"✅ Task completed: {result['task_name']}!\n"
            f"🎉 +{result['points_awarded']} points earned\n"
            f"💰 Total Score: {result['user_score']} points\n"
            f"⭐ Level: {result['user_level']}\n\n"
        )
        
        if tasks:
            keyboard = create_tasks_keyboard(tasks)
            success_text += "Click another task to complete:"
            await query.edit_message_text(success_text, reply_markup=keyboard)
        else:
            success_text += "🎊 All tasks completed! Great job!"
            await query.edit_message_text(success_text)

        logger.info("Successfully completed task", task_id=task_id, points=result['points_awarded'])

    except ValueError as e:
        logger.error("Invalid task ID format", error=str(e), callback_data=query.data if update.callback_query else None)
        await query.answer("❌ Invalid task")
    except TelegramError as e:
        logger.error("Telegram error in complete_task_callback", error=str(e), user_id=update.effective_user.id if update.effective_user else None)
        await query.answer("❌ Error updating message")
    except Exception as e:
        logger.error("Unexpected error in complete_task_callback", error=str(e), user_id=update.effective_user.id if update.effective_user else None)
        await query.answer("❌ Something went wrong")


def main() -> None:
    """Start the Telegram bot."""
    try:
        logger.info("Starting Telegram bot application")

        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

        api_url = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
        logger.info(f"Using API at: {api_url}")

        logger.info("Initializing bot with token")
        app = ApplicationBuilder().token(token).build()

        # Add handlers
        app.add_handler(CommandHandler("tasks", tasks_command))
        app.add_handler(CallbackQueryHandler(complete_task_callback))

        logger.info("Bot handlers registered, starting polling")
        # Run the bot
        app.run_polling()

    except ValueError as e:
        logger.error("Configuration error", error=str(e))
        raise
    except TelegramError as e:
        logger.error("Telegram API error during bot initialization", error=str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error during bot startup", error=str(e))
        raise


if __name__ == "__main__":
    main()

