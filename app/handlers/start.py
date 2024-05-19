from aiogram import F, types
from aiogram.filters.command import Command

from app.handlers.router import router
from app.database.users_repository import get_or_create_user
import app.keyboards as kb

@router.message(Command('start'))
async def start_command(message: types.Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name

    await get_or_create_user(telegram_id, name) 

    await message.answer(f"Здравствуйте, {name}! С помощью данного бота Вы можете совершать покупки в магазине КупиПК",
                        reply_markup=kb.main)
    
@router.message(F.text == 'Назад')
async def products_keyboard_command(message: types.Message):
    text = 'Выберите интересующий Вас пункт меню'
    await message.answer(text, reply_markup=kb.main)