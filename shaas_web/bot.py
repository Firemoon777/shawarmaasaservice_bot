from typing import Optional

from telegram._bot import BT
from telegram.ext import Application

app: Optional[Application] = None


def get_bot() -> BT:
    return app.bot


def make_bot(settings):
    global app
    app = Application.builder().token(settings.token).build()