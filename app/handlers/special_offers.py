from aiogram.enums.parse_mode import ParseMode
from aiogram import F, types

from app.handlers.products import format_price
from app.handlers.router import router
import app.database.categories_repository as cat
import app.database.products_repository as prod
import app.keyboards as kb


@router.message(F.text == 'Скидки')
async def special_offers_command(message: types.Message):
    categories = await cat.get_categories_with_spec_offers(1, kb.CATEGORIES_LIST_SIZE)
    categories_count = (await cat.get_categories_with_spec_offers_count())['count']

    text = "Выберите категорию:\n\n"
    
    keyboard = kb.create_categories_keyboard(categories, 1, categories_count, '-so_')

    markup = keyboard.as_markup()

    await message.reply(text, reply_markup=markup, parse_mode=ParseMode.HTML)

@router.callback_query(lambda c: c.data.startswith('categories-so_'))
async def process_category_so_pagination(callback_query: types.CallbackQuery):
    _, start = callback_query.data.split('_')
    start = int(start)

    categories = await cat.get_categories_with_spec_offers(start, kb.CATEGORIES_LIST_SIZE)
    categories_count = (await cat.get_categories_with_spec_offers_count())['count']

    text = "Выберите категорию:\n\n"

    keyboard = kb.create_categories_keyboard(categories, start, categories_count, '-so_')
    markup = keyboard.as_markup()

    await callback_query.message.edit_text(text, reply_markup=markup, parse_mode='MarkdownV2')
    await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith('products-so_'))
async def process_products_so_pagination(callback_query: types.CallbackQuery):
    _, category_id, start = callback_query.data.split('_')
    category_id = int(category_id)
    start = int(start)

    products = await prod.get_products_with_special_offers_small(category_id, start, kb.PRODUCTS_LIST_SIZE)
    categories_count = (await prod.get_products_with_special_offers_count(category_id))['count']

    text = "Выберите товар:\n\n"

    counter = 0
    for product in products:
        counter += 1
        name = product["name"]
        price = product["price"]
        new_price = product["new_price"]
        price_text = format_price(price, new_price)
        product_text = f"{counter}. {name} - {price_text}\n"
        text += product_text

    keyboard = kb.create_products_keyboard(products, category_id, start, categories_count)
    markup = keyboard.as_markup()

    await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback_query.answer()