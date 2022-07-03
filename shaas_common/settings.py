from pathlib import Path
from typing import Optional

import toml
from pydantic import BaseSettings


class DatabaseSettings(BaseSettings):
    dsn: str = ""


class BotSettings(BaseSettings):
    token: str
    base_url: str


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()
    bot: Optional[BotSettings]


settings = Settings()


def make_settings(path = "config.toml"):
    if not path:
        raise Exception("None instead of config")
    if not Path(path).exists():
        raise Exception(f"No config found")

    config = toml.load(path)

    global settings
    settings = Settings(**config)

    return settings


def get_settings():
    return settings