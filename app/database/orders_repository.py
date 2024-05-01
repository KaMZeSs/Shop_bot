from app.database.database import get_db_pool

async def get_orders_info(telegram_id, first, count):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            orders = await conn.fetch(
                """
                SELECT 
                    o.id,
                    pp.address,
                    o.status,
                    o.order_timestamp
                FROM orders o
                JOIN users us ON o.user_id = us.id
                JOIN pickup_points pp ON o.pickup_point_id = pp.id
                WHERE us.telegram_id = $1
                OFFSET $2 ROWS FETCH NEXT $3 ROWS ONLY;
                """, telegram_id, first-1, count
            )
            return orders
        
async def get_orders_count(telegram_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            count = await conn.fetchrow(
                """
                SELECT count(*)
                FROM orders o
                JOIN users us ON o.user_id = us.id
                WHERE us.telegram_id = $1
                """, telegram_id
            )
            return count