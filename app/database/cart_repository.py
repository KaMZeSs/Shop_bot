from app.database.database import get_db_pool

async def add_product_to_cart(product_id, user_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            data = await conn.fetchrow(
                """
                SELECT * FROM cart_items WHERE user_id = $1 AND product_id = $2
                """, user_id, product_id
            )
            if not data:
                await conn.execute(
                    """
                    INSERT INTO cart_items (user_id, product_id, quantity)
                    VALUES ($1, $2, 1)
                    """, user_id, product_id
                )
            else:
                await conn.execute(
                    """
                    UPDATE cart_items
                    SET quantity = quantity + 1
                    WHERE user_id = $1 AND product_id = $2
                    """, user_id, product_id
                )

async def get_cart_len_telegram_id(user_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            products = await conn.fetchrow(
                """
                SELECT 
                    count(*)
                FROM cart_items ci
                JOIN users us ON ci.user_id = us.id
                WHERE us.telegram_id = $1
                """, user_id
            )
            return products


async def get_cart_by_telegram_id(user_id, first, count):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            products = await conn.fetch(
                """
                SELECT
                    pr.id,
                    ci.user_id,
                    ci.product_id, 
                    ci.quantity user_quantity,
                    pr.name,
                    pr.price,
                    so.discount,
					(pr.price - pr.price * so.discount / 100)::integer AS new_price,
                    pr.quantity shop_quantity
                FROM cart_items ci
                JOIN products pr ON ci.product_id = pr.id
                JOIN users us ON ci.user_id = us.id
                LEFT JOIN special_offers so ON pr.id = so.product_id
							                   AND LOCALTIMESTAMP BETWEEN so.start_datetime AND so.end_datetime
                WHERE us.telegram_id = $1
                ORDER BY user_id, product_id
                OFFSET $2 ROWS FETCH NEXT $3 ROWS ONLY
                """, user_id, first-1, count
            )
            return products
        
async def get_cart_product_info(telegram_id, product_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            product = await conn.fetchrow(
                """
                SELECT
                    pr.id,
                    ci.user_id,
                    ci.product_id, 
                    ci.quantity user_quantity,
                    pr.name,
                    pr.price,
                    so.discount,
					(pr.price - pr.price * so.discount / 100)::integer AS new_price,
                    pr.quantity shop_quantity
                FROM cart_items ci
                JOIN products pr ON ci.product_id = pr.id
                JOIN users us ON ci.user_id = us.id
                LEFT JOIN special_offers so ON pr.id = so.product_id
							                   AND LOCALTIMESTAMP BETWEEN so.start_datetime AND so.end_datetime
                WHERE us.telegram_id = $1 AND pr.id = $2 
                """, telegram_id, product_id
            )
            return product
        
async def get_cart_size(telegram_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            count = await conn.fetchrow(
                """
                SELECT count(*) 
                FROM cart_items ci
                JOIN users us ON ci.user_id = us.id
                WHERE us.telegram_id = $1;
                """, telegram_id
            )
            return count
        
async def increase_product_in_cart(telegram_id, product_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                UPDATE cart_items ci
                SET quantity = quantity + 1
                WHERE user_id = (
                    SELECT us.id
                    FROM users us
                    WHERE us.telegram_id = $1
                )
                AND product_id = $2;

                """, telegram_id, product_id
            )
            
async def decrease_product_in_cart(telegram_id, product_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                UPDATE cart_items ci
                SET quantity = quantity - 1
                WHERE user_id = (
                    SELECT us.id
                    FROM users us
                    WHERE us.telegram_id = $1
                )
                AND product_id = $2;
                """, telegram_id, product_id
            )
            
async def delete_product_from_cart(telegram_id, product_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                DELETE FROM cart_items ci
                WHERE user_id = (
                    SELECT us.id
                    FROM users us
                    WHERE us.telegram_id = $1
                )
                AND ci.product_id = $2;
                """, telegram_id, product_id
            )

async def get_shortage_by_telegram_id(telegram_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            products = await conn.fetch(
                """
                SELECT
                    pr.id,
                    ci.user_id,
                    ci.product_id, 
                    ci.quantity user_quantity,
                    pr.name,
                    pr.quantity shop_quantity
                FROM cart_items ci
                JOIN products pr ON ci.product_id = pr.id
                JOIN users us ON ci.user_id = us.id
                WHERE us.telegram_id = $1 AND ci.quantity > pr.quantity
                ORDER BY product_id
                """, telegram_id
            )
            return products