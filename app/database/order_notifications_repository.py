from app.database.database import get_db_pool

async def get_new_notifications_info():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            to_notify = await conn.fetch(
                """
                SELECT 
                    nf.id,
                    nf.order_id,
                    nf.notified_at,
                    od.status,
                    us.telegram_id,
                    us.name,
                    us.is_subscribed_to_orders
                FROM order_notifications nf
                JOIN orders od ON od.id = nf.order_id
                JOIN users us ON us.id = od.user_id
                WHERE notified_at IS NULL
                """
            )
            return to_notify