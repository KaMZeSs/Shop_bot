from app.database.database import get_db_pool

async def get_or_create_user(telegram_id, name):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id = $1", telegram_id
            )
            if not user:
                await conn.execute(
                    "INSERT INTO users (telegram_id, name) VALUES ($1, $2)",
                    telegram_id, name
                )
            else:
                await conn.execute(
                    "UPDATE users SET name = $2 WHERE telegram_id = $1",
                    telegram_id, name
                )

async def get_user_id_by_telegram_id(telegram_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            user_id = await conn.fetchrow(
                "SELECT id FROM users WHERE telegram_id = $1", telegram_id
            )

            return user_id
        
async def get_user_notification_settings(telegram_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            user_info = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id = $1", telegram_id
            )

            return user_info
        
async def set_user_notification_setting(telegram_id, new_orders = None, new_news = None):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            if new_orders is not None:
                await conn.execute(
                    "UPDATE users SET is_subscribed_to_orders = $2 WHERE telegram_id = $1",
                    telegram_id, new_orders
                )
            if new_news is not None:
                await conn.execute(
                    "UPDATE users SET is_subscribed_to_news = $2 WHERE telegram_id = $1",
                    telegram_id, new_news
                )
