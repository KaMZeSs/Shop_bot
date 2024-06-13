from aiogram import Bot
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import BufferedInputFile

import app.database.order_notifications_repository as on

statuses = {
    'created' : 'Создан',
    'submitted' : 'Подтверждён',
    'ready' : 'Готов к получению',
    'completed' : 'Выдан',
    'canceled' : 'Отменён'
}

async def send_order_notifications(bot: Bot):
    try:
        notifications = await on.get_new_notifications_info()
    except:
        return

    for item in notifications:
        try:
            id = item['id']
            order_id = item['order_id']
            message = item['message']
            telegram_id = item['telegram_id']
            
            if message is not None:
                # Важное сообщение
                # Отправляется в любом случае
                text = f'Важная информация о заказе №<b>{order_id}</b>\n\n{message}'
                await bot.send_message(chat_id=telegram_id, text=text)
            else:
                # Уведомление о состоянии заказа
                is_accepts_notifications = item['is_subscribed_to_orders']
                if is_accepts_notifications:
                    # Пользователь согласен на отправку уведомлений
                    status = item['status']
                    try:
                        status = statuses[status]
                    except:
                        pass
                    
                    text = f'Заказ №<b>{order_id}</b>: <b>{status}</b>'
                    await bot.send_message(chat_id=telegram_id, text=text)
                    
            await on.delete_old_notification(id)
        except:
            pass
        
        
        
                
                
                
     
