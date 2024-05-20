from aiogram.enums.parse_mode import ParseMode
from aiogram import F, types

from app.handlers.router import router
import app.database.pickup_points_repository as pp

MAX_MESSAGE_LENGTH = 4096

@router.message(F.text == 'Пункты выдачи')
async def special_offers_command(message: types.Message):
    p_points = await pp.get_all_pickup_points()
    
    text_parts = []
    
    cur_text_part = ''
    for point in p_points:
        part = f'Адрес: {point['address']}\nОписание:\n{point['summary']}\n'
        if not point['is_receiving_orders']:
            part += 'Временно не работает\n'
        part += '\n'
        
        if len(cur_text_part) + len(part) > 4096:
            text_parts.append(cur_text_part)
            cur_text_part = part
        else:
            cur_text_part += part

    for part in text_parts:
        await message.answer(part, parse_mode=ParseMode.HTML)