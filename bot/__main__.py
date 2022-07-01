import asyncio
import datetime
import os
import logging

import toml
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application

from common.settings import Settings, make_settings
from common.session import make_session, get_db
from bot.handlers import all_handlers

settings = make_settings(os.environ.get("BOT_CONFIG"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

session = make_session(settings.db)

app = Application.builder().token(settings.bot.token).build()
app.add_handlers(all_handlers)

app.run_polling()