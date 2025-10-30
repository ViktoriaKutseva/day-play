# entrypoints/bot/main.py - Start the bot!

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .handlers import router
from ...config.settings import settings
from ...integrations.database import init_db


async def main():
    """Main function to start the bot"""
    
    print("🚀 Starting Telegram Bot...")
    
    # Initialize database
    print("📊 Setting up database...")
    init_db()
    
    # Create bot
    bot = Bot(
        token=settings.telegram_bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Create dispatcher
    dp = Dispatcher()
    dp.include_router(router)
    
    print("✅ Bot is ready!")
    print("Press Ctrl+C to stop")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        print("👋 Bot stopped. Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())