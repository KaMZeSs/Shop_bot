from aiogram import F, types

from app.handlers.router import router
import app.keyboards as kb

@router.message(F.text == 'Информация')
async def products_keyboard_command(message: types.Message):
    text = 'Выберите интересующий Вас пункт меню'
    await message.answer(text, reply_markup=kb.info)