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
                    so.discount,
					(p.price - p.price * so.discount / 100)::integer AS new_price
                FROM
                    products p
                LEFT JOIN
                    special_offers so ON p.id = so.product_id
                                    AND LOCALTIMESTAMP BETWEEN so.start_datetime AND so.end_datetime
                WHERE quantity != 0 AND category_id = $1
                ORDER BY COALESCE((p.price - p.price * so.discount / 100), p.price)
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
                    so.discount,
					(p.price - p.price * so.discount / 100)::integer AS new_price
                FROM
                    products p
                    LEFT JOIN
                        special_offers so ON p.id = so.product_id
                                            AND LOCALTIMESTAMP BETWEEN so.start_datetime AND so.end_datetime
                WHERE so.discount IS NOT NULL AND quantity != 0 AND category_id = $1
                ORDER BY COALESCE((p.price - p.price * so.discount / 100), p.price)
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
                    p.quantity,
                    p.price,
                    so.discount,
					(p.price - p.price * so.discount / 100)::integer AS new_price
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
                WHERE discount IS NOT NULL AND quantity != 0 AND category_id = $1
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
        
def replace_spaces_with_text(input_string, text):
    # Удаляем повторяющиеся пробелы
    output_string = ' '.join(input_string.split())
    
    # Заменяем пробелы на ' & '
    output_string = output_string.replace(' ', text)
    
    return output_string


async def search_products_small(text, first, count):
    text = replace_spaces_with_text(text, ' | ')
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            # products = await conn.fetch(
            #     """
            #     SELECT
            #         p.id,
            #         p.name,
            #         p.price,
            #         so.discount,
			# 		(p.price - p.price * so.discount / 100)::integer AS new_price
            #     FROM
            #         products p
            #     LEFT JOIN
            #         special_offers so ON p.id = so.product_id
            #                         AND LOCALTIMESTAMP BETWEEN so.start_datetime AND so.end_datetime
            #     WHERE quantity != 0 AND to_tsvector(name) @@ to_tsquery($1)
            #     ORDER BY ts_rank(to_tsvector(name), to_tsquery($1)) DESC
            #     OFFSET $2 ROWS FETCH NEXT $3 ROWS ONLY
            #     """, text, first-1, count
            # )
            
            # products = await conn.fetch(
            #     """
            #     SELECT
            #         p.id,
            #         p.name,
            #         p.price,
            #         so.discount,
            #         (p.price - p.price * so.discount / 100)::integer AS new_price
            #     FROM
            #         products p
            #     LEFT JOIN
            #         special_offers so ON p.id = so.product_id
            #                         AND LOCALTIMESTAMP BETWEEN so.start_datetime AND so.end_datetime
            #     WHERE 
            #         quantity != 0 
            #         AND concat_ws(' ', p.name) ILIKE '%' || $1 || '%'
            #     ORDER BY 
            #         ts_rank(to_tsvector(concat_ws(' ', p.name)), to_tsquery($1)) DESC
            #     OFFSET $2 ROWS FETCH NEXT $3 ROWS ONLY
            #     """, text, first-1, count
            # )
            
            products = await conn.fetch(
                """
                SELECT
                    p.id,
                    p.name,
                    p.price,
                    so.discount,
                    (p.price - p.price * so.discount / 100)::integer AS new_price,
                    ts_rank_cd(to_tsvector(p.name), plainto_tsquery($1)) AS rank
                FROM
                    products p
                LEFT JOIN
                    special_offers so ON p.id = so.product_id
                                    AND LOCALTIMESTAMP BETWEEN so.start_datetime AND so.end_datetime
                WHERE 
                    (
                        p.id::text = $1 OR
                        p.id::text ILIKE '%' || $1 || '%' OR
                        p.name ILIKE '%' || $1 || '%' OR
                        to_tsvector(p.name) @@ plainto_tsquery($1)
                    )
                    AND quantity != 0 
                ORDER BY 
                    CASE WHEN p.id::text = $1 THEN 1 ELSE 2 END, rank DESC
                OFFSET $2 ROWS FETCH NEXT $3 ROWS ONLY;
                """, text, first-1, count
            )
            
            return products