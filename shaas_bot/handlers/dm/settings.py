from telegram import Update, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, LoginUrl
from telegram.ext import CallbackContext, CommandHandler, filters, CallbackQueryHandler

from shaas_common.model import Chat
from shaas_common.storage import Storage


def _user_bool(data: bool):
    if data:
        return "✅"
    return "❌"


def _get_setting_msg(user: Chat):
    msg = "Настройки:"

    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"Личные сообщения: {_user_bool(user.send_direct_messages)}",
                callback_data=f"settings_dm"
            )
        ]
    ])

    return msg, markup


async def settings(update: Update, context: CallbackContext):
    s = Storage()

    async with s:
        user = await s.chat.get(update.message.from_user.id)

    msg, markup = _get_setting_msg(user)
    await update.message.reply_text(msg, reply_markup=markup)


async def settings_dm(update: Update, context: CallbackContext):
    s = Storage()

    async with s:
        user: Chat = await s.chat.get(update.callback_query.from_user.id)
        user.send_direct_messages = not user.send_direct_messages

    msg, markup = _get_setting_msg(user)
    await update.callback_query.message.edit_reply_markup(reply_markup=markup)


settings_handlers = [
    CommandHandler("settings", settings, filters.ChatType.PRIVATE),
    CallbackQueryHandler(settings_dm, pattern="settings_dm")
]