import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, MessageHandler, filters

from shaas_common.security import get_hash
from shaas_common.storage import Storage


async def open_admin_menu(update: Update, context: CallbackContext):
    base_url = context.bot_data["base_url"]

    user_id = update.message.from_user.id
    timestamp = int(datetime.datetime.utcnow().timestamp())
    hash = get_hash(context.bot.token, f"{timestamp}{user_id}")

    url = (
        f"{base_url}/admin/"
        f"?user_id={user_id}"
        f"&auth_time={timestamp}"
        f"&hash={hash}"
    )
    keyboard = [
        [InlineKeyboardButton("Открыть админку", url=url)]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Меню администратора сделано в виде веб-приложения. ",
        reply_markup=markup
    )


text = [
    "Открыть меню администратора"
]
open_admin_menu_handler = MessageHandler(filters.Text(text) & filters.ChatType.PRIVATE, open_admin_menu)