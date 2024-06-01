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
                    nf.message,
                    od.status,
                    us.telegram_id,
                    us.is_subscribed_to_orders
                FROM order_notifications nf
                JOIN orders od ON od.id = nf.order_id
                JOIN users us ON us.id = od.user_id
                """
            )
            return to_notify
        
async def delete_old_notification(id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                DELETE
                FROM order_notifications
                WHERE id = $1
                """, id
            )