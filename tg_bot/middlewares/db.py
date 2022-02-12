from aiogram import Bot
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from tg_bot.utils.db_commands import DB


class DBMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    async def pre_process(self, obj, data, *args):
        db = obj.bot.get('db')
        user = await db.get_user(obj.from_user.id)
        if not user:
            user = await db.add_user(obj.from_user.id, obj.from_user.username)
        data['user'] = user
