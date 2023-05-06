from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, filters

from shaas_web.model.storage import Storage


async def register(update: Update, context: CallbackContext):
    if not update.message:
        return

    s = Storage()
    async with s:
        chat = await s.chat.get(update.message.chat_id)
        if not chat:
            await s.chat.create(
                id=update.message.chat_id,
                name=update.message.chat.title,
                # username=""
            )
            await s.commit()

register_handler = MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, register)
