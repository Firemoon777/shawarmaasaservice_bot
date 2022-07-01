from telegram import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Update
from telegram.ext import CommandHandler, CallbackContext

from common.model import Chat
from common.session import get_db, SessionLocal


async def test1(update: Update, context: CallbackContext):
    session = SessionLocal()
    print(session)

    chat = Chat()
    chat.chat_id = update.message.chat_id
    session.add(chat)
    await session.commit()

    await update.message.reply_text("test1")



async def test2(update: Update, context: CallbackContext):
    web_app = WebAppInfo("https://bot.f1remoon.com/")
    keyboard = [
        [InlineKeyboardButton("Open", web_app=web_app)]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("test2", reply_markup=markup)


test1_handler = CommandHandler("test1", test1)
test2_handler = CommandHandler("test2", test2)

all_handlers = [
    test1_handler,
    test2_handler
]