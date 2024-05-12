from aiogram import F, types
from aiogram.enums.parse_mode import ParseMode

from asyncpg.exceptions import PostgresError

from app.handlers.products import format_price
from app.handlers.router import router
import app.keyboards as kb

from app.database.users_repository import get_user_id_by_telegram_id

import app.database.cart_repository as cart
import app.database.orders_repository as order
import app.database.pickup_points_repository as pick_point

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
    except Exception:
        text = 'Корзина достигла предела'

    
    await callback_query.message.reply(text)
    await callback_query.answer()

@router.message(F.text == 'Корзина')
async def catalog_command(message: types.Message):
    telegram_id = message.from_user.id
    products = await cart.get_cart_by_telegram_id(telegram_id, 1, kb.CART_LIST_SIZE)
    products_count = (await cart.get_cart_size(telegram_id))['count']

    if int(products_count) == 0:
        text = 'Корзина пуста'
        await message.reply(text)
        return

    text = 'В случае необходимости редактирования корзины выберите редактируемый товар:\n\n'

    counter = 1
    for product in products:
        articul = product["id"]
        name = product["name"]
        price = product["price"]
        new_price = product["new_price"]
        discount = product["discount"]
        user_quantity = int(product["user_quantity"])
        price_text = format_price(price, new_price, discount)
        if not new_price:
            full_price_text = format_price(price*user_quantity, None, None)
        else:
            full_price_text = format_price(price*user_quantity, new_price*user_quantity, discount)
        
        text += f'Товар №{counter}\nАртикул: {articul}\nНаименование: {name}\nСтоимость: {price_text}\nКоличество: {user_quantity}\nОбщая стоимость: {full_price_text}\n\n' 
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

    if int(products_count) == 0:
            text = 'Корзина пуста'
            await callback_query.message.edit_text(text, parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return

    text = 'В случае необходимости редактирования корзины выберите редактируемый товар:\n\n'

    counter = start
    for product in products:
        articul = product["id"]
        name = product["name"]
        price = product["price"]
        discount = product["discount"]
        new_price = product["new_price"]
        user_quantity = int(product["user_quantity"])
        price_text = format_price(price, new_price, discount)
        if not new_price:
            full_price_text = format_price(price*user_quantity, None, None)
        else:
            full_price_text = format_price(price*user_quantity, new_price*user_quantity, discount)
        
        text += f'Товар №{counter}\nАртикул: {articul}\nНаименование: {name}\n\
Стоимость: {price_text}\n\
Количество: {user_quantity}\n\
Общая стоимость: {full_price_text}\n\n' 
        counter += 1

    keyboard = kb.create_cart_keyboard(products, start, products_count)
    markup = keyboard.as_markup()

    await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith('cart_'))
async def process_cart_products_selection(callback_query: types.CallbackQuery):
    _, product_id = callback_query.data.split('_')
    product_id = int(product_id)

    telegram_id = callback_query.from_user.id
    product = await cart.get_cart_product_info(telegram_id, product_id)

    if product is None:
        await callback_query.message.reply('Товара нет в корзине', parse_mode=ParseMode.HTML)
        await callback_query.answer()
        return
    
    articul = product["id"]
    name = product["name"]
    price = product["price"]
    new_price = product["new_price"]
    discount = product["discount"]
    user_quantity = int(product["user_quantity"])
    price_text = format_price(price, new_price, discount)
    if not new_price:
        full_price_text = format_price(price*user_quantity, None, None)
    else:
        full_price_text = format_price(price*user_quantity, new_price*user_quantity, discount)
        
    text = f'Артикул: {articul}\nНаименование: {name}\nСтоимость: {price_text}\nКоличество: {user_quantity}\nОбщая стоимость: {full_price_text}\n\n'

    keyboard = kb.create_cart_product_keyboard(product_id, user_quantity)
    markup = keyboard.as_markup()

    await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith('cart-prouduct_'))
async def process_cart_products_action(callback_query: types.CallbackQuery):
    _, action, product_id = callback_query.data.split('_')
    product_id = int(product_id)

    telegram_id = callback_query.from_user.id

    try:
        if action == 'remove':
            await cart.delete_product_from_cart(telegram_id, product_id)

            products = await cart.get_cart_by_telegram_id(telegram_id, 1, kb.CART_LIST_SIZE)
            products_count = (await cart.get_cart_size(telegram_id))['count']

            if int(products_count) == 0:
                text = 'Корзина пуста'
                await callback_query.message.edit_text(text, parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return

            text = 'В случае необходимости редактирования корзины выберите редактируемый товар:\n\n'

            counter = 1
            for product in products:
                articul = product["id"]
                name = product["name"]
                price = product["price"]
                discount = product["discount"]
                new_price = product["new_price"]
                user_quantity = int(product["user_quantity"])
                price_text = format_price(price, new_price, discount)
                if not new_price:
                    full_price_text = format_price(price*user_quantity, None, None)
                else:
                    full_price_text = format_price(price*user_quantity, new_price*user_quantity, discount)
                
                text += f'Товар №{counter}\nАртикул: {articul}\nНаименование: {name}\nСтоимость: {price_text}\nКоличество: {user_quantity}\nОбщая стоимость: {full_price_text}\n\n'
                counter += 1

            keyboard = kb.create_cart_keyboard(products, 1, products_count)
            markup = keyboard.as_markup()

            await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return

        if action == 'increase':
            await cart.increase_product_in_cart(telegram_id, product_id)
        else:
            await cart.decrease_product_in_cart(telegram_id, product_id)

        product = await cart.get_cart_product_info(telegram_id, product_id)
        
        articul = product["id"]
        name = product["name"]
        price = product["price"]
        discount = product["discount"]
        new_price = product["new_price"]
        user_quantity = int(product["user_quantity"])
        price_text = format_price(price, new_price, discount)
        if not new_price:
            full_price_text = format_price(price*user_quantity, None, discount)
        else:
            full_price_text = format_price(price*user_quantity, new_price*user_quantity, discount)
            
        text = f'Артикул: {articul}\nНаименование: {name}\nСтоимость: {price_text}\nКоличество: {user_quantity}\nОбщая стоимость: {full_price_text}\n\n'

        keyboard = kb.create_cart_product_keyboard(product_id, user_quantity)
        markup = keyboard.as_markup()

        await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
        await callback_query.answer()
    except:
        await callback_query.message.reply('Ошибка выполнения действия', parse_mode=ParseMode.HTML)
        await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith('cart-back'))
async def process_cart_products_selection(callback_query: types.CallbackQuery):
    start = 1

    telegram_id = callback_query.from_user.id
    products = await cart.get_cart_by_telegram_id(telegram_id, start, kb.CART_LIST_SIZE)
    products_count = (await cart.get_cart_size(telegram_id))['count']

    if int(products_count) == 0:
            text = 'Корзина пуста'
            await callback_query.message.edit_text(text, parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return

    text = 'В случае необходимости редактирования корзины выберите редактируемый товар:\n\n'

    counter = start
    for product in products:
        articul = product["id"]
        name = product["name"]
        price = product["price"]
        discount = product["discount"]
        new_price = product["new_price"]
        user_quantity = int(product["user_quantity"])
        price_text = format_price(price, new_price, discount)
        if not new_price:
            full_price_text = format_price(price*user_quantity, None, None)
        else:
            full_price_text = format_price(price*user_quantity, new_price*user_quantity, discount)
        
        text += f'Товар №{counter}\nАртикул: {articul}\nНаименование: {name}\n\
Стоимость: {price_text}\n\
Количество: {user_quantity}\n\
Общая стоимость: {full_price_text}\n\n' 
        counter += 1

    keyboard = kb.create_cart_keyboard(products, start, products_count)
    markup = keyboard.as_markup()

    await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith('start-place-order'))
async def start_place_order(callback_query: types.CallbackQuery):
    telegram_id = callback_query.from_user.id

    cart_len = (await cart.get_cart_size(telegram_id))['count']
    if cart_len == 0:
        text = 'Невозможно создать заказ, так как корзина пуста'
        await callback_query.message.answer(text)
        await callback_query.answer()
        return

    shortage_products = await cart.get_shortage_by_telegram_id(telegram_id)

    if not shortage_products:
        text = 'Выберите адрес пункта самовывоза:\n\n'
        pickup_points = await pick_point.get_pickup_points(1, kb.PICKUP_POINTS_LIST_SIZE)
        pickup_points_count = (await pick_point.get_pickup_points_count())['count']

        counter = 1
        for pickup_point in pickup_points:
            text += f'Пункт самовывоза №{counter}\n'
            address = pickup_point['address']
            text += f'Адрес: {address}\n\n'
            counter += 1

        keyboard = kb.create_pickup_points_order_keyboard(pickup_points, 1, pickup_points_count)
        markup = keyboard.as_markup()

        await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
        await callback_query.answer()
    else:
        text = 'Данных товаров недостаточно на складе:\n\n'
        for product in shortage_products:
            articul = product['id']
            name = product['name']
            user_quantity = product['user_quantity']
            shop_quantity = product['shop_quantity']
            shortage = int(user_quantity) - int(shop_quantity)
            text += f'[{articul}] {name}\nНедостаточно товаров: {shortage}\n\n'

        text += 'Пожалуйста, уменьшите количество товаров в заказе.\nПросим прощения за неудобства.'
        
        await callback_query.message.reply(text, parse_mode=ParseMode.HTML)
        await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith('order-pickup-points_'))
async def start_place_order_pickup_points_pagination(callback_query: types.CallbackQuery):
    _, start = callback_query.data.split('_')
    start = int(start)

    text = 'Выберите адрес пункта самовывоза:\n\n'
    pickup_points = await pick_point.get_pickup_points(start, kb.PICKUP_POINTS_LIST_SIZE)
    pickup_points_count = (await pick_point.get_pickup_points_count())['count']

    counter = start
    for pickup_point in pickup_points:
        text += f'Пункт самовывоза №{counter}\n'
        address = pickup_point['address']
        text += f'Адрес: {address}\n\n'
        counter += 1

    keyboard = kb.create_pickup_points_order_keyboard(pickup_points, start, pickup_points_count)
    markup = keyboard.as_markup()

    await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith('order-pickup-point_'))
async def end_place_order(callback_query: types.CallbackQuery):
    _, pickup_point_id = callback_query.data.split('_')
    pickup_point_id = int(pickup_point_id)

    telegram_id = callback_query.from_user.id

    cart_len = (await cart.get_cart_size(telegram_id))['count']
    if cart_len == 0:
        text = 'Невозможно создать заказ, так как корзина пуста'
        await callback_query.message.answer(text)
        await callback_query.answer()
        return

    shortage_products = await cart.get_shortage_by_telegram_id(telegram_id)
    pickup_point_info = await pick_point.get_point_info(pickup_point_id)
    
    if not pickup_point_info:
        text = 'Выбранный Вами пункт выдачи не существует'
        await callback_query.message.reply(text)
        await callback_query.answer()
        return
    if not bool(pickup_point_info['is_works']):
        text = 'Выбранный Вами пункт выдачи в данный момент не работает'
        await callback_query.message.reply(text)
        await callback_query.answer()
        return

    if len(shortage_products) != 0:
        text = 'Данных товаров недостаточно на складе:\n\n'
        for product in shortage_products:
            articul = product['name']
            name = product['name']
            user_quantity = product['user_quantity']
            shop_quantity = product['shop_quantity']
            shortage = int(user_quantity) - int(shop_quantity)
            text += f'Артикул: {articul}\nНаименование: {name}\nКоличество: {user_quantity}\nНедостаточно товаров: {shortage}\n\n'

        text += 'Пожалуйста, уменьшите количество товаров в заказе.\nПросим прощения за неудобства.'
        
        await callback_query.message.reply(text, parse_mode=ParseMode.HTML)
        await callback_query.answer()
        return
    try:
        await order.create_new_order(telegram_id, pickup_point_id)
        await callback_query.message.answer('Заказ успешно создан')
    except PostgresError as e:
        await callback_query.message.answer(f'Ошибка размещения заказа: {e}')
    
    await callback_query.answer()