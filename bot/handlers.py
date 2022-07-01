from telegram import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Update
from telegram.ext import CommandHandler, CallbackContext

from common.model import Chat, Menu, MenuItem
from common.session import get_db, SessionLocal


async def test1(update: Update, context: CallbackContext):
    session = SessionLocal()
    print(session)

    chat = Chat()
    chat.chat_id = update.message.chat_id
    session.add(chat)

    menu = Menu()
    menu.name = "Шавадэй"

    from common.data import items
    for item_data in items:
        item = MenuItem()
        item.name = item_data["name"]
        item.price = item_data["price"]
        item.fats = item_data["fats"]
        item.carbohydrates = item_data["carbohydrates"]
        item.calories = item_data["calories"]
        item.proteins = item_data["proteins"]
        item.description = item_data["description"]

        menu.items.append(item)

    chat.menu.append(menu)

    await session.commit()
    await update.message.reply_text("test1")


async def test2(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_hash = ""
    web_app = WebAppInfo(f"https://bot.f1remoon.com/shaas/1?user_id={user_id}&user_hash={user_hash}")
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