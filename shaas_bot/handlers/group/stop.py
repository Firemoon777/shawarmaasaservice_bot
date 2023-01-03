from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, filters, MessageHandler

from shaas_bot.utils import is_group_chat, is_sender_admin
from shaas_common.model import Event
from shaas_common.storage import Storage


async def execute_silent(f):
    try:
        await f
    except BadRequest:
        pass


async def stop(update: Update, context: CallbackContext):
    await is_group_chat(update, context, raises=True)
    await is_sender_admin(update, context, raises=True)

    chat_id = update.message.chat_id

    s = Storage()
    async with s:
        event: Event = await s.event.get_current(chat_id)

        if not event:
            await update.message.reply_text("Нечего заканчивать")
            return

        temp_msg = await update.message.reply_text("Завершаем...")

        actions = [
            context.bot.unpin_chat_message(chat_id=chat_id, message_id=event.order_message_id),
            context.bot.unpin_chat_message(chat_id=chat_id, message_id=event.collect_message_id),
            context.bot.delete_message(chat_id=chat_id, message_id=event.additional_message_id),
            context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=event.collect_message_id or event.order_message_id),
            context.bot.edit_message_reply_markup(chat_id=event.owner_id, message_id=event.admin_message_id or 0)
        ]

        for action in actions:
            await execute_silent(action)

        await s.event.stop_event(update.message.chat_id)

        await temp_msg.edit_text("Сделано!")


stop_handler = MessageHandler(filters.Text(["Харэ"]) & filters.ChatType.GROUPS, stop)