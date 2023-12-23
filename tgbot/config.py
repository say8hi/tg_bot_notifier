from dataclasses import dataclass
from typing import Optional

from environs import Env


@dataclass
class TgBot:
    """
    Creates the TgBot object from environment variables.
    """

    token: str
    admin_ids: list[int]
    use_redis: bool

    @staticmethod
    def from_env(env: Env):
        token = env.str("BOT_TOKEN")
        admin_ids = list(map(int, env.list("ADMINS")))
        use_redis = env.bool("USE_REDIS")
        return TgBot(token=token, admin_ids=admin_ids, use_redis=use_redis)


@dataclass
class Miscellaneous:
    other_params: str = None


@dataclass
class Postgres:
    db_name: str
    db_user: str
    db_pass: str
    db_host: str

    @staticmethod
    def from_env(env: Env):
        db_name = env.str("POSTGRES_DB")
        db_user = env.str("POSTGRES_USER")
        db_pass = env.str("POSTGRES_PASSWORD")
        db_host = env.str("POSTGRES_HOST")
        return Postgres(db_name=db_name,
                        db_user=db_user,
                        db_pass=db_pass,
                        db_host=db_host)


@dataclass
class Redis:

    redis_pass: Optional[str]
    redis_port: Optional[int]
    redis_host: Optional[str]

    def dsn(self) -> str:
        if self.redis_pass:
            return f"redis://:{self.redis_pass}@{self.redis_host}:{self.redis_port}/0"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def from_env(env: Env):
        redis_pass = env.str("REDIS_PASSWORD")
        redis_port = env.int("REDIS_PORT")
        redis_host = env.str("REDIS_HOST")

        return Redis(
            redis_pass=redis_pass, redis_port=redis_port, redis_host=redis_host
        )


@dataclass
class Config:
    tg_bot: TgBot
    misc: Miscellaneous
    postgres: Postgres
    redis: Redis


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot.from_env(env),
        misc=Miscellaneous(),
        postgres=Postgres.from_env(env),
        redis=Redis.from_env(env),
    )
