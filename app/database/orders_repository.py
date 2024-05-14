from asyncpg.exceptions import PostgresError
from app.database.database import get_db_pool
from app.database.users_repository import get_user_id_by_telegram_id
       
async def get_orders_count(telegram_id, is_current: bool):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            count = await conn.fetchrow(
                f"""
                SELECT count(*)
                FROM orders o
                JOIN users us ON o.user_id = us.id
                WHERE us.telegram_id = $1 AND o.status {'NOT' if is_current else ''} IN ('completed', 'canceled')
                """, telegram_id
            )
            return count
        
async def create_new_order(telegram_id, pickup_point_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                order_id = await conn.fetchrow(
                    """
                    SELECT create_order($1, $2)
                    """, telegram_id, pickup_point_id
                )
                return order_id
            except PostgresError as e:
                raise

async def cancel_order(order_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                await conn.execute(
                    """
                    UPDATE orders SET status = 'canceled' WHERE id = $1
                    """, order_id
                )
                return order_id
            except PostgresError as e:
                raise

async def get_user_orders(telegram_id, is_current: bool, first, count):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            orders = await conn.fetch(
                f"""
                SELECT
                    o.id AS order_id,
                    o.user_id,
                    o.pickup_point_id,
                    pp.address AS pickup_point_address,
                    o.status,
                    o.order_timestamp,
                    o_sum.total_price,
                    o_sum.total_count
                FROM orders o
                JOIN pickup_points pp ON o.pickup_point_id = pp.id
                JOIN users us ON o.user_id = us.id
                JOIN (
                    SELECT 
                        order_id,
                        count(*) as total_count,
                        sum(price*quantity) as total_price
                    FROM order_items
                    GROUP BY order_id
                ) o_sum ON o.id = o_sum.order_id
                WHERE us.telegram_id = $1 AND o.status {'NOT' if is_current else ''} IN ('completed', 'canceled')
                ORDER BY o.order_timestamp DESC
                OFFSET $2 ROWS FETCH NEXT $3 ROWS ONLY;
                """, telegram_id, first-1, count
            )
            return orders
        
async def get_order_items(order_id, first, count):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            order_items = await conn.fetch(
                f"""
                SELECT 
                    pr.id,
                    pr.name,
                    oi.quantity,
                    oi.price,
                    oi.price * oi.quantity AS total_price
                FROM order_items oi
                JOIN products pr ON pr.id = oi.product_id
                WHERE oi.order_id = $1
                OFFSET $2 ROWS FETCH NEXT $3 ROWS ONLY;
                """, order_id, first-1, count
            )
            return order_items
        
async def get_order_items_count(order_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            order_items = await conn.fetchrow(
                f"""
                SELECT 
                    count(*)
                FROM order_items oi
                WHERE oi.order_id = $1
                """, order_id
            )
            return order_items
        
async def get_is_order_history(order_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            order_items = await conn.fetchrow(
                f"""
                SELECT 
                    status IN ('canceled', 'completed') as is_history
                FROM orders 
                WHERE id = $1
                """, order_id
            )
            return order_items