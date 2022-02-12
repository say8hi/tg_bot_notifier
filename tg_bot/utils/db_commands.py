import datetime

import asyncpg
from asyncpg import Pool

from tg_bot.config import Config


async def create_db_pool(config: Config):
    return await asyncpg.create_pool(config.db.db_uri)


class DB:

    def __init__(self, pool: Pool):
        self.pool = pool

    # ===========================USERS===========================
    async def add_user(self, user_id: int, username: str, lang: str = "en"):
        if not self.get_user(user_id):
            await self.pool.execute("INSERT INTO users (id, username, lang) VALUES ($1, $2, $3)",
                                    user_id, username, lang)
            return self.get_user(user_id)

    async def get_user(self, user_id):
        sql = "SELECT * FROM users  WHERE id=$1"
        return await self.pool.fetchrow(sql, user_id)

    async def update_user(self, user_id: int, **kwargs):
        params = self._convert_dict_to_params(kwargs)
        await self.pool.execute(f"UPDATE users SET {','.join(params)} WHERE id=$1", user_id)

    async def del_user(self, user_id: int):
        await self.pool.execute(f"DELETE FROM users WHERE id=$1", user_id)

    # ===========================NOTIFICATIONS===========================
    async def add_notification(self, user_id: int, desc: str, date_complete: str, title: str):
        await self.pool.execute(
            'INSERT INTO notifications (user_id, "desc", date_set) VALUES ($1, $2, $3)',
            user_id, desc, datetime.datetime.now().strftime("%Y.%m.%d"))

    async def update_notification(self, notification_id: int, **kwargs):
        params = self._convert_dict_to_params(kwargs)
        await self.pool.execute(f"UPDATE notifications SET {','.join(params)} WHERE id=$1", notification_id)

    async def get_notification(self, notification_id: int, get_all: bool = False):
        if not get_all:
            return await self.pool.fetchrow("SELECT * FROM notifications WHERE id=$1", notification_id)
        else:
            return await self.pool.fetch("SELECT * FROM notifications WHERE user_id=$1", notification_id)

    async def del_notification(self, notification_id):
        await self.pool.execute("DELETE FROM notifications WHERE id=$1", notification_id)

    # MISC
    @staticmethod
    def _convert_dict_to_params(dictionary: dict):
        return [f"{key}='{value}'" for key, value in dictionary.items()]
