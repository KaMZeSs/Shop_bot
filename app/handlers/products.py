from aiogram.enums.parse_mode import ParseMode
from aiogram import types

from app.handlers.router import router
import app.database.products_repository as prod
import app.keyboards as kb

from aiogram.types import BufferedInputFile


def format_price(price, new_price, discount):
    if new_price is None:
        return f"<b>{price} руб.</b>"
    else:
        return f"<b>{new_price} руб.</b> <s>{price} руб.</s> <b>-{discount}%</b>"

@router.callback_query(lambda c: c.data.startswith('products_'))
async def process_products_pagination(callback_query: types.CallbackQuery):
    _, category_id, start = callback_query.data.split('_')
    category_id = int(category_id)
    start = int(start)

    products = await prod.get_products_small(category_id, start, kb.PRODUCTS_LIST_SIZE)
    categories_count = (await prod.get_products_count(category_id))['count']

    text = "Выберите товар:\n\n"

    counter = start
    for product in products:
        articul = product["id"]
        name = product["name"]
        price = product["price"]
        discount = product["discount"]
        new_price = product["new_price"]
        price_text = format_price(price, new_price, discount)
        product_text = f"<i>{counter}.</i> [{articul}] {name} - {price_text}\n\n"
        text += product_text
        counter += 1

    keyboard = kb.create_products_keyboard(products, category_id, start, categories_count)
    markup = keyboard.as_markup()

    await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback_query.answer()

def format_product_info(product_info):
    articul = product_info['id']
    name = product_info['name']
    price = product_info['price']
    new_price = product_info['new_price']
    discount = product_info['discount']
    price_text = format_price(price, new_price, discount)
    description = product_info['description']

    text = f'<b>{name}</b>\n<i>Артикул:</i> {articul}\n<i>Цена:</i> {price_text}\n<i>Описание:</i>\n{description}'

    return text

@router.callback_query(lambda c: c.data.startswith('product_'))
async def view_product_info(callback_query: types.CallbackQuery):
    _, product_id = callback_query.data.split('_')
    product_id = int(product_id)

    try:
        product_info = await prod.get_product_info(product_id)
        product_image = await prod.get_product_image(product_id)

        text = format_product_info(product_info)

        keyboard = kb.create_product_info_keyboard(product_info['id'])
        markup = keyboard.as_markup()

        if product_image is not None:
            image_bytearray = product_image['image']
            # Преобразование bytearray в bytes
            image_bytes = bytes(image_bytearray)

            # Создание InputFile из файлоподобного объекта
            photo = BufferedInputFile(image_bytes, filename='image.jpg')

            await callback_query.message.reply_photo(photo)
        await callback_query.message.reply(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    except:
        await callback_query.message.reply("Данные о товаре не найдены", parse_mode=ParseMode.HTML)
    finally:
        await callback_query.answer()