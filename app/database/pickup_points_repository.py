from app.database.database import get_db_pool

async def get_pickup_points(first, count):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            pickup_points = await conn.fetch(
                "SELECT * FROM pickup_points WHERE is_works = True AND is_receiving_orders = True ORDER BY id OFFSET $1 ROWS FETCH NEXT $2 ROWS ONLY;", 
                first-1, count
            )
            return pickup_points
        
async def get_pickup_points_count():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            count = await conn.fetchrow(
                "SELECT count(*) FROM pickup_points WHERE is_works = True AND is_receiving_orders = True;"
            )
            return count

async def get_point_info(id):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            pickup_point = await conn.fetchrow(
                "SELECT * FROM pickup_points WHERE id = $1;", 
                id
            )
            return pickup_point
        
async def get_all_pickup_points():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            pickup_points = await conn.fetch(
                "SELECT * FROM pickup_points WHERE is_works = True ORDER BY id;"
            )
            return pickup_points