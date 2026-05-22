from dataclasses import dataclass
from environs import Env

@dataclass
class TgBot:
    token: str
    admin_ids: str
    ai_token: str
    money_token: int
    bot_username: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env("BOT_TOKEN"),
                               admin_ids=env("ADMIN_IDS"),
                               ai_token=env("AI_TOKEN"),
                               money_token=env("MONEY_TOKEN"),
                               bot_username=env("BOT_USERNAME")
))