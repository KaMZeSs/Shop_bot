import textwrap
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


CATEGORIES_LIST_SIZE = 10

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Каталог'), KeyboardButton(text='Скидки')], 
                                     [KeyboardButton(text='Корзина'), KeyboardButton(text='История заказов')], 
                                     [KeyboardButton(text='Список пунктов выдачи')], 
                                     [KeyboardButton(text='О нас'), KeyboardButton(text='Уведомления')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню')

def create_categories_keyboard(categories, start, list_count, spec = '_'):
    builder = InlineKeyboardBuilder()

    for category in categories:
        builder.add(InlineKeyboardButton(
            text=f"{category['name']}",
            callback_data=f"products{spec}{category['id']}_1"
        ))

    builder.adjust(1)

    controls = []

    if start > 1:
        prev_start = start - CATEGORIES_LIST_SIZE
        if prev_start < 1:
            prev_start = 1

        controls.append(
            InlineKeyboardButton(text="Предыдущие", callback_data=f"categories{spec}{prev_start}")
        )
        
    end = start + CATEGORIES_LIST_SIZE - 1
    if end < list_count:
        next_start = start + CATEGORIES_LIST_SIZE
        controls.append(
            InlineKeyboardButton(text="Следующие", callback_data=f"categories{spec}{next_start}")
        )


    builder.row(*controls, width=2)

    return builder

PRODUCTS_LIST_SIZE = 9

def create_products_keyboard(products, category_id, start, list_count):
    builder = InlineKeyboardBuilder()

    counter = start
    for product in products:
        button_text = f'{counter}'

        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f"product_{product['id']}"
        ))
        counter += 1

    builder.adjust(3)

    controls = []

    if start > 1:
        prev_start = start - PRODUCTS_LIST_SIZE
        if prev_start < 1:
            prev_start = 1

        controls.append(
            InlineKeyboardButton(text="Предыдущие", callback_data=f"products_{category_id}_{prev_start}")
        )
        
    end = start + PRODUCTS_LIST_SIZE - 1
    if end < list_count:
        next_start = start + PRODUCTS_LIST_SIZE
        controls.append(
            InlineKeyboardButton(text="Следующие", callback_data=f"products_{category_id}_{next_start}")
        )


    builder.row(*controls, width=2)

    return builder

def create_product_info_keyboard(product_id):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
            text='Добавить в корзину',
            callback_data=f"add-to-cart_{product_id}"
        ))

    return builder

def create_notification_settings_keyboard(user_info):
    builder = InlineKeyboardBuilder()

    orders = user_info['is_subscribed_to_orders']
    orders_text = ('Выключить' if orders else 'Включить') + ' уведомления о заказах'
    orders_callback = f'notifications_orders_disable' if orders else 'notifications_orders_enable'

    builder.row(InlineKeyboardButton(
            text=orders_text,
            callback_data=orders_callback
        ))
    
    news = user_info['is_subscribed_to_news']
    news_text = ('Выключить' if news else 'Включить') + ' уведомления о новостях'
    news_callback = 'notifications_news_disable' if news else 'notifications_news_enable'

    builder.row(InlineKeyboardButton(
            text=news_text,
            callback_data=news_callback
        ))

    return builder

CART_LIST_SIZE = 3

def create_cart_keyboard(products, start, list_count):
    builder = InlineKeyboardBuilder()

    counter = start
    for product in products:
        button_text = f'{counter}'

        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f"cart_{product['product_id']}"
        ))
        counter += 1

    builder.adjust(3)

    controls = []

    if start > 1:
        prev_start = start - CART_LIST_SIZE
        if prev_start < 1:
            prev_start = 1

        controls.append(
            InlineKeyboardButton(text="Предыдущие", callback_data=f"cart-proudcts_{prev_start}")
        )
        
    end = start + CART_LIST_SIZE - 1
    if end < list_count:
        next_start = start + CART_LIST_SIZE
        controls.append(
            InlineKeyboardButton(text="Следующие", callback_data=f"cart-proudcts_{next_start}")
        )


    builder.row(*controls, width=2)

    builder.row(
        InlineKeyboardButton(text='Оформить заказ', callback_data="place-an-order")
    )

    return builder