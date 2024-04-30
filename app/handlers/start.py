from aiogram import types
from aiogram.filters.command import Command

from app.handlers.router import router
from app.database.users_repository import get_or_create_user
import app.keyboards as kb

@router.message(Command('start'))
async def start_command(message: types.Message):
    telegram_id = message.from_user.id
    name = message.from_user.first_name

    await get_or_create_user(telegram_id, name) 

    await message.reply(f"Здравствуйте, {name}! С помощью данного бота Вы можете совершать покупки в магазине КупиПК",
                        reply_markup=kb.main)