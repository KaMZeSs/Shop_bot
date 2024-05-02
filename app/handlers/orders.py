from aiogram.enums.parse_mode import ParseMode
from aiogram import F, types

from app.handlers.router import router
import app.database.categories_repository as cat
import app.keyboards as kb

@router.message(F.text == 'Заказы')
async def products_keyboard_command(message: types.Message):
    text = 'Выберите интересующий Вас пункт меню'
    await message.answer(text, reply_markup=kb.orders)