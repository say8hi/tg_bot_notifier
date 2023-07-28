from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str
    admins: list


@dataclass
class Config:
    tg_bot: TgBot


def load_config():
    env = Env()
    env.read_env()

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admins=list(map(int, env.list("ADMINS")))
        )
    )
