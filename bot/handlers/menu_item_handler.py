from sqlalchemy import select, cast, BigInteger
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters, ConversationHandler, \
    CallbackQueryHandler

from bot.utils import is_group_chat, is_sender_admin, cancel_handler
from common.exception import NoMenuInGroupError
from common.model import Menu, MenuItem
from common.session import get_db, SessionLocal

MENU_WAIT_CALLBACK = 1
MENU_WAIT_ITEM = 3


async def menu_item_add(update: Update, context: CallbackContext):
    await is_group_chat(update, context, raises=True)
    await is_sender_admin(update, context, raises=True)

    try:
        del context.user_data["menu_id"]
    except KeyError:
        pass

    session = SessionLocal()
    menu = await Menu.chat_menu(session, update.message.chat_id)

    if len(menu) == 0:
        raise NoMenuInGroupError()

    if len(menu) == 1:
        context.user_data["menu_id"] = menu[0].id
        return await menu_item_wait(update, context)

    keyboard = [
        [
            InlineKeyboardButton(
                row.name,
                callback_data=f"menu_item_callback_{update.message.from_user.id}_{row.id}"
            )
        ] for row in menu
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Какое меню хотите удалить?",
        reply_markup=markup
    )

    return MENU_WAIT_CALLBACK


async def menu_wait_callback(update: Update, context: CallbackContext):
    user_id, menu_id = update.callback_query.data.replace("menu_item_callback_", "").split("_", 1)
    user_id = int(user_id)
    menu_id = int(menu_id)
    if user_id != update.callback_query.from_user.id:
        await update.callback_query.answer("Не-а")
        return

    await update.callback_query.answer()
    await update.callback_query.message.edit_reply_markup()

    context.user_data["menu_id"] = menu_id

    return await menu_item_wait(update, context)


async def menu_item_wait(update: Update, context: CallbackContext):
    if update.message:
        message = update.message
    else:
        message = update.callback_query.message

    await message.reply_text(
        "Введите позиции меню, которые нужно добавить в строгом соответствии с формой:\n"
        "\n"
        "Имя: название позиции (короче - лучше)\n"
        "Описание: тут можно не ограничивать себя, но лучше все же ограничивать\n"
        "Цена: число в рублях. В рублях и точка.\n"
        "Белки: число\n"
        "Жиры: число\n"
        "Углеводы: число\n"
        "ККал: число\n"
        "Опрос: 1, если добавить в общий опрос"
    )

    return MENU_WAIT_ITEM


async def menu_item_parse(update: Update, context: CallbackContext):
    session = SessionLocal()
    menu_id = context.user_data["menu_id"]
    
    t = {
        "Имя": "name",
        "Описание": "description",
        "Цена": "price",
        "Белки": "proteins",
        "Жиры": "fats",
        "Углеводы": "carbohydrates",
        "ККал": "calories",
        "Опрос": "poll_enable"
    }

    entries = update.message.text.split("\n\n")

    for entry in entries:
        item = MenuItem()
        item.menu_id = menu_id

        lines = entry.split("\n")
        data = dict()
        for line in lines:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            data[t[key]] = value

        item.name = data["name"]
        item.description = data["description"]
        item.price = int(data["price"])
        item.proteins = float(data["proteins"])
        item.fats = float(data["fats"])
        item.carbohydrates = float(data["carbohydrates"])
        item.calories = float(data["calories"])
        item.poll_enable = bool(data.get("poll_enable", False))

        session.add(item)

    await session.commit()

    await update.message.reply_text(
        "Успеешно добавлено!"
    )
    return ConversationHandler.END

menu_item_add_handler = ConversationHandler(
    entry_points=[CommandHandler("menu_item_add", menu_item_add)],
    states={
        MENU_WAIT_CALLBACK: [CallbackQueryHandler(menu_wait_callback, pattern="menu_item_callback_")],
        MENU_WAIT_ITEM: [MessageHandler(filters.TEXT, menu_item_parse)],
    },
    fallbacks=[cancel_handler]
)