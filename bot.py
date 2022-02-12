import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tg_bot.config import load_config
from tg_bot.filters.role import RoleFilter, AdminFilter
from tg_bot.handlers.errors import register_errors
from tg_bot.handlers.general import register_user
from tg_bot.middlewares.db import DBMiddleware
from tg_bot.middlewares.role import RoleMiddleware
from tg_bot.utils.db_commands import create_db_pool, DB

logger = logging.getLogger(__name__)


def register_all_handlers(dp: Dispatcher):
    register_errors(dp)
    register_user(dp)


async def main():
    logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.INFO)
    logger.info("Starting bot")
    config = load_config()

    storage = MemoryStorage()

    pool = await create_db_pool(config)

    scheduler = AsyncIOScheduler()

    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(RoleMiddleware(config.tg_bot.admins))
    dp.middleware.setup(DBMiddleware())
    dp.filters_factory.bind(RoleFilter)
    dp.filters_factory.bind(AdminFilter)

    bot['scheduler'] = scheduler
    bot['config'] = config
    bot['db'] = DB(pool)

    register_all_handlers(dp)

    # start
    try:
        scheduler.start()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped!")
