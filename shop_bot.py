import asyncio
import logging
import sys
import dotenv

from aiogram import Bot, Dispatcher

from app.database.database import close_db_pool, get_db_pool, db_pool
from app.handlers.router import router

import pkgutil
from importlib import import_module
import app.handlers

def import_handlers():
    package = app.handlers
    for _, modname, _ in pkgutil.iter_modules(package.__path__):
        module = import_module(f"{package.__name__}.{modname}")

async def main() -> None:
    TOKEN = dotenv.dotenv_values()['API_KEY']
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    import_handlers()
    global db_pool
    db_pool = await get_db_pool()
    try:
        await dp.start_polling(bot)
    finally:
        await close_db_pool()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())