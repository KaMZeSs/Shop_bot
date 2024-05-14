from aiogram import F, types
from aiogram.enums.parse_mode import ParseMode

import app.database.orders_repository as order

from app.handlers.router import router
import app.keyboards as kb

from datetime import datetime

statuses = {
    "created": "Создан",
    "canceled": "Отменен",
    "submitted": "Подтвержден",
    "ready": "Готов к получению",
}

@router.message(F.text == 'Заказы')
async def products_keyboard_command(message: types.Message):
    text = 'Выберите интересующий Вас пункт меню'
    await message.answer(text, reply_markup=kb.orders)


@router.message(F.text == 'Текущие заказы')
async def products_keyboard_command(message: types.Message):

    telegram_id = message.from_user.id

    orders = await order.get_user_orders(telegram_id, True, 1, kb.ORDERS_LIST_SIZE)
    orders_count = (await order.get_orders_count(telegram_id, True))['count']

    if int(orders_count) == 0:
        text = 'У Вас нет текущих заказов'
        await message.answer(text)
        return
    
    text = 'Выберите интересующий Вас заказ\n\n'

    counter = 1
    for item in orders:
        pickup_point_address = item["pickup_point_address"]
        
        id = item["order_id"]
        
        try:
            status = item["status"]
            status = statuses[status]
        except:
            pass
        
        order_timestamp = item["order_timestamp"]
        formatted_dt = order_timestamp.strftime("%H:%M %d.%m.%Y")

        total_price = item["total_price"]
        total_count = int(item["total_count"])
        text += f'Заказ №{counter} от {formatted_dt}\nИдентификатор: <b>{id}</b>\nСтатус: {status}\nТоваров: {total_count} на {total_price}руб.\nПункт выдачи: {pickup_point_address}\n\n' 
        counter += 1

    keyboard = kb.create_orders_keyboard(orders, 1, orders_count, True)
    markup = keyboard.as_markup()

    await message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)

@router.callback_query(lambda c: c.data.startswith('orders_'))
async def process_orders_pagination(callback_query: types.CallbackQuery):
    _, is_current, start = callback_query.data.split('_')
    start = int(start)
    is_current = True if is_current == 'current' else False

    telegram_id = callback_query.from_user.id

    orders = await order.get_user_orders(telegram_id, is_current, start, kb.ORDERS_LIST_SIZE)
    orders_count = (await order.get_orders_count(telegram_id, is_current))['count']

    if int(orders_count) == 0:
        if is_current:
            text = 'У Вас нет текущих заказов'
        else:
            text = 'У Вас нет заказов в истории'
        await callback_query.answer(text)
        return
    
    text = 'Выберите интересующий Вас заказ\n\n'

    counter = start
    for item in orders:
        pickup_point_address = item["pickup_point_address"]
        
        id = item["order_id"]
        
        try:
            status = item["status"]
            status = statuses[status]
        except:
            pass
        
        order_timestamp = item["order_timestamp"]
        formatted_dt = order_timestamp.strftime("%H:%M %d.%m.%Y")

        total_price = item["total_price"]
        total_count = int(item["total_count"])
        text += f'Заказ №{counter} от {formatted_dt}\nИдентификатор: <b>{id}</b>\nСтатус: {status}\nТоваров: {total_count} на {total_price}руб.\nПункт выдачи: {pickup_point_address}\n\n' 
        counter += 1

    keyboard = kb.create_orders_keyboard(orders, start, orders_count, is_current)
    markup = keyboard.as_markup()

    await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)

@router.callback_query(lambda c: c.data.startswith('order_'))
async def process_order_info(callback_query: types.CallbackQuery):
    _, order_id = callback_query.data.split('_')
    order_id = int(order_id)

    is_history = await order.get_is_order_history(order_id)
    is_history = is_history['is_history']

    order_items = await order.get_order_items(order_id, 1, kb.ORDER_ITEMS_LIST_SIZE)
    order_items_count = await order.get_order_items_count(order_id)
    order_items_count = int(order_items_count['count'])

    text = f'Заказ <b>{order_id}</b>\n\n' if is_history else f'Для отмены заказа <b>{order_id}</b> нажмите на кнопку\n\n'

    for product in order_items:
        articul = product["id"]
        name = product["name"]
        price = product["price"]
        quantity = product["quantity"]
        total_price = product["total_price"]
        text += f'Артикул: {articul}\nНаименование: {name}\nСтоимость: {price}\nКоличество: {quantity}\nОбщая стоимость: {total_price}\n\n'

    if is_history:
        await callback_query.message.answer(text, parse_mode=ParseMode.HTML)
    else:
        keyboard = kb.create_order_items_keyboard(order_id, 1, order_items_count, not is_history)
        markup = keyboard.as_markup()
        await callback_query.message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)

@router.callback_query(lambda c: c.data.startswith('order-items_'))
async def process_order_items_pagination(callback_query: types.CallbackQuery):
    _, order_id, start = callback_query.data.split('_')
    order_id = int(order_id)
    start = int(start)

    is_history = await order.get_is_order_history(order_id)
    is_history = is_history['is_history']

    order_items = await order.get_order_items(order_id, start, kb.ORDER_ITEMS_LIST_SIZE)

    text = f'Заказ <b>{order_id}</b>\n\n' if is_history else f'Для отмены заказа <b>{order_id}</b> нажмите на кнопку\n\n'

    for product in order_items:
        articul = product["id"]
        name = product["name"]
        price = product["price"]
        quantity = product["quantity"]
        total_price = product["total_price"]
        text += f'Артикул: {articul}\nНаименование: {name}\nСтоимость: {price}\nКоличество: {quantity}\nОбщая стоимость: {total_price}\n\n'

    if is_history:
        await callback_query.message.answer(text, parse_mode=ParseMode.HTML)
    else:
        keyboard = kb.create_order_items_keyboard(order_id, start, kb.ORDER_ITEMS_LIST_SIZE, not is_history)
        markup = keyboard.as_markup()
        await callback_query.message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)

@router.callback_query(lambda c: c.data.startswith('order-cancel_'))
async def cancel_order(callback_query: types.CallbackQuery):
    _, order_id = callback_query.data.split('_')
    order_id = int(order_id)

    await order.cancel_order(order_id)

    await callback_query.message.edit_text(f'Заказ {order_id} был отменен', parse_mode=ParseMode.HTML)

    


@router.message(F.text == 'История заказов')
async def products_keyboard_command(message: types.Message):
    telegram_id = message.from_user.id

    orders = await order.get_user_orders(telegram_id, False, 1, kb.ORDERS_LIST_SIZE)
    orders_count = (await order.get_orders_count(telegram_id, False))['count']

    if int(orders_count) == 0:
        text = 'У Вас нет заказов в истории'
        await message.answer(text)
        return
    
    text = 'Выберите интересующий Вас заказ\n\n'

    counter = 1
    for item in orders:
        pickup_point_address = item["pickup_point_address"]
        
        id = item["order_id"]
        
        try:
            status = item["status"]
            status = statuses[status]
        except:
            pass
        
        order_timestamp = item["order_timestamp"]
        formatted_dt = order_timestamp.strftime("%H:%M %d.%m.%Y")

        total_price = item["total_price"]
        total_count = int(item["total_count"])
        text += f'Заказ №{counter} от {formatted_dt}\nИдентификатор: <b>{id}</b>\nСтатус: {status}\nТоваров: {total_count} на {total_price}руб.\nПункт выдачи: {pickup_point_address}\n\n' 
        counter += 1

    keyboard = kb.create_orders_keyboard(orders, 1, orders_count, False)
    markup = keyboard.as_markup()

    await message.answer(text, reply_markup=markup)