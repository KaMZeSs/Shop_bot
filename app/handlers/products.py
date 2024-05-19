from aiogram.enums.parse_mode import ParseMode
from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder

from app.handlers.router import router
import app.database.products_repository as prod
import app.database.cart_repository as cart
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
    quantity = product_info['quantity']
    description = product_info['description']

    text = f'<b>{name}</b>\n<i>Артикул:</i> {articul}\n<i>Цена:</i> {price_text}\n<i>Доступно на складе:</i> {quantity}<i>\nОписание:</i>\n{description}'

    return text

@router.callback_query(lambda c: c.data.startswith('product_'))
async def view_product_info(callback_query: types.CallbackQuery):
    _, product_id, prev_start, category_id = callback_query.data.split('_')
    product_id = int(product_id)
    prev_start = int(prev_start)
    category_id = int(category_id) if category_id != 'None' else None
    
    try:
        product_info = await prod.get_product_info(product_id)
        product_images = await prod.get_product_images(product_id)
    
        text = format_product_info(product_info)
        
        product_in_cart = await cart.get_cart_product_info_small(callback_query.from_user.id, product_id)
        if product_in_cart is not None:
            text += f'\n\nТоваров в корзине: {product_in_cart['quantity']}'
        try:
            if len(product_images) != 0:
                media = MediaGroupBuilder()
                for image in product_images:
                    try:
                        image_bytearray = image['image']
                        image_bytes = bytes(image_bytearray)
                        photo = BufferedInputFile(image_bytes, filename='image.jpg')
                        media.add_photo(photo)
                    except:
                        pass

                vs = await callback_query.message.answer_media_group(media=media.build())
                vs = vs[0]
                
                keyboard = kb.create_product_info_keyboard(product_info['id'], category_id, prev_start, vs.message_id)
                markup = keyboard.as_markup()
                await callback_query.message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)
                await callback_query.bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
            else:
                keyboard = kb.create_product_info_keyboard(product_info['id'], category_id, prev_start, None)
                markup = keyboard.as_markup()
                await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
        except:
            keyboard = kb.create_product_info_keyboard(product_info['id'], category_id, prev_start, None)
            markup = keyboard.as_markup()
            await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    except:
        await callback_query.message.answer("Данные о товаре не найдены", parse_mode=ParseMode.HTML)
        raise
    finally:
        await callback_query.answer()
        
@router.callback_query(lambda c: c.data.startswith('product-back_'))
async def process_products_pagination(callback_query: types.CallbackQuery):
    _, category_id, start, photo_msg_id = callback_query.data.split('_')
    category_id = int(category_id)
    start = int(start)
    if photo_msg_id is not None:
        photo_msg_id = int(photo_msg_id)

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
    
    # if photo_msg_id is not None:
    #     await callback_query.bot.delete_message(callback_query.message.chat.id, photo_msg_id)

    await callback_query.message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback_query.answer()
