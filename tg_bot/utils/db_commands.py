import asyncpg
from asyncpg import Pool

from tg_bot.config import Config


async def create_db_pool(config: Config):
    return asyncpg.create_pool(host=config.db.host, port=5432,
                               user=config.db.user, password=config.db.password,
                               database=config.db.db_name)


async def add_user(pool: Pool, user_id, username):
    await pool.execute("INSERT INTO users (id, username) VALUES ($1, $2)", user_id, username)
