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
        # Создаем задачу для периодического вызова periodic_task
        periodic_task = asyncio.create_task(periodic_task_wrapper(bot))
        await dp.start_polling(bot)
    finally:
        await close_db_pool()
        # Отменяем задачу periodic_task_task
        periodic_task.cancel()


def run_periodic_task(bot):
    asyncio.run(periodic_task_wrapper(bot))

async def periodic_task_wrapper(bot: Bot):
    while True:
        await asyncio.sleep(60)
        await periodic_task(bot)
        

async def periodic_task(bot: Bot):
    # Ваш код функции здесь
    print("Функция вызвана")



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())