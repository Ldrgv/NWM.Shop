from dataclasses import dataclass
from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    name: str


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]


@dataclass
class Misc:
    payment_token: str
    module_chat: int


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Misc


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASSWORD'),
            user=env.str('DB_USER'),
            name=env.str('DB_NAME')
        ),
        misc=Misc(
            payment_token=env.str('PAYMENT_TOKEN'),
            module_chat=env.int("MODULE_CHAT")
        )
    )
