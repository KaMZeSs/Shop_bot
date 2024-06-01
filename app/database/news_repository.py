from app.database.database import get_db_pool
from asyncpg import PostgresError
        
async def get_user_news_subscribed():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            user_info = await conn.fetch(
                "SELECT telegram_id FROM users WHERE is_subscribed_to_news = True"
            )

            return user_info
        
async def get_new_news():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            news = await conn.fetch(
                "SELECT * FROM news WHERE notified = False"
            )

            return news
        
async def get_news_images(id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            user_info = await conn.fetch(
                "SELECT image FROM news_images WHERE news_id = $1", id
            )

            return user_info
        
async def set_news_notified(id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "UPDATE news SET notified = True WHERE id = $1", id
            )
