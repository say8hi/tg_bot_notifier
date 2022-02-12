from dataclasses import dataclass

from environs import Env


@dataclass
class DBConfig:
    db_uri: str


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
            db_uri=env.str("URI")
        )
    )
