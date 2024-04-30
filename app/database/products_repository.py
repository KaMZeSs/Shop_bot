from app.database.database import get_db_pool

async def get_products_small(category_id, first, count):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            products = await conn.fetch(
                """
                SELECT
                    p.id,
                    p.name,
                    p.price,
                    so.new_price
                FROM
                    products p
                LEFT JOIN
                    special_offers so ON p.id = so.product_id
                                    AND LOCALTIMESTAMP BETWEEN so.start_datetime AND so.end_datetime
                WHERE quantity != 0 AND category_id = $1
                ORDER BY COALESCE(so.new_price, p.price)
                OFFSET $2 ROWS FETCH NEXT $3 ROWS ONLY
                """, category_id, first-1, count
            )
            return products

async def get_products_with_special_offers_small(category_id, first, count):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            products = await conn.fetch(
                """                
                SELECT
                    p.id,
                    p.name,
                    p.price,
                    so.new_price
                FROM
                    products p
                    LEFT JOIN
                        special_offers so ON p.id = so.product_id
                                            AND LOCALTIMESTAMP BETWEEN so.start_datetime AND so.end_datetime
                WHERE new_price IS NOT NULL AND quantity != 0 AND category_id = $1
                ORDER BY COALESCE(so.new_price, p.price)
                OFFSET $2 ROWS FETCH NEXT $3 ROWS ONLY
                """, category_id, first-1, count
            )
            return products
        
async def get_product_info(product_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            info = await conn.fetchrow(
                """
                SELECT
                    p.id,
                    p.name,
                    p.description,
                    p.price,
                    so.new_price
                FROM
                    products p
                LEFT JOIN
                    special_offers so ON p.id = so.product_id
                                    AND LOCALTIMESTAMP BETWEEN so.start_datetime AND so.end_datetime
                WHERE p.id = $1;
                """, product_id
            )
            return info
        
async def get_products_count(category_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            count = await conn.fetchrow(
                "SELECT count(*) FROM products WHERE quantity != 0 AND category_id = $1;",
                category_id
            )
            return count
        
async def get_products_with_special_offers_count(category_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            count = await conn.fetchrow(
                """
                SELECT count(*)
                FROM
                    products p
                    LEFT JOIN
                        special_offers so ON p.id = so.product_id
                                             AND LOCALTIMESTAMP BETWEEN so.start_datetime AND so.end_datetime
                WHERE new_price IS NOT NULL AND quantity != 0 AND category_id = $1
                """, category_id
            )
            return count
        
        
async def get_product_image(product_id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            image_data = await conn.fetchrow(
                "SELECT image FROM product_images WHERE product_id = $1;", 
                product_id
            )
            return image_data

