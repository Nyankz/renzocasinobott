import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import start, balance, games, admin

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Создаем диспетчер
dp = Dispatcher()

async def main():
    # Подключаем роутеры
    dp.include_router(start.router)
    dp.include_router(balance.router)
    dp.include_router(games.router)
    dp.include_router(admin.router)
    
    # Инициализируем базу данных
    from database import init_db
    init_db()
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())