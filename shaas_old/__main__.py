import datetime
import os
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application

from common.session import make_session
from shaas_old.handlers import all_handlers

TOKEN = os.environ["BOT_TOKEN"]


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


app = Application.builder().token(TOKEN).build()
app.add_handlers(all_handlers)
app.run_polling()