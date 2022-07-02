import json

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters

from common.model import Menu, MenuItem
from common.session import get_db, SessionLocal


async def test1(update: Update, context: CallbackContext):
    session = SessionLocal()

    menu = Menu()
    menu.name = "Шавадэй"
    menu.chat_id = update.message.chat_id

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

    menu.append(menu)

    session.add(menu)
    await session.commit()
    await update.message.reply_text("test1")


async def test2(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_hash = "123"

    if user_id != update.message.chat_id:
        keyboard = [
            [InlineKeyboardButton("В личку боту", url="https://t.me/shawarmaasaservice_stg_bot?start=test")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("В группе показ меню недоступен. Жми на кнопку, а затем на старт", reply_markup=markup)
    else:
        web_app = WebAppInfo(f"https://bot.f1remoon.com/shaas/1?user_id={user_id}&user_hash={user_hash}")
        keyboard = [
            [InlineKeyboardButton("Открыть меню", web_app=web_app)]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Налетай", reply_markup=markup)


async def web_app_data(update: Update, context: CallbackContext):
    print(update.effective_message.web_app_data.data)
    data = json.loads(update.effective_message.web_app_data.data)
    await context.bot.send_message(
        chat_id=update.effective_message.chat_id,
        text=str(data)
    )
    

test1_handler = CommandHandler("test1", test1)
test2_handler = CommandHandler("test2", test2)
web_app_handler = MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data)