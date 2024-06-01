from aiogram import Bot
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import BufferedInputFile

import app.database.news_repository as ns

async def send_news(bot: Bot):
    news = await ns.get_new_news()
    users = await ns.get_user_news_subscribed()
    user_ids = [x['telegram_id'] for x in users]

    for item in news:
        images = await ns.get_news_images(item['id'])
        title = item['title']
        content = item['content']
        
        text = f'<b>{title}</b>\n\n{content}'
        
        await ns.set_news_notified(int(item['id']))
        
        if len(images) != 0:
            media = MediaGroupBuilder()
            if len(images) != 0:
                for image in images:
                    try:
                        image_bytearray = image['image']
                        image_bytes = bytes(image_bytearray)
                        photo = BufferedInputFile(image_bytes, filename='image.jpg')
                        media.add_photo(photo)
                    except:
                        pass
            media.caption = text
            
            for id in user_ids:
                await bot.send_media_group(chat_id=id, media=media)
        else:
            for id in user_ids:
                await bot.send_message(chat_id=id, text=text)
                
                
                
     
