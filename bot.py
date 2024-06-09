import asyncio
import logging

from alembic import command
import betterlogging as bl
import pytz
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from tgbot.database.database import Base
from tgbot.database.orm import AsyncORM
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from tgbot.config import load_config, Config
from tgbot.handlers import routers_list
from tgbot.middlewares.global_instances import GlobalInstances
from tgbot.middlewares.database import DatabaseMiddleware
from tgbot.services import broadcaster
from tgbot.services.notifications import restore_notifications


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Бот запущен")


def register_global_middlewares(
    dp: Dispatcher, config: Config, scheduler: AsyncIOScheduler
):
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


async def setup_database(config: Config):
    logging.info("Trying to connect to PostgresSQL Database")
    while True:
        try:
            async_engine = create_async_engine(
                url=f"postgresql+asyncpg://{config.postgres.db_user}:{config.postgres.db_pass}"
                f"@{config.postgres.db_host}:5432/{config.postgres.db_name}",
                # echo=True,
            )
            async_session_factory = async_sessionmaker(async_engine)
            AsyncORM.set_session_factory(async_session_factory)
            AsyncORM.init_models()
            break
        except Exception:
            await asyncio.sleep(1)

    logging.info("Successfully connected to PostgresSQL Database")
    return async_engine


def get_storage(config):
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def run_migrations(engine: AsyncEngine):
    from alembic.config import Config

    logging.info("Database: Trying to migrate")
    alembic_cfg = Config("alembic.ini")
    async with engine.begin() as conn:
        await conn.run_sync(generate_migration, alembic_cfg)
        await conn.run_sync(run_upgrade, alembic_cfg)

    logging.info("Database: Successfully migrated")


def generate_migration(connection, cfg):
    cfg.attributes["connection"] = connection
    command.revision(cfg, autogenerate=True, message="Autogenerated migration")


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


async def main():
    config = load_config(".env")

    engine = await setup_database(config)

    await run_migrations(engine)
    setup_logging()
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(storage=get_storage(config))
    scheduler = AsyncIOScheduler(timezone=str(pytz.timezone("Asia/Almaty")))

    dp.include_routers(*routers_list)

    register_global_middlewares(dp, config, scheduler)

    await on_startup(bot, config.tg_bot.admin_ids)

    try:
        logging.info("Trying to connect to PostgresSQL Database")
        logging.info("Successfully connected to PostgresSQL Database")
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot is stopped")
