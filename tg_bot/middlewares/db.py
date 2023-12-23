import time

from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from tg_bot.models.database import Database


class DBMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    async def pre_process(self, obj, data, *args):
        user = await Database.users.get(obj.from_user.id)
        if not user:
            user = await Database.users.add(id=obj.from_user.id, username=obj.from_user.username,
                                            registered=time.time())
        data['user'] = user
