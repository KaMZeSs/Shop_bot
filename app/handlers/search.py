from aiogram import F, types
from aiogram.filters import StateFilter
from aiogram.enums.parse_mode import ParseMode

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import app.database.products_repository as prod

from app.handlers.products import format_price
import app.keyboards as kb

from app.handlers.router import router

class Search(StatesGroup):
    search_text_typing = State()
    
@router.message(StateFilter(None), F.text == 'Поиск товара')
async def cmd_food(message: types.Message, state: FSMContext):
    await message.answer(text='Введите поисковый запрос:', reply_markup=kb.search)
    await state.set_state(Search.search_text_typing)

@router.message(F.text == 'Отменить поиск')
async def search_stop(message: types.Message, state: FSMContext):
    await message.answer(text='Поиск отменён', reply_markup=kb.catalog)
    await state.clear()

@router.message(Search.search_text_typing, F.text.is_not('Отменить поиск'))
async def search(message: types.Message, state: FSMContext):
    text = message.text

    products = await prod.search_products_small(text, 1, kb.PRODUCTS_LIST_SIZE)

    if products is None or len(products) == 0:
        text = 'По данному запросу не найдены товары'
        await message.answer(text)
        return
    
    text = "Выберите товар из результатов поиска:"
    await message.answer(text, reply_markup=kb.catalog)

    text = ''

    counter = 1
    for product in products:
        articul = product["id"]
        name = product["name"]
        price = product["price"]
        new_price = product["new_price"]
        discount = product["discount"]
        price_text = format_price(price, new_price, discount)
        product_text = f"<i>{counter}.</i> [{articul}] {name} - {price_text}\n\n"
        text += product_text
        counter += 1

    keyboard = kb.create_products_keyboard(products, None, 1, kb.PRODUCTS_LIST_SIZE)
    markup = keyboard.as_markup()

    await message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await state.clear()