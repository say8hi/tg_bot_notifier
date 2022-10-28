import datetime

import asyncpg
from asyncpg import Pool

from tg_bot.config import Config


async def create_db_pool(config: Config) -> asyncpg.Pool:
    return await asyncpg.create_pool(config.db.db_uri)


class DB:

    def __init__(self, pool: Pool):
        self.pool = pool

    # ===========================USERS===========================
    async def add_user(self, user_id: int, username: str, lang: str = "en"):
        if not await self.get_user(user_id):
            await self.pool.execute("INSERT INTO users (id, username, lang) VALUES ($1, $2, $3)",
                                    user_id, username, lang)
            return await self.get_user(user_id)

    async def get_user(self, user_id=None, get_all: bool = False):
        if user_id and not get_all:
            return await self.pool.fetchrow("SELECT * FROM users WHERE id=$1", user_id)
        return await self.pool.fetch("SELECT * FROM users")

    async def update_user(self, user_id: int, **kwargs):
        params = self._convert_dict_to_params(kwargs)
        await self.pool.execute(f"UPDATE users SET {','.join(params)} WHERE id=$1", user_id)

    async def del_user(self, user_id: int):
        await self.pool.execute(f"DELETE FROM users WHERE id=$1", user_id)

    # ===========================NOTIFICATIONS===========================
    async def add_notification(self, user_id: int, desc: str, date_complete: str, title: str):
        return await self.pool.fetchrow(
            'INSERT INTO notifications (user_id, "desc", date_set, date_complete, title) VALUES ($1, $2, $3, $4, $5)'
            ' returning *',
            user_id, desc, datetime.datetime.now().strftime("%d.%m.%Y"), date_complete, title)

    async def update_notification(self, notification_id: int, **kwargs):
        params = self._convert_dict_to_params(kwargs)
        await self.pool.execute(f"UPDATE notifications SET {','.join(params)} WHERE id=$1", notification_id)

    async def get_notification(self, notification_id: int = None, get_all: bool = False):
        if not get_all:
            return await self.pool.fetchrow("SELECT * FROM notifications WHERE id=$1", notification_id)
        else:
            if notification_id:
                return await self.pool.fetch("SELECT * FROM notifications WHERE user_id=$1", notification_id)
            return await self.pool.fetch("SELECT * FROM notifications")

    async def del_notification(self, notification_id):
        await self.pool.execute("DELETE FROM notifications WHERE id=$1", notification_id)

    # ===========================NOTIFICATIONS===========================
    async def add_time_zone(self, time_zone: str):
        await self.pool.execute('INSERT INTO time_zones (time_zone) VALUES ($1)', time_zone)

    async def get_all_time_zones(self):
        return await self.pool.fetch("SELECT * FROM time_zones")

    # MISC
    @staticmethod
    def _convert_dict_to_params(dictionary: dict):
        return [f"{key}='{value}'" for key, value in dictionary.items()]
