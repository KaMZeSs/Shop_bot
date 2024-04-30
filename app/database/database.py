from asyncpg import create_pool, Pool
from dotenv import dotenv_values

CONN_DATA = dotenv_values()

# Глобальная переменная для хранения пула соединений
db_pool = None

# Функция для создания или получения существующего пула соединений
async def get_db_pool() -> Pool:
    global db_pool
    if not db_pool:
        db_pool = await create_pool(
            host=CONN_DATA['host'],
            user=CONN_DATA['user'],
            password=CONN_DATA['password'],
            database=CONN_DATA['database']
        )
    return db_pool

# Функция для закрытия пула соединений
async def close_db_pool():
    global db_pool
    if db_pool:
        await db_pool.close()
        db_pool = None