from app.database.database import get_db_pool

async def get_pickup_points(first, count):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            pickup_points = await conn.fetch(
                "SELECT * FROM pickup_points ORDER BY id OFFSET $1 ROWS FETCH NEXT $2 ROWS ONLY;", 
                first-1, count
            )
            return pickup_points
        
async def get_pickup_points_count():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            count = await conn.fetchrow(
                "SELECT count(*) FROM pickup_points;"
            )
            return count