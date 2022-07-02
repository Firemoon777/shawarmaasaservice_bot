import os
import logging

from telegram.ext import Application

from common.settings import make_settings
from common.session import make_session
from bot.handlers import handlers, error_handlers

settings = make_settings(os.environ.get("BOT_CONFIG"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

session = make_session(settings.db)

app = Application.builder().token(settings.bot.token).build()
app.add_handlers(handlers)
for error_handler in error_handlers:
    app.add_error_handler(error_handler)

app.run_polling()