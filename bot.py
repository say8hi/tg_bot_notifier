import asyncio
import logging

import betterlogging as bl
import pytz
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import load_config, Config
from tgbot.handlers import routers_list
from tgbot.middlewares.global_instances import GlobalInstances
from tgbot.middlewares.database import DatabaseMiddleware
from tgbot.services import broadcaster
from tgbot.services.db_commands import DatabaseCommands
from tgbot.services.notifications import restore_notifications


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Бот запущен")


def register_global_middlewares(dp: Dispatcher, config: Config, scheduler: AsyncIOScheduler):
    middleware_types = [
        GlobalInstances(config, scheduler),
        DatabaseMiddleware(),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging():
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage(config):
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def main():
    setup_logging()

    config = load_config(".env")
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(storage=get_storage(config))
    scheduler = AsyncIOScheduler(timezone=str(pytz.timezone("Asia/Almaty")))

    dp.include_routers(*routers_list)

    register_global_middlewares(dp, config, scheduler)

    await on_startup(bot, config.tg_bot.admin_ids)

    try:
        logging.info('Trying to connect to PostgresSQL Database')
        await DatabaseCommands.connect(config.postgres.db_user, config.postgres.db_pass,
                                       config.postgres.db_name, config.postgres.db_host)
        logging.info('Successfully connected to PostgresSQL Database')
        await DatabaseCommands.create_tables()
        # await DatabaseCommands.make_migrations()
        await restore_notifications(bot, scheduler)
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()
        await DatabaseCommands.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot is stopped")
