from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, filters

from shaas_bot.utils import is_group_chat, is_sender_admin
from shaas_common.storage import Storage


async def stop(update: Update, context: CallbackContext):
    await is_group_chat(update, context, raises=True)
    await is_sender_admin(update, context, raises=True)

    s = Storage()
    await s.event.stop_event(update.message.chat_id)
    await s.commit()

    await update.message.reply_text("Сделано")


stop_handler = CommandHandler("stop", stop, filters.ChatType.GROUPS)