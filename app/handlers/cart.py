from aiogram.enums.parse_mode import ParseMode
from aiogram import F, types

from app.handlers.products import format_price
from app.handlers.router import router
import app.keyboards as kb

from app.database.users_repository import get_user_id_by_telegram_id

import app.database.cart_repository as cart

@router.callback_query(lambda c: c.data.startswith('add-to-cart_'))
async def add_product_to_cart(callback_query: types.CallbackQuery):
    _, product_id = callback_query.data.split('_')
    product_id = int(product_id)

    telegram_id = callback_query.from_user.id
    user_id = await get_user_id_by_telegram_id(telegram_id)
    user_id = int(user_id['id'])
    
    try:
        await cart.add_product_to_cart(product_id, user_id)
        text = 'Товар успешно добавлен в корзину'
    except:
        text = 'Ошибка добавления товара в корзину'

    
    await callback_query.message.reply(text)
    await callback_query.answer()

@router.message(F.text == 'Корзина')
async def catalog_command(message: types.Message):
    telegram_id = message.from_user.id
    products = await cart.get_cart_by_telegram_id(telegram_id, 1, kb.CART_LIST_SIZE)
    products_count = (await cart.get_cart_size(telegram_id))['count']

    text = 'В случае необходимости редактирования корзины \
        выберите редактируемый товар:\n\n'

    counter = 1
    for product in products:
        name = product["name"]
        price = product["price"]
        new_price = product["new_price"]
        user_quantity = int(product["user_quantity"])
        price_text = format_price(price, new_price)
        if not new_price:
            full_price_text = format_price(price*user_quantity, None)
        else:
            full_price_text = format_price(price*user_quantity, new_price*user_quantity)
        
        text += f'Товар №{counter}\nНаименование: {name}\nСтоимость: {price_text}\nКоличество: {user_quantity}\nОбщая стоимость: {full_price_text}\n\n' 
        counter += 1

    keyboard = kb.create_cart_keyboard(products, 1, products_count)
    markup = keyboard.as_markup()

    await message.reply(text, reply_markup=markup, parse_mode=ParseMode.HTML)


@router.callback_query(lambda c: c.data.startswith('cart-proudcts_'))
async def process_products_pagination(callback_query: types.CallbackQuery):
    _, start = callback_query.data.split('_')
    start = int(start)

    telegram_id = callback_query.from_user.id
    products = await cart.get_cart_by_telegram_id(telegram_id, start, kb.CART_LIST_SIZE)
    products_count = (await cart.get_cart_size(telegram_id))['count']

    text = 'В случае необходимости редактирования корзины \
        выберите редактируемый товар:\n\n'

    counter = start
    for product in products:
        name = product["name"]
        price = product["price"]
        new_price = product["new_price"]
        user_quantity = int(product["user_quantity"])
        price_text = format_price(price, new_price)
        if not new_price:
            full_price_text = format_price(price*user_quantity, None)
        else:
            full_price_text = format_price(price*user_quantity, new_price*user_quantity)
        
        text += f'Товар №{counter}\nНаименование: {name}\nСтоимость: {price_text}\nКоличество: {user_quantity}\nОбщая стоимость: {full_price_text}\n\n' 
        counter += 1

    keyboard = kb.create_cart_keyboard(products, start, products_count)
    markup = keyboard.as_markup()

    await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback_query.answer()