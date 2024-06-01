import asyncio
import logging
import sys
import dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.bot import DefaultBotProperties


from app.notifications.news import send_news
from app.notifications.orders import send_order_notifications
from app.database.database import close_db_pool, get_db_pool, db_pool
from app.handlers.router import router

import pkgutil
from importlib import import_module
import app.handlers

def import_handlers():
    package = app.handlers
    for _, modname, _ in pkgutil.iter_modules(package.__path__):
        _ = import_module(f"{package.__name__}.{modname}")

async def main() -> None:
    TOKEN = dotenv.dotenv_values()['API_KEY']
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    import_handlers()

    global db_pool
    db_pool = await get_db_pool()

    try:
        news_task = asyncio.create_task(news_task_wrapper(bot))
        order_notifications_task = asyncio.create_task(orders_task_wrapper(bot))
        await dp.start_polling(bot)
    finally:
        await close_db_pool()
        news_task.cancel()
        order_notifications_task.cancel()


async def news_task_wrapper(bot: Bot):
    while True:
        await asyncio.sleep(2)
        await send_order_notifications(bot)
        
async def orders_task_wrapper(bot: Bot):
    while True:
        await asyncio.sleep(2)
        await send_news(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())