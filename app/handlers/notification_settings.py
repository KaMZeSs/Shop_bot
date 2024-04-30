from aiogram.enums.parse_mode import ParseMode
from aiogram import F, types

from app.handlers.router import router
import app.keyboards as kb

from app.database.users_repository import get_user_notification_settings, set_user_notification_setting

@router.message(F.text == 'Уведомления')
async def notification_settings_command(message: types.Message):

    telegram_id = message.from_user.id
    user_info = await get_user_notification_settings(telegram_id)
    
    orders = user_info['is_subscribed_to_orders']
    news = user_info['is_subscribed_to_news']

    orders_text = 'Включены' if orders else 'Выключены'
    news_text = 'Включены' if news else 'Выключены'

    text = f'Текущие настройки:\n\nУведомления о заказах: <b>{orders_text}</b>\nУведомления о новостях: <b>{news_text}</b>'
    
    keyboard = kb.create_notification_settings_keyboard(user_info)

    markup = keyboard.as_markup()

    await message.reply(text, reply_markup=markup, parse_mode=ParseMode.HTML)

@router.callback_query(lambda c: c.data.startswith('notifications_'))
async def process_notifications_settings_change(callback_query: types.CallbackQuery):
    _, setting, new_value = callback_query.data.split('_')

    new_value_bool = True if new_value == 'enable' else False

    telegram_id = callback_query.from_user.id

    if setting == 'orders':
        await set_user_notification_setting(telegram_id, new_orders=new_value_bool)
    elif setting == 'news':
        await set_user_notification_setting(telegram_id, new_news=new_value_bool)

    user_info = await get_user_notification_settings(telegram_id)
    
    orders = user_info['is_subscribed_to_orders']
    news = user_info['is_subscribed_to_news']

    orders_text = 'Включены' if orders else 'Выключены'
    news_text = 'Включены' if news else 'Выключены'

    text = f'Текущие настройки:\n\nУведомления о заказах: <b>{orders_text}</b>\nУведомления о новостях: <b>{news_text}</b>'
    
    keyboard = kb.create_notification_settings_keyboard(user_info)
    markup = keyboard.as_markup()

    await callback_query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await callback_query.answer()