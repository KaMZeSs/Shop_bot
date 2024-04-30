from app.database.database import get_db_pool

async def get_categories(first, count):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            categories = await conn.fetch(
                "SELECT * FROM categories ORDER BY id OFFSET $1 ROWS FETCH NEXT $2 ROWS ONLY;", 
                first-1, count
            )
            return categories
        
async def get_categories_count():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            count = await conn.fetchrow(
                "SELECT count(*) FROM categories;"
            )
            return count
        
async def get_categories_with_spec_offers(first, count):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            categories = await conn.fetch(
                """
                SELECT DISTINCT category_id AS id, ca.name
                FROM products pr
                JOIN special_offers so ON pr.id = so.product_id
                JOIN categories ca ON pr.category_id = ca.id
                ORDER BY category_id
                OFFSET $1 ROWS FETCH NEXT $2 ROWS ONLY;
                """, first-1, count
            )
            return categories
        
async def get_categories_with_spec_offers_count():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            count = await conn.fetchrow(
                """SELECT count(DISTINCT category_id)
                FROM products pr
                JOIN special_offers so ON pr.id = so.product_id"""
            )
            return count