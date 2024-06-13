from aiogram.enums.parse_mode import ParseMode
from aiogram import F, types

from app.handlers.router import router
import app.database.categories_repository as cat
import app.keyboards as kb


@router.message(F.text == 'Товары')
async def products_keyboard_command(message: types.Message):
    text = 'Выберите интересующий Вас пункт меню'
    await message.answer(text, reply_markup=kb.catalog)

@router.message(F.text == 'Каталог')
async def catalog_command(message: types.Message):
    categories = await cat.get_categories(1, kb.CATEGORIES_LIST_SIZE)
    categories_count = (await cat.get_categories_count())['count']

    text = "Выберите категорию:\n\n"
    
    keyboard = kb.create_categories_keyboard(categories, 1, categories_count)

    markup = keyboard.as_markup()

    await message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)

@router.callback_query(lambda c: c.data.startswith('categories_'))
async def process_category_pagination(callback_query: types.CallbackQuery):
    _, start = callback_query.data.split('_')
    start = int(start)

    categories = await cat.get_categories(start, kb.CATEGORIES_LIST_SIZE)
    categories_count = (await cat.get_categories_count())['count']

    text = "Выберите категорию:\n\n"

    keyboard = kb.create_categories_keyboard(categories, start, categories_count)
    markup = keyboard.as_markup()

    await callback_query.message.edit_text(text, reply_markup=markup, parse_mode='MarkdownV2')
    await callback_query.answer()