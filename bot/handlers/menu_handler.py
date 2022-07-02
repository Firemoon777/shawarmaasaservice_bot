from sqlalchemy import select, cast, BigInteger
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters, ConversationHandler, \
    CallbackQueryHandler

from bot.utils import is_group_chat, is_sender_admin, cancel_handler
from common.model import Menu, MenuItem
from common.session import get_db, SessionLocal

MENU_PARSE_NAME = 1


async def menu_add(update: Update, context: CallbackContext):
    await is_group_chat(update, context, raises=True)
    await is_sender_admin(update, context, raises=True)

    await update.message.reply_text(
        "Введите название для меню"
    )

    return MENU_PARSE_NAME


async def menu_parse_name(update: Update, context: CallbackContext):
    session = SessionLocal()

    name = update.message.text.strip()

    menu = Menu()
    menu.chat_id = update.message.chat_id
    menu.name = name

    session.add(menu)
    await session.commit()

    await update.message.reply_text(
        "Меню добавлено."
    )
    return ConversationHandler.END

menu_add_handler = ConversationHandler(
    entry_points=[CommandHandler("menu_add", menu_add)],
    states={
        MENU_PARSE_NAME: [MessageHandler(filters.TEXT, menu_parse_name)],
    },
    fallbacks=[cancel_handler]
)


async def menu_list(update: Update, context: CallbackContext):
    session = SessionLocal()

    menu = await Menu.chat_menu(session, update.message.chat_id)

    menu_str = [f"- {row.name}" for row in menu]
    if len(menu_str):
        await update.message.reply_text(
            text="Меню в данном чате:\n" + "\n".join(menu_str),
        )
    else:
        await update.message.reply_text(
            text="В данном чате ещё нет меню!"
        )


menu_list_handler = CommandHandler("menu_list", menu_list)


async def menu_remove(update: Update, context: CallbackContext):
    await is_group_chat(update, context, raises=True)
    await is_sender_admin(update, context, raises=True)

    session = SessionLocal()

    menu = await Menu.chat_menu(session, update.message.chat_id)

    keyboard = [
        [InlineKeyboardButton(row.name, callback_data=f"menu-remove-{row.id}")] for row in menu
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Какое меню хотите удалить?",
        reply_markup=markup
    )


async def menu_remove_callback(update: Update, context: CallbackContext):
    session = SessionLocal()

    await update.callback_query.answer()
    await update.callback_query.message.edit_reply_markup(reply_markup=None)

    menu_id = int(update.callback_query.data.replace("menu-remove-", ""))
    menu = await Menu.get(session, menu_id)

    if menu is not None:
        await session.delete(menu)
        await session.commit()
        await update.callback_query.message.reply_text(f"Удалено меню \"{menu.name}\"")


menu_remove_handler = CommandHandler("menu_remove", menu_remove)
menu_remove_callback_handler = CallbackQueryHandler(menu_remove_callback, pattern="menu-remove-")