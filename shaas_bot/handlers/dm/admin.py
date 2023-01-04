import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, MessageHandler, filters, CommandHandler

from shaas_common.action.admin import get_controlled_chats


async def open_admin_menu(update: Update, context: CallbackContext):
    base_url = context.bot_data["base_url"]
    chats = await get_controlled_chats(context.bot, update.message.from_user.id)
    keyboard = [
        [InlineKeyboardButton(f"{chat.name}", url=f"{base_url}/admin/{chat.id}")] for chat in chats
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Меню какого чата необходимо открыть?",
        reply_markup=markup
    )


open_admin_menu_handler = CommandHandler("admin", open_admin_menu)
