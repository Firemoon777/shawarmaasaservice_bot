from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, filters

from shaas_common.storage import Storage


async def register(update: Update, context: CallbackContext):
    s = Storage()
    try:
        await s.chat.create(chat_id=update.message.chat_id)
        await s.commit()
    except Exception:
        pass

register_handler = MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, register)
