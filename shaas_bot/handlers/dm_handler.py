from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler


async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_hash = ""
    menu_id, chat_id = update.message.text[7:].split("_")

    web_app = WebAppInfo(
        f"https://bot.f1remoon.com/shaas/{menu_id}"
        f"?user_id={user_id}"
        f"&user_hash={user_hash}"
        f"&chat_id={chat_id}"
    )
    keyboard = [
        [InlineKeyboardButton("Открыть меню", web_app=web_app)]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Расширенное меню доступно по кнопке под сообщением.\n"
        "\n"
        "При первом открытии вас предупредят, что приложение может получмть доступ к вашему IP-адресу. "
        "Но вы же всё равно из офиса, у вас одинаковый и уже давно известный адрес...",
        reply_markup=markup
    )


start_handler = CommandHandler("start", start)