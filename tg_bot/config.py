from dataclasses import dataclass

from environs import Env


@dataclass
class DBConfig:
    host: str
    user: str
    password: str
    db_name: str


@dataclass
class TgBot:
    token: str
    admins: list


@dataclass
class Config:
    tg_bot: TgBot
    db: DBConfig


def load_config():
    env = Env()
    env.read_env()

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admins=list(map(int, env.list("ADMINS")))
        ),
        db=DBConfig(
            host=env.str("HOST"),
            user=env.str("USER"),
            password=env.str("PASSWORD"),
            db_name=env.str("DB_NAME")
        )
    )
