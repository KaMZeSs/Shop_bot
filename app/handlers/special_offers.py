from aiogram.enums.parse_mode import ParseMode
from aiogram import F, types


from app.handlers.products import format_price, format_product_info
from app.handlers.router import router
import app.database.categories_repository as cat
import app.database.products_repository as prod
import app.database.cart_repository as cart
import app.keyboards as kb

from aiogram.types import BufferedInputFile
from aiogram.utils.media_group import MediaGroupBuilder


@router.message(F.text == 'Скидки')
async def special_offers_command(message: types.Message):
    categories = await cat.get_categories_with_spec_offers(1, kb.CATEGORIES_LIST_SIZE)
    categories_count = (await cat.get_categories_with_spec_offers_count())['count']

    text = "Выберите категорию:\n\n"
    
    keyboard = kb.create_categories_keyboard(categories, 1, categories_count, '-so_')

    markup = keyboard.as_markup()

    await message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)

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
        articul = product["id"]
        name = product["name"]
        price = product["price"]
        new_price = product["new_price"]
        discount = product["discount"]
        price_text = format_price(price, new_price, discount)
        product_text = f"{counter}. [{articul}] {name} - {price_text}\n\n"
        text += product_text

    keyboard = kb.create_products_keyboard(products, category_id, start, categories_count, '-so')
    markup = keyboard.as_markup()

    await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback_query.answer()
    
@router.callback_query(lambda c: c.data.startswith('product-so_'))
async def view_product_info(callback_query: types.CallbackQuery):
    _, product_id, prev_start, category_id = callback_query.data.split('_')
    product_id = int(product_id)
    prev_start = int(prev_start)
    category_id = int(category_id)
    
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
                
                keyboard = kb.create_product_info_keyboard(product_info['id'], category_id, prev_start, vs.message_id, '-so')
                markup = keyboard.as_markup()
                await callback_query.message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)
                await callback_query.bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
            else:
                keyboard = kb.create_product_info_keyboard(product_info['id'], category_id, prev_start, None, '-so')
                markup = keyboard.as_markup()
                await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
        except:
            keyboard = kb.create_product_info_keyboard(product_info['id'], category_id, prev_start, None, '-so')
            markup = keyboard.as_markup()
            await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
            
    except:
        await callback_query.message.answer("Данные о товаре не найдены", parse_mode=ParseMode.HTML)
        raise
    finally:
        await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith('product-back-so_'))
async def products_back(callback_query: types.CallbackQuery):
    _, category_id, start, photo_msg_id = callback_query.data.split('_')
    category_id = int(category_id)
    start = int(start)
    if photo_msg_id is not None:
        photo_msg_id = int(photo_msg_id)

    products = await prod.get_products_with_special_offers_small(category_id, start, kb.PRODUCTS_LIST_SIZE)
    products_count = (await prod.get_products_with_special_offers_count(category_id))['count']

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

    keyboard = kb.create_products_keyboard(products, category_id, start, products_count, '-so')
    markup = keyboard.as_markup()
    
    # if photo_msg_id is not None:
    #     await callback_query.bot.delete_message(callback_query.message.chat.id, photo_msg_id)

    await callback_query.message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback_query.answer()

